"""
flyer_render.py - Premium HTML/CSS flyer rendering via Playwright.

Replaces the old PIL-drawn badge/minimal/poster templates in process_photos.py.
See the premium-photo-forward-design skill (~/.claude/skills/premium-photo-forward-design)
for the full design rationale. Two layout archetypes ("full_bleed", "editorial_split")
are chosen deterministically per (event, date). Each layout lays its content out with
CSS flexbox (not fixed absolute-pixel offsets), and the optional deal-photo inset is a
normal-flow child of that same flex column -- so it can never silently collide with the
headline/detail text the way the old PIL system's independently-positioned deal badge
once did. The browser's layout engine handles the spacing, not hand-computed coordinates.
"""

from __future__ import annotations

import hashlib
import html
import os
import tempfile
from pathlib import Path

from PIL import Image, ImageOps
from playwright.sync_api import sync_playwright

import config

LAYOUTS = ["full_bleed", "editorial_split"]


def _rgba(hex_color: str, alpha: float) -> str:
    """Convert a '#RRGGBB' hex string + alpha (0-1) into a CSS rgba() string,
    so gradient/overlay colors stay derived from config.COLORS instead of
    being hand-computed and risking silent drift if the brand palette changes."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


def choose_layout(event: str, date_str: str) -> str:
    """Deterministic layout rotation: the same (event, date) always picks the
    same layout on re-runs, but different dates/events vary."""
    seed = int(hashlib.md5(f"{event}{date_str}".encode()).hexdigest(), 16)
    return LAYOUTS[seed % len(LAYOUTS)]


def prep_photo(src_path: str, out_path: str, size=(1080, 1080), centering=(0.5, 0.4)) -> str:
    """Orientation-correct (EXIF) and crop-to-cover a real photo before
    referencing it from the HTML template -- CSS background-image ignores
    EXIF rotation, so skipping this renders sideways photos."""
    img = ImageOps.exif_transpose(Image.open(src_path))
    img = ImageOps.fit(img, size, method=Image.LANCZOS, centering=centering)
    img.convert("RGB").save(out_path, quality=92)
    return out_path


def _file_uri(path: str) -> str:
    return Path(path).resolve().as_uri()


def _deal_row_html(deal_photo_uri, key_details) -> str:
    if not deal_photo_uri:
        return ""
    detail = html.escape(key_details.split(",")[0].strip()) if key_details else ""
    caption_detail = f"<b>{detail}</b>" if detail else ""
    return f"""
  <div class="deal-row">
    <img class="deal-thumb" src="{deal_photo_uri}">
    <div class="deal-caption">Today's Deal{caption_detail}</div>
  </div>"""


def _deal_css(deal_photo_uri, thumb_size, caption_font_size, detail_font_size, gap, margin_bottom) -> str:
    """Only emit the .deal-row/.deal-thumb/.deal-caption stylesheet rules when
    a deal photo is actually being rendered -- otherwise even a deal-less
    flyer's HTML would contain the literal string "deal-row" via its <style>
    block, which defeats callers (and tests) that check for the row's
    presence/absence in the rendered output as a whole."""
    if not deal_photo_uri:
        return ""
    c = config.COLORS
    return (
        ".deal-row{display:flex;align-items:center;gap:" + str(gap) + "px;"
        "margin-bottom:" + str(margin_bottom) + "px;}"
        ".deal-thumb{width:" + str(thumb_size) + "px;height:" + str(thumb_size) + "px;"
        "border-radius:10px;object-fit:cover;border:3px solid " + c['gold'] + ";flex-shrink:0;}"
        ".deal-caption{color:" + c['gold'] + ";font-weight:700;font-size:" + str(caption_font_size) + "px;"
        "letter-spacing:2px;text-transform:uppercase;line-height:1.5;}"
        ".deal-caption b{color:" + c['cream'] + ";display:block;font-size:" + str(detail_font_size) + "px;"
        "letter-spacing:0.5px;text-transform:none;font-weight:700;}"
    )


def _full_bleed_html(photo_uri, event, key_details, day_of_week, deal_photo_uri=None) -> str:
    c = config.COLORS
    event_esc = html.escape(event.upper())
    day_esc = html.escape(day_of_week.upper())
    detail_esc = html.escape(key_details.split(",")[0].strip()) if key_details else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Barlow+Condensed:wght@500;600;700&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{width:1080px;height:1080px;}}
.canvas{{width:1080px;height:1080px;position:relative;overflow:hidden;background:{c['navy']};font-family:'Barlow Condensed',sans-serif;}}
.photo{{position:absolute;inset:0;background-image:url('{photo_uri}');background-size:cover;background-position:center;filter:contrast(1.08) saturate(1.12) brightness(0.98);}}
.grade{{position:absolute;inset:0;background:linear-gradient(160deg, {_rgba(c['navy'], 0.28)} 0%, {_rgba(c['navy'], 0)} 40%, {_rgba(c['gold'], 0.10)} 100%);mix-blend-mode:overlay;}}
.grain{{position:absolute;inset:0;opacity:0.06;mix-blend-mode:overlay;pointer-events:none;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");}}
.scrim{{position:absolute;left:0;right:0;bottom:0;height:60%;
  background:linear-gradient(to top, {_rgba(c['navy'], 0.97)} 0%, {_rgba(c['navy'], 0.88)} 30%, {_rgba(c['navy'], 0.4)} 68%, {_rgba(c['navy'], 0)} 100%);}}
.eyebrow{{position:absolute;top:56px;left:56px;display:flex;align-items:center;gap:12px;}}
.eyebrow .dot{{width:7px;height:7px;border-radius:50%;background:{c['yellow']};}}
.eyebrow span{{color:{c['yellow']};font-weight:700;font-size:22px;letter-spacing:6px;text-transform:uppercase;text-shadow:0 2px 8px rgba(0,0,0,0.5);}}
.content{{position:absolute;left:56px;right:56px;bottom:64px;display:flex;flex-direction:column;}}
{_deal_css(deal_photo_uri, thumb_size=84, caption_font_size=15, detail_font_size=19, gap=14, margin_bottom=20)}
.headline{{font-family:'Anton';color:{c['cream']};font-size:108px;line-height:0.88;letter-spacing:1px;text-transform:uppercase;
  text-shadow:0 4px 24px rgba(0,0,0,0.55);}}
.rule{{width:64px;height:4px;background:{c['gold']};margin-top:24px;margin-bottom:18px;}}
.detail{{color:{c['gold']};font-weight:600;font-size:28px;letter-spacing:1px;line-height:1.4;}}
.footer{{position:absolute;bottom:56px;right:56px;text-align:right;}}
.footer .mark{{color:{c['cream']};font-weight:700;font-size:18px;letter-spacing:5px;text-transform:uppercase;opacity:0.9;}}
.footer .tag{{color:{_rgba(c['cream'], 0.55)};font-weight:500;font-size:13px;letter-spacing:3px;text-transform:uppercase;margin-top:4px;}}
</style></head>
<body>
<div class="canvas">
  <div class="photo"></div>
  <div class="grade"></div>
  <div class="scrim"></div>
  <div class="grain"></div>
  <div class="eyebrow"><div class="dot"></div><span>{day_esc}</span></div>
  <div class="content">{_deal_row_html(deal_photo_uri, key_details)}
    <div class="headline">{event_esc}</div>
    <div class="rule"></div>
    <div class="detail">{detail_esc}</div>
  </div>
  <div class="footer">
    <div class="mark">Backyard Brew</div>
    <div class="tag">Craft Brews &amp; Things To Do</div>
  </div>
</div>
</body></html>"""


