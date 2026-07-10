"""
process_photos.py - Crop/resize/enhance photos and build flyers.

Modes (from the `enhance` column or the filename suffix):
  none / blank  -> light polish only: crop to platform aspect + auto brightness/contrast
  text_overlay  -> premium HTML/CSS flyer over the photo (see flyer_render.py)
  logo          -> photo + logo watermark in a corner
  both          -> flyer + logo
  premade_art   -> finished graphic: NO editing, only resize to fit platform dims
                   (any filename ending in _art is auto-treated as premade_art)

text_overlay/both delegate to flyer_render.py (HTML/CSS rendered via Playwright) for real
design quality -- see the premium-photo-forward-design skill for why. Everything else here
stays plain PIL, which is already correctly simple for those modes.
"""

from __future__ import annotations

import os

from PIL import Image, ImageEnhance, ImageOps

import config
import flyer_render


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


def process(input_path, out_path, platform_key, enhance_col,
            event="", key_details="", day_of_week="", date_str="",
            deal_photo_path=None):
    """Process one image for one platform and save it to out_path.

    text_overlay/both delegate entirely to flyer_render.render_flyer(), which
    saves directly to out_path; "both" then reopens that file to stamp the
    logo on top. Every other mode stays plain PIL.

    Returns out_path on success. Never raises on cosmetic issues -- worst case it
    still writes a correctly-sized image so a post is never blocked.
    """
    size = config.DIMENSIONS[platform_key]
    mode = resolve_mode(input_path, enhance_col)
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    if mode in ("text_overlay", "both"):
        flyer_render.render_flyer(input_path, event, key_details, day_of_week, date_str,
                                  out_path, size=size, deal_photo_path=deal_photo_path)
        if mode == "both":
            logoed = _add_logo(Image.open(out_path).convert("RGB"))
            logoed.save(out_path, quality=92)
        return out_path

    img = Image.open(input_path)
    if mode == "premade_art":
        # Post exactly as supplied -- only fit to platform dims, no other edits.
        result = _fit_contain(img.convert("RGB"), size)
    elif mode == "none":
        result = _fit_cover(_auto_polish(img), size)
    elif mode == "logo":
        result = _add_logo(_fit_cover(_auto_polish(img), size))
    else:
        result = _fit_cover(_auto_polish(img), size)

    result.save(out_path, quality=92)
    return out_path


def output_name(platform_short, event, date_str, ext=".png"):
    """backyard-brew-[platform]-[type]-[YYYY-MM-DD].ext"""
    slug = "".join(ch if ch.isalnum() else "-" for ch in event.lower()).strip("-")
    slug = "-".join(filter(None, slug.split("-")))
    return f"backyard-brew-{platform_short}-{slug}-{date_str}{ext}"
