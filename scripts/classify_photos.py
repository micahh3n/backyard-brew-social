"""
classify_photos.py - Vision + EXIF classification of un-suffixed photos.

For every photo in /photos/ that isn't already claimed by a filename suffix
(_teaser, _art, _vibe, _spotlight) or already used in posts.csv, ask Claude's
vision model what it's looking at: does it match a known recurring event,
read as a candid/atmosphere shot, or read as spotlight-worthy? A suffix on
the filename always wins over this guess -- this module only ever looks at
photos with no such signal.

Low-confidence photos are left alone entirely -- never forced into a post.
"""

from __future__ import annotations

import base64
import os
from datetime import datetime

from PIL import Image

import config
from anthropic_client import _extract_json

try:
    import anthropic
except ImportError:
    anthropic = None

OVERRIDE_SUFFIXES = ("_teaser", "_art", "_vibe", "_spotlight")


def needs_classification(filename: str) -> bool:
    """False if the filename already carries an explicit override signal."""
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


def _call_vision(path: str, known_events: list[str]) -> str:
    """Send the image to Claude, return the raw text response."""
    if anthropic is None or not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("anthropic not available or API key not set")
    with open(path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    media_type = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    prompt = (
        "You classify photos for a bar's social media system. Known recurring "
        f"events: {', '.join(known_events)}. Look at this photo and return ONLY "
        'JSON: {"match": "<one of the known events, or null>", '
        '"kind": "event" | "vibe" | "spotlight" | null, '
        '"confidence": "high" | "low"}. '
        '"vibe" = candid atmosphere/scenery with no clear event tie-in. '
        '"spotlight" = a review screenshot, or a posed victory/celebration moment '
        "worth a dedicated shoutout. Use \"low\" confidence whenever you are not "
        "reasonably sure -- do not guess."
    )
    resp = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}},
                {"type": "text", "text": prompt},
            ],
        }],
    )
    return "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")


def classify_photo(path: str, known_events: list[str]) -> dict:
    """Return {"match", "kind", "confidence"}. Never raises -- low confidence on any failure."""
    try:
        text = _call_vision(path, known_events)
        data = _extract_json(text)
        match = data.get("match") or None
        kind = data.get("kind") or None
        confidence = data.get("confidence") if data.get("confidence") in ("high", "low") else "low"
        if match not in known_events:
            match = None
        return {"match": match, "kind": kind, "confidence": confidence}
    except Exception as exc:
        print(f"[classify_photos] classification failed for {path}: {exc}")
        return {"match": None, "kind": None, "confidence": "low"}


def classify_new_photos(photo_dir: str, known_events: list[str], used_filenames: set) -> list[dict]:
    """Classify every eligible, unused photo in photo_dir. Returns a list of
    {"filename", "capture_time", "match", "kind", "confidence"} dicts."""
    if not os.path.isdir(photo_dir):
        return []
    out = []
    for filename in sorted(os.listdir(photo_dir)):
        path = os.path.join(photo_dir, filename)
        if not os.path.isfile(path) or filename in used_filenames:
            continue
        if filename.lower().endswith((".txt", ".md")) or not needs_classification(filename):
            continue
        result = classify_photo(path, known_events)
        if result["confidence"] != "high" or (not result["match"] and not result["kind"]):
            continue
        out.append({**result, "filename": filename, "capture_time": read_capture_time(path)})
    return out