def _editorial_split_html(photo_uri, event, key_details, day_of_week, deal_photo_uri=None) -> str:
    c = config.COLORS
    event_esc = html.escape(event.upper())
    day_esc = html.escape(day_of_week.upper())
    detail_esc = html.escape(key_details.split(",")[0].strip()) if key_details else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Barlow+Condensed:wght@500;600;700&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{width:1080px;height:1080px;}}
.canvas{{width:1080px;height:1080px;position:relative;overflow:hidden;background:{c['navy']};font-family:'Barlow Condensed',sans-serif;}}
.photo{{position:absolute;top:0;bottom:0;right:0;width:66%;background-image:url('{photo_uri}');background-size:cover;background-position:65% center;filter:contrast(1.06) saturate(1.1);}}
.photo-fade{{position:absolute;top:0;bottom:0;right:0;width:66%;background:linear-gradient(90deg, {_rgba(c['navy'], 0.9)} 0%, {_rgba(c['navy'], 0)} 12%);}}
.grain{{position:absolute;inset:0;opacity:0.05;mix-blend-mode:overlay;pointer-events:none;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");}}
.panel{{position:absolute;top:0;bottom:0;left:0;width:38%;padding:64px 0 56px 56px;display:flex;flex-direction:column;justify-content:flex-end;}}
{_deal_css(deal_photo_uri, thumb_size=72, caption_font_size=13, detail_font_size=17, gap=12, margin_bottom=24)}
.eyebrow{{display:flex;align-items:center;gap:12px;margin-bottom:24px;}}
.eyebrow .bar{{width:36px;height:3px;background:{c['gold']};}}
.eyebrow span{{color:{c['gold']};font-weight:700;font-size:19px;letter-spacing:5px;text-transform:uppercase;}}
.headline{{font-family:'Anton';color:{c['cream']};font-size:86px;line-height:0.9;letter-spacing:1px;text-transform:uppercase;}}
.detail{{margin-top:26px;color:{c['cream']};font-weight:500;font-size:23px;line-height:1.5;opacity:0.92;max-width:290px;}}
.footer{{margin-top:32px;}}
.footer .mark{{color:{_rgba(c['cream'], 0.55)};font-weight:600;font-size:13px;letter-spacing:4px;text-transform:uppercase;}}
</style></head>
<body>
<div class="canvas">
  <div class="photo"></div>
  <div class="photo-fade"></div>
  <div class="grain"></div>
  <div class="panel">{_deal_row_html(deal_photo_uri, key_details)}
    <div class="eyebrow"><div class="bar"></div><span>{day_esc}</span></div>
    <div class="headline">{event_esc}</div>
    <div class="detail">{detail_esc}</div>
    <div class="footer"><div class="mark">Backyard Brew</div></div>
  </div>
</div>
</body></html>"""


_LAYOUT_BUILDERS = {"full_bleed": _full_bleed_html, "editorial_split": _editorial_split_html}


def render_flyer(photo_path, event, key_details, day_of_week, date_str, out_path,
                 size=(1080, 1080), deal_photo_path=None, layout=None) -> str:
    """Render one flyer: prep the photo(s), pick a layout (or use the given
    override -- mainly for tests), build the HTML, screenshot it via
    Playwright, save to out_path. Returns out_path.

    Note: `size` only drives photo-prep dimensions and the Playwright viewport --
    both HTML layout templates hardcode .canvas to 1080x1080, so passing a
    non-square size (e.g. an ig_story 1080x1920) will NOT produce a taller
    canvas; it will just add blank space around a still-1080x1080 layout."""
    with tempfile.TemporaryDirectory() as tmp:
        prepped_photo = os.path.join(tmp, "photo.jpg")
        prep_photo(photo_path, prepped_photo, size=size)
        photo_uri = _file_uri(prepped_photo)

        deal_photo_uri = None
        if deal_photo_path:
            prepped_deal = os.path.join(tmp, "deal.jpg")
            prep_photo(deal_photo_path, prepped_deal, size=(400, 400))
            deal_photo_uri = _file_uri(prepped_deal)

        chosen_layout = layout or choose_layout(event, date_str or day_of_week)
        html_str = _LAYOUT_BUILDERS[chosen_layout](
            photo_uri, event, key_details, day_of_week, deal_photo_uri)
        html_path = os.path.join(tmp, "flyer.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_str)

        out_dir = os.path.dirname(out_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": size[0], "height": size[1]})
            page.goto(_file_uri(html_path))
            # page.goto()'s default waitUntil="load" does not reliably wait for
            # @import'd web fonts (Anton, Barlow Condensed) to finish downloading
            # and applying -- without this, the screenshot can race the font load
            # and silently fall back to a system serif/sans font.
            page.wait_for_load_state("networkidle")
            page.evaluate("document.fonts.ready")
            page.screenshot(path=out_path)
            browser.close()

    return out_path
