"""
build_preview.py - Generates preview/this-week.html, a static visual
snapshot of the week's generated posts so the owner can scan everything at a
glance before manually scheduling them. Read-only convenience view --
posts.csv stays the actual source of truth the owner edits.
"""

from __future__ import annotations

import html
import os

import config

PREVIEW_DIR = os.path.join(config.REPO_ROOT, "preview")
PREVIEW_FILE = os.path.join(PREVIEW_DIR, "this-week.html")

CSS = """
body { font-family: Arial, sans-serif; background: #0B1C2D; color: #F5EFD8; margin: 0; padding: 24px; }
h1 { color: #C8922A; }
.card { background: #14273b; border: 2px solid #C8922A; border-radius: 12px;
        padding: 16px; margin-bottom: 20px; display: flex; gap: 20px; align-items: flex-start; }
.photos { display: flex; flex-direction: column; gap: 8px; }
.card img { width: 260px; height: 260px; object-fit: cover; border-radius: 8px; }
.placeholder { width: 260px; height: 260px; background: #1c3450; border-radius: 8px; }
.extra-photos { display: flex; gap: 8px; }
.extra-photos img { width: 120px; height: 120px; }
.meta { font-size: 14px; color: #F5C842; margin-bottom: 8px; }
.caption-label { font-weight: bold; color: #C8922A; margin-top: 10px; }
.caption-text { white-space: pre-wrap; }
"""


def _card_html(row: dict) -> str:
    img_rel = (row.get("generated_image") or "").replace("\\", "/")
    img_tag = (f'<img src="../{html.escape(img_rel)}" alt="post image">'
               if img_rel else '<div class="placeholder"></div>')
    extra_photos = [p.strip() for p in (row.get("photos") or "").split(",")[1:] if p.strip()]
    extra_html = ""
    if extra_photos:
        imgs = "".join(f'<img src="../photos/{html.escape(p)}" alt="additional photo">'
                       for p in extra_photos)
        extra_html = f'<div class="extra-photos">{imgs}</div>'
    return f"""
<div class="card">
  <div class="photos">
    {img_tag}
    {extra_html}
  </div>
  <div>
    <div class="meta">{html.escape(row.get('scheduled_time', ''))} &mdash;
        {html.escape(row.get('event', ''))} ({html.escape(row.get('post_type', ''))})</div>
    <div class="caption-label">Facebook</div>
    <div class="caption-text">{html.escape(row.get('fb_caption', ''))}</div>
    <div class="caption-label">Instagram</div>
    <div class="caption-text">{html.escape(row.get('ig_caption', ''))}</div>
  </div>
</div>"""


def build_preview(rows: list) -> str:
    """Return the full HTML document for these rows, sorted by scheduled_time."""
    ordered = sorted(rows, key=lambda r: r.get("scheduled_time", ""))
    cards = "\n".join(_card_html(r) for r in ordered)
    return f"""<!doctype html>
<html>
<head><meta charset="utf-8"><title>Backyard Brew - This Week's Posts</title>
<style>{CSS}</style></head>
<body>
<h1>This Week's Posts</h1>
{cards}
</body>
</html>"""


def write_preview(rows: list) -> str:
    """Write preview/this-week.html for the given rows. Never raises -- a
    preview-generation failure must never block the Sunday job itself."""
    try:
        os.makedirs(PREVIEW_DIR, exist_ok=True)
        with open(PREVIEW_FILE, "w", encoding="utf-8") as f:
            f.write(build_preview(rows))
        return PREVIEW_FILE
    except Exception as exc:
        print(f"[build_preview] could not write preview page: {exc}")
        return ""
