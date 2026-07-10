"""
process_photos.py - Crop/resize/enhance photos and build flyers.

Modes (from the `enhance` column or the filename suffix):
  none / blank  -> light polish only: crop to platform aspect + auto brightness/contrast
  text_overlay  -> retro-badge flyer with event info over the photo
  logo          -> photo + logo watermark in a corner
  both          -> flyer + logo
  premade_art   -> finished graphic: NO editing, only resize to fit platform dims
                   (any filename ending in _art is auto-treated as premade_art)

Fonts that fit the brand are auto-downloaded into assets/fonts/ on first run.
Everything degrades gracefully: missing logo -> watermark skipped; font download
fails -> PIL's default font is used so text still renders.
"""

from __future__ import annotations

import hashlib
import os
import urllib.request

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

import config

# ---------------------------------------------------------------------------
# Free, brand-fitting fonts (static TTFs from the Google Fonts repo, OFL).
# Headline = bold condensed varsity (Anton) or heavy slab (Alfa Slab One);
# body = Barlow Condensed; script accent = Pacifico.
# ---------------------------------------------------------------------------
FONT_FILES = {
    "Anton-Regular.ttf":
        "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf",
    "AlfaSlabOne-Regular.ttf":
        "https://github.com/google/fonts/raw/main/ofl/alfaslabone/AlfaSlabOne-Regular.ttf",
    "BarlowCondensed-Medium.ttf":
        "https://github.com/google/fonts/raw/main/ofl/barlowcondensed/BarlowCondensed-Medium.ttf",
    "BarlowCondensed-Bold.ttf":
        "https://github.com/google/fonts/raw/main/ofl/barlowcondensed/BarlowCondensed-Bold.ttf",
    "Pacifico-Regular.ttf":
        "https://github.com/google/fonts/raw/main/ofl/pacifico/Pacifico-Regular.ttf",
}

# Events whose flyers read better with a chunky slab (food/poster feel).
SLAB_EVENTS = {"Tacos + Poker Club", "Bingo Night"}


def ensure_fonts() -> None:
    """Download brand fonts into assets/fonts/ if they aren't there yet."""
    os.makedirs(config.FONTS_DIR, exist_ok=True)
    for name, url in FONT_FILES.items():
        dest = os.path.join(config.FONTS_DIR, name)
        if os.path.exists(dest):
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "backyard-brew-bot"})
            with urllib.request.urlopen(req, timeout=30) as r, open(dest, "wb") as f:
                f.write(r.read())
            print(f"[process_photos] downloaded font {name}")
        except Exception as exc:
            print(f"[process_photos] could not download {name}: {exc}")


