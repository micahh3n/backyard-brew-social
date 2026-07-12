"""
classify_photos.py - Filename-convention helpers for photo handling.

No vision API here -- Claude Code looks at any un-suffixed photo directly
during the Sunday session and decides its kind by eye. This module only
covers the deterministic filename rules: an explicit _vibe/_spotlight
suffix, whether a filename is claimed by the event/food photo pool
(config.EVENT_PHOTO_KEYWORDS/FOOD_PHOTO_KEYWORDS), and EXIF capture time
for the pool's LRU ordering.
"""

from __future__ import annotations

import os
from datetime import datetime

from PIL import Image

import config

OVERRIDE_SUFFIXES = ("_teaser", "_art", "_vibe", "_spotlight")

# A photo tagged _vibe or _spotlight is the owner telling us its kind
# directly -- honor that as a free, deterministic result instead of
# guessing.
MANUAL_KIND_SUFFIXES = {"_vibe": "vibe", "_spotlight": "spotlight"}


def manual_kind(filename: str) -> str | None:
    """'vibe'/'spotlight' if the filename carries that override suffix, else None."""
    stem = os.path.splitext(filename)[0].lower()
    for suffix, kind in MANUAL_KIND_SUFFIXES.items():
        if stem.endswith(suffix) or f"{suffix}_" in stem:
            return kind
    return None


def pool_claimed(filename: str) -> bool:
    """True if this filename's stem contains a keyword from
    config.EVENT_PHOTO_KEYWORDS or config.FOOD_PHOTO_KEYWORDS -- these
    photos are handled by the event/food photo pool (generate_captions.py),
    not treated as a loose candid needing a manual look."""
    stem = os.path.splitext(filename)[0].lower()
    for keywords in config.EVENT_PHOTO_KEYWORDS.values():
        if any(kw.lower() in stem for kw in keywords):
            return True
    for keyword in config.FOOD_PHOTO_KEYWORDS:
        if keyword.lower() in stem:
            return True
    return False


# Never treated as a still-image candid -- iPhones drop these alongside
# photos in the same camera roll export.
VIDEO_EXTENSIONS = (".mp4", ".mov", ".m4v", ".avi")


def needs_classification(filename: str) -> bool:
    """False if the filename already carries an explicit override signal,
    or isn't a still-image file at all (see VIDEO_EXTENSIONS)."""
    if filename.lower().endswith(VIDEO_EXTENSIONS):
        return False
    stem = os.path.splitext(filename)[0].lower()
    return not any(stem.endswith(s) or f"{s}_" in stem for s in OVERRIDE_SUFFIXES) \
        and "_art" not in stem and "art" not in stem.split("_")


def read_capture_time(path: str):
    """EXIF DateTimeOriginal if present, else the file's mtime. None on error."""
    try:
        img = Image.open(path)
        exif = img.getexif()
        raw = exif.get(36867) or exif.get(306)  # DateTimeOriginal, DateTime
        if raw:
            return datetime.strptime(raw, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    try:
        return datetime.fromtimestamp(os.path.getmtime(path))
    except Exception:
        return None