def _font(name: str, size: int):
    """Load a font by filename, falling back to PIL's default if unavailable."""
    path = os.path.join(config.FONTS_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        try:
            return ImageFont.load_default(size)
        except Exception:
            return ImageFont.load_default()


def _headline_font(event: str, size: int):
    fname = "AlfaSlabOne-Regular.ttf" if event in SLAB_EVENTS else "Anton-Regular.ttf"
    return _font(fname, size)


# ---------------------------------------------------------------------------
# Filename / mode helpers
# ---------------------------------------------------------------------------
def resolve_mode(filename: str, enhance_col: str) -> str:
    """Decide the processing mode. A _art suffix always wins (premade_art)."""
    stem = os.path.splitext(os.path.basename(filename))[0].lower()
    if stem.endswith("_art") or stem.endswith("_teaser_art") or "_art" in stem.split("_")[-1:]:
        return "premade_art"
    # Robust check: any token equal to "art".
    if "art" in stem.split("_"):
        return "premade_art"
    mode = (enhance_col or "").strip().lower()
    if mode in {"none", ""}:
        return "none"
    if mode in {"text_overlay", "logo", "both", "premade_art"}:
        return mode
    return "none"


def _fit_cover(img: Image.Image, size) -> Image.Image:
    """Crop-to-cover: fill the target box exactly, cropping overflow (center)."""
    return ImageOps.fit(img, size, method=Image.LANCZOS, centering=(0.5, 0.5))


def _fit_contain(img: Image.Image, size) -> Image.Image:
    """Contain: scale to fit inside the box, pad with brand navy (no cropping)."""
    canvas = Image.new("RGB", size, config.COLORS["navy"])
    scaled = img.copy()
    scaled.thumbnail(size, Image.LANCZOS)
    x = (size[0] - scaled.width) // 2
    y = (size[1] - scaled.height) // 2
    canvas.paste(scaled, (x, y))
    return canvas


def _auto_polish(img: Image.Image) -> Image.Image:
    """Gentle, universal cleanup: mild autocontrast + tiny brightness/color lift."""
    img = ImageOps.exif_transpose(img)  # respect phone orientation
    img = ImageOps.autocontrast(img, cutoff=1)
    img = ImageEnhance.Brightness(img).enhance(1.03)
    img = ImageEnhance.Color(img).enhance(1.05)
    return img


def _load_logo():
    for name in ("logo.png", "logo_light.png"):
        p = os.path.join(config.LOGO_DIR, name)
        if os.path.exists(p):
            try:
                return Image.open(p).convert("RGBA")
            except Exception:
                pass
    return None


def _add_logo(img: Image.Image) -> Image.Image:
    logo = _load_logo()
    if logo is None:
        print("[process_photos] no logo found in assets/logo/, skipping watermark")
        return img
    target_w = int(img.width * 0.18)
    ratio = target_w / logo.width
    logo = logo.resize((target_w, int(logo.height * ratio)), Image.LANCZOS)
    margin = int(img.width * 0.04)
    pos = (img.width - logo.width - margin, img.height - logo.height - margin)
    base = img.convert("RGBA")
    base.alpha_composite(logo, pos)
    return base.convert("RGB")


def _wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _autosize_headline(draw, event, max_w, start_px, floor_px, step=6):
    """Shrink the headline font until "event" wraps to <=2 lines within
    max_w, or floor_px is reached. Returns (font, lines, size_px) so callers
    can position/draw the result."""
    size_px = start_px
    while size_px > floor_px:
        hf = _headline_font(event, size_px)
        lines = _wrap(draw, event.upper(), hf, max_w)
        if len(lines) <= 2:
            break
        size_px -= step
    hf = _headline_font(event, size_px)
    lines = _wrap(draw, event.upper(), hf, max_w)
    return hf, lines, size_px


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _build_flyer(photo: Image.Image, event, key_details, day_of_week, size) -> Image.Image:
    """Retro outdoor-badge flyer: photo, darkened, with a gold-bordered info panel."""
    navy, gold, cream, yellow = (_hex(config.COLORS[k])
                                 for k in ("navy", "gold", "cream", "yellow"))
    base = _fit_cover(photo, size).convert("RGB")
    # Darken so text is readable.
    base = ImageEnhance.Brightness(base).enhance(0.55)
    draw = ImageDraw.Draw(base)
    W, H = size
    inset = int(W * 0.05)

    # Outer badge border.
    draw.rectangle([inset, inset, W - inset, H - inset], outline=gold, width=max(4, W // 180))

    # Day tag (top).
    tag_font = _font("BarlowCondensed-Bold.ttf", int(H * 0.045))
    tag = day_of_week.upper()
    tw = draw.textlength(tag, font=tag_font)
    ty = int(H * 0.13)
    pad = int(W * 0.02)
    draw.rectangle([(W - tw) / 2 - pad, ty - pad, (W + tw) / 2 + pad, ty + tag_font.size + pad],
                   fill=gold)
    draw.text(((W - tw) / 2, ty), tag, font=tag_font, fill=navy)

    # Event headline (auto-shrink to fit two lines).
    max_w = W - 2 * inset - int(W * 0.06)
    hf, lines, size_px = _autosize_headline(draw, event, max_w, int(H * 0.12), int(H * 0.05))
    y = int(H * 0.30)
    for line in lines:
        lw = draw.textlength(line, font=hf)
        draw.text(((W - lw) / 2, y), line, font=hf, fill=cream)
        y += int(size_px * 1.05)

    # One-liner detail (first fact only, keeps it clean).
    detail = key_details.split(",")[0].strip()
    bf = _font("BarlowCondensed-Medium.ttf", int(H * 0.05))
    for line in _wrap(draw, detail, bf, max_w)[:2]:
        lw = draw.textlength(line, font=bf)
        draw.text(((W - lw) / 2, y + int(H * 0.02)), line, font=bf, fill=yellow)
        y += int(H * 0.06)

    # Script flourish footer.
    sf = _font("Pacifico-Regular.ttf", int(H * 0.045))
    foot = "Craft Brews & Things To Do"
    fw = draw.textlength(foot, font=sf)
    draw.text(((W - fw) / 2, H - inset - int(H * 0.09)), foot, font=sf, fill=gold)
    return base


FLYER_TEMPLATES = ["badge", "minimal", "poster"]


def choose_template(event: str, date_str: str) -> str:
    """Deterministic template rotation: the same (event, date) always picks
    the same template on re-runs, but different dates/events vary visually
    so consecutive weeks don't look identical."""
    seed = int(hashlib.md5(f"{event}{date_str}".encode()).hexdigest(), 16)
    return FLYER_TEMPLATES[seed % len(FLYER_TEMPLATES)]


def _build_flyer_minimal(photo: Image.Image, event, key_details, day_of_week, size) -> Image.Image:
    """Clean minimal layout: full photo, light polish, a solid caption bar
    across the bottom third instead of a bordered badge."""
    navy, cream, gold = (_hex(config.COLORS[k]) for k in ("navy", "cream", "gold"))
    base = _fit_cover(_auto_polish(photo), size).convert("RGBA")
    W, H = size
    bar_h = int(H * 0.28)
    bar = Image.new("RGBA", (W, bar_h), navy + (235,))
    base.alpha_composite(bar, (0, H - bar_h))
    draw = ImageDraw.Draw(base)

    max_w = W - int(W * 0.12)
    hf, lines, size_px = _autosize_headline(draw, event, max_w, int(H * 0.09), int(H * 0.045))
    y = H - bar_h + int(bar_h * 0.12)
    for line in lines:
        draw.text((int(W * 0.06), y), line, font=hf, fill=cream)
        y += int(size_px * 1.05)

    detail = key_details.split(",")[0].strip() if key_details else ""
    bf = _font("BarlowCondensed-Medium.ttf", int(H * 0.04))
    tag_font = _font("BarlowCondensed-Bold.ttf", int(H * 0.035))
    draw.text((int(W * 0.06), y + int(H * 0.01)), day_of_week.upper(), font=tag_font, fill=gold)
    if detail:
        for line in _wrap(draw, detail, bf, max_w)[:1]:
            draw.text((int(W * 0.06), y + int(H * 0.05)), line, font=bf, fill=gold)
    return base.convert("RGB")


def _build_flyer_poster(photo: Image.Image, event, key_details, day_of_week, size) -> Image.Image:
    """Bold poster layout: full-bleed darkened photo, giant headline banner
    across the top third -- a punchier alternative to the retro badge."""
    navy, gold, cream = (_hex(config.COLORS[k]) for k in ("navy", "gold", "cream"))
    base = _fit_cover(photo, size).convert("RGB")
    base = ImageEnhance.Brightness(base).enhance(0.7)
    base = base.convert("RGBA")
    W, H = size
    banner_h = int(H * 0.32)
    banner = Image.new("RGBA", (W, banner_h), gold + (255,))
    base.alpha_composite(banner, (0, 0))
    draw = ImageDraw.Draw(base)

    max_w = W - int(W * 0.1)
    hf, lines, size_px = _autosize_headline(draw, event, max_w, int(H * 0.11), int(H * 0.05))
    total_h = sum(int(size_px * 1.05) for _ in lines)
    y = (banner_h - total_h) // 2
    for line in lines:
        lw = draw.textlength(line, font=hf)
        draw.text(((W - lw) / 2, y), line, font=hf, fill=navy)
        y += int(size_px * 1.05)

    detail = key_details.split(",")[0].strip() if key_details else ""
    bf = _font("BarlowCondensed-Medium.ttf", int(H * 0.05))
    tag = f"{day_of_week.upper()} -- {detail}" if detail else day_of_week.upper()
    for line in _wrap(draw, tag, bf, max_w)[:2]:
        lw = draw.textlength(line, font=bf)
        draw.text(((W - lw) / 2, H - int(H * 0.12)), line, font=bf, fill=cream)
    return base.convert("RGB")


def _add_deal_callout(img: Image.Image, deal_photo_path: str, key_details: str) -> Image.Image:
    """Stamp a small real-photo badge (bottom-left, opposite the logo corner)
    advertising today's deal: a cropped thumbnail of deal_photo_path inside a
    gold-bordered square, with the deal's first detail as a caption
    underneath. Never raises -- a missing/corrupt deal photo just returns img
    unchanged so it never blocks the rest of the flyer."""
    try:
        deal_img = Image.open(deal_photo_path).convert("RGB")
    except Exception as exc:
        print(f"[process_photos] could not open deal photo {deal_photo_path}: {exc}")
        return img

    navy, gold, cream = (_hex(config.COLORS[k]) for k in ("navy", "gold", "cream"))
    base = img.convert("RGBA")
    W, H = base.size
    badge_size = int(W * 0.30)
    margin = int(W * 0.05)
    thumb = _fit_cover(deal_img, (badge_size, badge_size)).convert("RGBA")

    pos = (margin, H - badge_size - margin - int(H * 0.08))
    border = Image.new("RGBA", (badge_size + 10, badge_size + 10), gold + (255,))
    base.alpha_composite(border, (pos[0] - 5, pos[1] - 5))
    base.alpha_composite(thumb, pos)

    draw = ImageDraw.Draw(base)
    label_font = _font("BarlowCondensed-Bold.ttf", int(H * 0.032))
    label = "TODAY'S DEAL"
    detail = key_details.split(",")[0].strip() if key_details else ""
    lx, ly = pos[0], pos[1] + badge_size + 6
    pad = int(W * 0.015)
    draw.rectangle([lx - pad, ly - pad, lx + badge_size + pad, ly + label_font.size * 2 + pad * 3],
                   fill=navy + (200,))
    draw.text((lx, ly), label, font=label_font, fill=gold)
    if detail:
        for line in _wrap(draw, detail, label_font, badge_size)[:1]:
            draw.text((lx, ly + label_font.size + 4), line, font=label_font, fill=cream)
    return base.convert("RGB")


def process(input_path, out_path, platform_key, enhance_col,
            event="", key_details="", day_of_week="", date_str="",
            deal_photo_path=None):
    """Process one image for one platform and save it to out_path.

    Returns out_path on success. Never raises on cosmetic issues -- worst case it
    still writes a correctly-sized image so a post is never blocked by a font.
    """
    ensure_fonts()
    size = config.DIMENSIONS[platform_key]
    mode = resolve_mode(input_path, enhance_col)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    img = Image.open(input_path)
    builders = {"badge": _build_flyer, "minimal": _build_flyer_minimal,
                "poster": _build_flyer_poster}

    if mode == "premade_art":
        # Post exactly as supplied -- only fit to platform dims, no other edits.
        result = _fit_contain(img.convert("RGB"), size)
    elif mode == "none":
        result = _fit_cover(_auto_polish(img), size)
    elif mode == "text_overlay":
        builder = builders[choose_template(event, date_str or day_of_week)]
        result = builder(img, event, key_details, day_of_week, size)
    elif mode == "logo":
        result = _add_logo(_fit_cover(_auto_polish(img), size))
    elif mode == "both":
        builder = builders[choose_template(event, date_str or day_of_week)]
        result = _add_logo(builder(img, event, key_details, day_of_week, size))
    else:
        result = _fit_cover(_auto_polish(img), size)

    if deal_photo_path and mode in ("text_overlay", "both"):
        result = _add_deal_callout(result, deal_photo_path, key_details)

    result.save(out_path, quality=92)
    return out_path


def output_name(platform_short, event, date_str, ext=".png"):
    """backyard-brew-[platform]-[type]-[YYYY-MM-DD].ext"""
    slug = "".join(ch if ch.isalnum() else "-" for ch in event.lower()).strip("-")
    slug = "-".join(filter(None, slug.split("-")))
    return f"backyard-brew-{platform_short}-{slug}-{date_str}{ext}"
