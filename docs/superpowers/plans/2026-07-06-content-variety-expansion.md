# Content Variety Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three new opportunistic post types (carousel, behind-the-scenes/vibe, community spotlight) to the existing Sunday-generate / owner-approves / hourly-post system, driven by automatic photo classification instead of filename renaming, without ever exceeding a hard daily post cap or drifting from Backyard Brew's authentic voice.

**Architecture:** A new classification pass (`classify_photos.py`) runs at the start of the Sunday job, tagging each un-suffixed photo with an event/vibe/spotlight guess using Claude vision + EXIF timestamps. `generate_captions.py` turns qualifying groups into extra `posts.csv` rows, subject to a hard per-day cap and anti-stacking scheduling. `anthropic_client.py` gets new voice framings for the new post types plus a repetition guard sourced from `posts.csv`'s own history. `meta_client.py` gets carousel (IG) and multi-photo (FB) posting paths; `post_to_meta.py` learns to drive them when a row has more than one photo.

**Tech Stack:** Python 3.11, Pillow (EXIF read via `Image.getexif()`), `anthropic` SDK (vision message content blocks), `requests` (Graph API), pytest.

## Global Constraints

- No `posts.csv` schema changes — `post_type` stays free text, `photos` stays comma-separated (both already true today).
- A filename suffix always overrides the AI's classification guess (mirrors existing `_art`-always-wins rule in `process_photos.resolve_mode`).
- Hard cap: never more than today + teaser + **one** extra post, per platform, per day — checked explicitly, not emergent.
- Extra posts are a ceiling (~3-4/week), never a quota — a thin week produces fewer, never padded.
- All new post types share the existing base brand-voice system prompt in `anthropic_client._system_prompt()` — only framing/CTA rules differ per type.
- Every new Graph API call must degrade gracefully (return `[]`/`None`/skip on failure) — never block caption generation or posting on a best-effort lookup, matching `meta_client._find_ig_location_id()`'s existing pattern.
- Timezone stays `America/Chicago` (`config.TIMEZONE`); date format stays `%Y-%m-%d`; scheduled_time format stays `"YYYY-MM-DD HH:MM"`.

---

## Task 1: Store helpers — recent captions + used-photo lookup

**Files:**
- Modify: `scripts/store.py`
- Test: `scripts/test_store.py` (new)

**Interfaces:**
- Consumes: `config.POSTS_CSV`, `config.POSTS_COLUMNS`, `store.load_posts()` (existing)
- Produces: `store.recent_captions_for_event(rows, event, limit=4) -> list[str]`, `store.used_photo_filenames(rows) -> set[str]` — both consumed by Task 3 and Task 5.

- [ ] **Step 1: Write the failing tests**

```python
# scripts/test_store.py
import store


def _row(event="Bingo Night", date="2026-06-01", status="posted",
         ig_caption="Old caption", photos="2026-06-01_bingo.jpg"):
    row = store.blank_row()
    row.update(event=event, date=date, status=status,
               ig_caption=ig_caption, photos=photos)
    return row


def test_recent_captions_for_event_returns_most_recent_first():
    rows = [
        _row(date="2026-05-04", ig_caption="First"),
        _row(date="2026-06-01", ig_caption="Second"),
        _row(date="2026-06-08", ig_caption="Third", status="approved"),
        _row(date="2026-06-08", event="Pool Night", ig_caption="Unrelated"),
    ]
    result = store.recent_captions_for_event(rows, "Bingo Night", limit=2)
    assert result == ["Third", "Second"]


def test_recent_captions_for_event_ignores_pending_rows():
    rows = [_row(status="needs_review", ig_caption="Not yet approved")]
    assert store.recent_captions_for_event(rows, "Bingo Night") == []


def test_used_photo_filenames_splits_comma_lists():
    rows = [
        _row(photos="2026-06-01_bingo.jpg, 2026-06-01_bingo_teaser.jpg"),
        _row(photos=""),
    ]
    result = store.used_photo_filenames(rows)
    assert result == {"2026-06-01_bingo.jpg", "2026-06-01_bingo_teaser.jpg"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_store.py -v`
Expected: FAIL with `AttributeError: module 'store' has no attribute 'recent_captions_for_event'`

- [ ] **Step 3: Implement the two helpers**

Add to `scripts/store.py` (after `blank_row()`):

```python
def recent_captions_for_event(rows, event, limit=4):
    """Most-recent-first ig_captions already posted/approved for this event.

    Used as the repetition guard so the caption prompt can be told what it
    already said recently and told not to repeat it.
    """
    matches = [r for r in rows
               if r["event"] == event and r["status"] in (config.STATUS_APPROVED, config.STATUS_POSTED)
               and r["ig_caption"]]
    matches.sort(key=lambda r: r["date"], reverse=True)
    return [r["ig_caption"] for r in matches[:limit]]


def used_photo_filenames(rows):
    """Every filename that already appears in some row's photos column."""
    used = set()
    for r in rows:
        for name in (r["photos"] or "").split(","):
            name = name.strip()
            if name:
                used.add(name)
    return used
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_store.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/store.py scripts/test_store.py
git commit -m "Add recent-caption and used-photo lookup helpers to store.py"
```

---

## Task 2: EXIF capture time + photo classification

**Files:**
- Create: `scripts/classify_photos.py`
- Test: `scripts/test_classify_photos.py`

**Interfaces:**
- Consumes: `config.PHOTOS_DIR`, `config.EVENT_ANGLES` (for the list of known event names), `anthropic_client._extract_json` (reused, not duplicated), `config.ANTHROPIC_MODEL`
- Produces: `classify_photos.read_capture_time(path) -> datetime | None`, `classify_photos.needs_classification(filename) -> bool`, `classify_photos.classify_photo(path, known_events) -> dict` (keys: `match` (event name or None), `kind` (`"event"`/`"vibe"`/`"spotlight"`/None), `confidence` (`"high"`/`"low"`)), `classify_photos.classify_new_photos(photo_dir, known_events, used_filenames) -> list[dict]` (each dict adds `filename` and `capture_time` to the classify_photo result) — consumed by Task 3.

- [ ] **Step 1: Write the failing tests**

```python
# scripts/test_classify_photos.py
from datetime import datetime
from unittest.mock import patch

import classify_photos


def test_needs_classification_skips_known_suffixes():
    assert classify_photos.needs_classification("2026-06-01_bingo_teaser.jpg") is False
    assert classify_photos.needs_classification("2026-06-01_bingo_art.png") is False
    assert classify_photos.needs_classification("2026-06-01_vibe_sunset.jpg") is False
    assert classify_photos.needs_classification("2026-06-01_spotlight_regular.jpg") is False


def test_needs_classification_allows_plain_photos():
    assert classify_photos.needs_classification("IMG_4821.jpg") is True
    assert classify_photos.needs_classification("bonfire_night.png") is True


def test_classify_photo_parses_model_response():
    fake_response_text = '{"match": "Bingo Night", "kind": "event", "confidence": "high"}'
    with patch("classify_photos._call_vision", return_value=fake_response_text):
        result = classify_photos.classify_photo("fake/path.jpg", ["Bingo Night", "Pool Night"])
    assert result == {"match": "Bingo Night", "kind": "event", "confidence": "high"}


def test_classify_photo_falls_back_to_low_confidence_on_bad_response():
    with patch("classify_photos._call_vision", return_value="not json at all"):
        result = classify_photos.classify_photo("fake/path.jpg", ["Bingo Night"])
    assert result == {"match": None, "kind": None, "confidence": "low"}


def test_classify_new_photos_skips_used_and_suffixed_files(tmp_path):
    (tmp_path / "2026-06-01_bingo_teaser.jpg").write_bytes(b"x")
    (tmp_path / "already_used.jpg").write_bytes(b"x")
    (tmp_path / "fresh_one.jpg").write_bytes(b"x")
    with patch("classify_photos.classify_photo",
               return_value={"match": None, "kind": "vibe", "confidence": "high"}), \
         patch("classify_photos.read_capture_time", return_value=datetime(2026, 6, 1, 18, 0)):
        result = classify_photos.classify_new_photos(
            str(tmp_path), ["Bingo Night"], used_filenames={"already_used.jpg"})
    assert len(result) == 1
    assert result[0]["filename"] == "fresh_one.jpg"
    assert result[0]["kind"] == "vibe"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_classify_photos.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'classify_photos'`

- [ ] **Step 3: Implement classify_photos.py**

```python
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
    if anthropic is None or not os.environ.get("ANTHROPIC_API_KEY"):
        return {"match": None, "kind": None, "confidence": "low"}
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_classify_photos.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/classify_photos.py scripts/test_classify_photos.py
git commit -m "Add EXIF + vision-based photo classification for extra post types"
```

---

## Task 3: Extra-post scheduling — hard daily cap, anti-stacking, row builder

**Files:**
- Modify: `scripts/config.py`
- Modify: `scripts/generate_captions.py`
- Test: `scripts/test_generate_captions.py` (new)

**Interfaces:**
- Consumes: `classify_photos.classify_new_photos(...)` (Task 2), `store.used_photo_filenames(rows)` (Task 1), `config.PHOTOS_DIR`, `config.EVENT_ANGLES`
- Produces: `config.MAX_EXTRA_POSTS_PER_DAY = 1`, `config.MAX_EXTRA_POSTS_PER_WEEK = 4`, `config.EXTRA_POST_TIME_EVENING = "19:30"`, `config.EXTRA_POST_TIME_MORNING = "11:30"`; `generate_captions.day_post_counts(rows) -> dict[str, int]`, `generate_captions.quietest_day(candidate_dates, counts) -> str`, `generate_captions.group_carousel_candidates(classified) -> list[dict]` (each: `event`, `filenames` (3+), `event_date_guess`), `generate_captions.build_extra_rows(classified, existing_rows, run_date) -> list[row]` — called from `main()`.

- [ ] **Step 1: Write the failing tests**

```python
# scripts/test_generate_captions.py
from datetime import date

import config
import generate_captions as gc
import store


def _scheduled_row(dt_str):
    row = store.blank_row()
    row["scheduled_time"] = dt_str
    return row


def test_day_post_counts_counts_by_date():
    rows = [_scheduled_row("2026-06-01 12:00"), _scheduled_row("2026-06-01 19:00"),
            _scheduled_row("2026-06-02 12:00")]
    counts = gc.day_post_counts(rows)
    assert counts == {"2026-06-01": 2, "2026-06-02": 1}


def test_quietest_day_picks_lowest_count():
    counts = {"2026-06-01": 2, "2026-06-02": 0, "2026-06-03": 1}
    assert gc.quietest_day(["2026-06-01", "2026-06-02", "2026-06-03"], counts) == "2026-06-02"


def test_group_carousel_candidates_requires_three_plus_same_event():
    classified = [
        {"filename": "a.jpg", "match": "Bingo Night", "kind": "event", "confidence": "high"},
        {"filename": "b.jpg", "match": "Bingo Night", "kind": "event", "confidence": "high"},
        {"filename": "c.jpg", "match": "Bingo Night", "kind": "event", "confidence": "high"},
        {"filename": "d.jpg", "match": "Pool Night", "kind": "event", "confidence": "high"},
    ]
    groups = gc.group_carousel_candidates(classified)
    assert len(groups) == 1
    assert groups[0]["event"] == "Bingo Night"
    assert sorted(groups[0]["filenames"]) == ["a.jpg", "b.jpg", "c.jpg"]


def test_build_extra_rows_never_exceeds_one_per_day():
    run_date = date(2026, 5, 31)  # a Sunday
    classified = [
        {"filename": "a.jpg", "match": "Bingo Night", "kind": "event", "confidence": "high"},
        {"filename": "b.jpg", "match": "Bingo Night", "kind": "event", "confidence": "high"},
        {"filename": "c.jpg", "match": "Bingo Night", "kind": "event", "confidence": "high"},
        {"filename": "vibe1.jpg", "match": None, "kind": "vibe", "confidence": "high"},
        {"filename": "vibe2.jpg", "match": None, "kind": "vibe", "confidence": "high"},
    ]
    existing_rows = [_scheduled_row("2026-06-01 12:00")]  # Monday already has 1 post
    rows = gc.build_extra_rows(classified, existing_rows, run_date)
    counts = gc.day_post_counts(existing_rows + rows)
    assert all(c <= 2 for c in counts.values())  # existing (1) + at most 1 extra
    assert len(rows) <= config.MAX_EXTRA_POSTS_PER_WEEK
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_generate_captions.py -v`
Expected: FAIL with `AttributeError: module 'generate_captions' has no attribute 'day_post_counts'`

- [ ] **Step 3: Add scheduling constants to config.py**

Add after `DEFAULT_TIME_FALLBACK` in `scripts/config.py`:

```python
# ---------------------------------------------------------------------------
# Extra post types (carousel / vibe / spotlight) -- opportunistic, capped.
# ---------------------------------------------------------------------------
EXTRA_POST_TYPES = ("carousel", "vibe", "spotlight")
MAX_EXTRA_POSTS_PER_DAY = 1     # per platform, on top of today/teaser -- hard cap
MAX_EXTRA_POSTS_PER_WEEK = 4    # ceiling, not a quota
EXTRA_POST_TIME_EVENING = "19:30"
EXTRA_POST_TIME_MORNING = "11:30"
```

- [ ] **Step 4: Implement the scheduling + grouping + row-builder functions**

Add to `scripts/generate_captions.py`, after `load_recurring_by_day()`:

```python
from collections import defaultdict

import classify_photos


def day_post_counts(rows):
    counts = {}
    for r in rows:
        d = (r.get("scheduled_time") or "").split(" ")[0]
        if d:
            counts[d] = counts.get(d, 0) + 1
    return counts


def quietest_day(candidate_dates, counts):
    return min(candidate_dates, key=lambda d: counts.get(d, 0))


def group_carousel_candidates(classified):
    """Group same-event 'event' kind photos into carousel candidates (3+ only)."""
    by_event = defaultdict(list)
    for item in classified:
        if item["kind"] == "event" and item["match"]:
            by_event[item["match"]].append(item)
    groups = []
    for event, items in by_event.items():
        if len(items) >= 3:
            groups.append({
                "event": event,
                "filenames": [i["filename"] for i in items],
                "capture_times": [i["capture_time"] for i in items if i["capture_time"]],
            })
    return groups


def build_extra_rows(classified, existing_rows, run_date):
    """Build carousel/vibe/spotlight rows, respecting the hard daily cap and
    the weekly ceiling. Never forces a post -- thin material means fewer rows."""
    counts = dict(day_post_counts(existing_rows))
    week_dates = [(run_date + timedelta(days=i)).strftime(DATE_FMT) for i in range(1, 8)]
    extra_rows = []

    def try_schedule(kind, event, key_details, filenames, preferred_date, time_slot):
        if len(extra_rows) >= config.MAX_EXTRA_POSTS_PER_WEEK:
            return
        candidates = [d for d in week_dates if counts.get(d, 0) < 2]  # today+teaser already = up to 2
        if not candidates:
            return
        target = preferred_date if preferred_date in candidates else quietest_day(candidates, counts)
        row = store.blank_row()
        row["date"] = target
        row["photos"] = ", ".join(filenames)
        row["event"] = event
        row["key_details"] = key_details
        row["platforms"] = "both"
        row["post_type"] = kind
        row["enhance"] = "none"
        row["scheduled_time"] = f"{target} {time_slot}"
        caps = generate_captions_for(event, key_details, dow_name(parse_date(target)), kind)
        row["fb_caption"] = caps["fb_caption"]
        row["ig_caption"] = caps["ig_caption"]
        row["status"] = config.STATUS_NEEDS_REVIEW
        extra_rows.append(row)
        counts[target] = counts.get(target, 0) + 1

    # Carousels: scheduled the day after the event, evening slot.
    for group in group_carousel_candidates(classified):
        times = [t for t in group["capture_times"] if t]
        event_day = times[0].date() if times else run_date
        recap_date = (event_day + timedelta(days=1)).strftime(DATE_FMT)
        try_schedule("carousel", group["event"], "A look back at last night.",
                     group["filenames"], recap_date, config.EXTRA_POST_TIME_EVENING)

    # Vibe + spotlight: single photos, quietest day, alternating morning/evening slot.
    singles = [i for i in classified if i["kind"] in ("vibe", "spotlight") and not i["match"]]
    for idx, item in enumerate(singles):
        kind = item["kind"]
        event_label = "Behind The Scenes" if kind == "vibe" else "Community Spotlight"
        slot = config.EXTRA_POST_TIME_MORNING if idx % 2 == 0 else config.EXTRA_POST_TIME_EVENING
        try_schedule(kind, event_label, "", [item["filename"]], week_dates[0], slot)

    return extra_rows


def generate_captions_for(event, key_details, day_of_week, post_type):
    """Thin wrapper so build_extra_rows doesn't need to import anthropic_client
    directly -- keeps the caption-generation entry point in one place."""
    from anthropic_client import generate_captions as _gen
    return _gen(event, key_details, day_of_week, post_type)
```

Also add `from datetime import timedelta` if not already imported at the top (it already is, per the existing `from datetime import datetime, timedelta` line) -- no change needed there.

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_generate_captions.py -v`
Expected: PASS (4 tests)

- [ ] **Step 6: Wire it into main()**

Modify `scripts/generate_captions.py`'s `main()` — add before the final `store.write_posts(all_rows)` call:

```python
    # --- 5. Extra post types: carousel / vibe / spotlight --------------------
    used = store.used_photo_filenames(posts + generated)
    known_events = list(config.EVENT_ANGLES.keys())
    classified = classify_photos.classify_new_photos(config.PHOTOS_DIR, known_events, used)
    extra_rows = build_extra_rows(classified, posts + generated, run_date)
    generated += extra_rows
    if extra_rows:
        store.log(f"generated {len(extra_rows)} extra post(s): "
                  f"{', '.join(r['post_type'] for r in extra_rows)}")
```

Move the existing `all_rows = posts + generated` / `store.write_posts(all_rows)` lines (currently step "4. Save") to after this new block.

- [ ] **Step 7: Run the full generate_captions test suite once more**

Run: `cd scripts && python -m pytest test_generate_captions.py test_store.py test_classify_photos.py -v`
Expected: PASS (all tests across the three files)

- [ ] **Step 8: Commit**

```bash
git add scripts/config.py scripts/generate_captions.py scripts/test_generate_captions.py
git commit -m "Add hard-capped, anti-stacking scheduling for carousel/vibe/spotlight posts"
```

---

## Task 4: New voice framings for vibe / spotlight / carousel

**Files:**
- Modify: `scripts/anthropic_client.py`
- Test: `scripts/test_anthropic_client.py` (new)

**Interfaces:**
- Consumes: nothing new — same `generate_captions(event, key_details, day_of_week, post_type, days_until=None, past_examples=None)` call signature stays intact for now (renamed in Task 5).
- Produces: `_framing()` and `fallback_captions()` both handle `post_type` values `"vibe"`, `"spotlight"`, `"carousel"` correctly — consumed already by Task 3's `generate_captions_for()`.

- [ ] **Step 1: Write the failing tests**

```python
# scripts/test_anthropic_client.py
import anthropic_client as ac


def test_framing_vibe_suppresses_cta():
    text = ac._framing("vibe", None)
    assert "no CTA" in text or "NO CTA" in text.upper()


def test_framing_spotlight_mentions_crediting():
    text = ac._framing("spotlight", None)
    assert "credit" in text.lower()


def test_framing_carousel_mentions_recap():
    text = ac._framing("carousel", None)
    assert "recap" in text.lower() or "looking back" in text.lower()


def test_fallback_captions_handles_vibe():
    result = ac.fallback_captions("Behind The Scenes", "", post_type="vibe")
    assert result["fb_caption"] and result["ig_caption"]


def test_fallback_captions_handles_spotlight():
    result = ac.fallback_captions("Community Spotlight", "", post_type="spotlight")
    assert result["fb_caption"] and result["ig_caption"]


def test_fallback_captions_handles_carousel():
    result = ac.fallback_captions("Bingo Night", "10 rounds", post_type="carousel")
    assert result["fb_caption"] and result["ig_caption"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_anthropic_client.py -v`
Expected: FAIL (`_framing("vibe", ...)` currently falls through to the reminder branch and won't mention "no CTA")

- [ ] **Step 3: Update `_framing()` and `fallback_captions()`**

Replace `_framing()` in `scripts/anthropic_client.py`:

```python
def _framing(post_type: str, days_until: int | None) -> str:
    """Return the timing/format-specific instruction for this post."""
    if post_type == "today":
        return ("This is a TODAY post -- urgent, same-day framing. It's happening TONIGHT, "
                "come now. Same-day energy.")
    if post_type == "teaser":
        return ("This is a TOMORROW TEASER post -- anticipation/planning framing. Tomorrow's "
                "the night, tell your people, get ready. Must feel genuinely different from the "
                "same event's today post, not a copy with the day swapped.")
    if post_type == "vibe":
        return ("This is a BEHIND-THE-SCENES / VIBE post. NO CTA, no membership mention, no "
                "urgency framing -- suspend the usual foot-traffic-CTA rule entirely for this "
                "one. Just a short, warm, personality-driven line about this specific candid "
                "moment. Its whole job is likability, not conversion.")
    if post_type == "spotlight":
        return ("This is a COMMUNITY SPOTLIGHT post. Credit the person or moment specifically "
                "and warmly -- a genuine shoutout, not a generic mention. If concrete facts were "
                "given, use them exactly. If not, write a plausible generic shoutout from what "
                "the photo shows -- never invent a specific name.")
    if post_type == "carousel":
        return ("This is a CAROUSEL recap post, published the day AFTER the event, covering "
                "several photos from that night. Frame it as looking back at how it went -- "
                "'here's how last night went down' energy -- not urgency to attend, since it "
                "already happened.")
    # Campaign reminder
    if days_until is not None and days_until >= 10:
        urgency = "It's a couple weeks out -- 'mark your calendar / save the date' energy, build anticipation."
    elif days_until is not None and days_until >= 4:
        urgency = "It's about a week out -- 'start making plans, clear your schedule' energy."
    else:
        urgency = "It's just days away -- rising urgency, 'this is almost here, lock it in' energy."
    return (f"This is a REMINDER post {days_until} days before the event. {urgency} "
            "It must read differently from the other reminders in this campaign -- new hook, "
            "new angle, never a repeat.")
```

Replace `fallback_captions()`:

```python
def fallback_captions(event, key_details, post_type="today", days_until=None) -> dict:
    """Simple templated captions used when the API is unavailable.

    Framing-aware so an outage still produces a sensible-sounding post. Not
    fancy -- just enough for the owner to review and rewrite by hand.
    """
    details = key_details.strip().rstrip(".") if key_details else ""
    first = details.split(",")[0].strip() if details else event
    if post_type == "today":
        when_fb, when_ig = "Tonight at", f"{event} tonight \U0001F37A"
    elif post_type == "teaser":
        when_fb, when_ig = "Tomorrow at", f"Tomorrow: {event} \U0001F37A"
    elif post_type == "vibe":
        fb = f"Just another day at {config.BUSINESS['name']} \U0001F332\U0001F37A."
        ig = "Living the backyard life \U0001F332"
        return {"fb_caption": fb, "ig_caption": ig, "_fallback": True}
    elif post_type == "spotlight":
        fb = f"Shoutout to our regulars at {config.BUSINESS['name']} -- you make this place \U0001F37A."
        ig = "Community shoutout \U0001F3AF"
        return {"fb_caption": fb, "ig_caption": ig, "_fallback": True}
    elif post_type == "carousel":
        fb = (f"Last night at {config.BUSINESS['name']} -- {event}! {details or 'Great crowd, great time.'} "
              "Wisconsin-made drinks, disc golf & hiking out back. Come see for yourself next time!")
        ig = f"Last night: {event} \U0001F37A recap"
        return {"fb_caption": fb, "ig_caption": ig, "_fallback": True}
    else:  # reminder
        lead = (f"{days_until} days out" if days_until else "Coming up")
        when_fb, when_ig = f"{lead} at", f"Mark your calendar: {event} \U0001F37A"
    fb = (f"{when_fb} {config.BUSINESS['name']} -- {event}! {details}. "
          f"All Wisconsin-made drinks, disc golf & hiking out back. See you there!")
    ig = f"{when_ig} {first}. Come hang."
    return {"fb_caption": fb, "ig_caption": ig, "_fallback": True}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_anthropic_client.py -v`
Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/anthropic_client.py scripts/test_anthropic_client.py
git commit -m "Add vibe/spotlight/carousel voice framings and fallback captions"
```

---

## Task 5: Real caption history — voice anchor + repetition guard

**Files:**
- Modify: `scripts/meta_client.py`
- Modify: `scripts/anthropic_client.py`
- Modify: `scripts/generate_captions.py`
- Test: `scripts/test_anthropic_client.py` (append), `scripts/test_meta_client.py` (new)

**Interfaces:**
- Consumes: `store.recent_captions_for_event(rows, event, limit=4)` (Task 1)
- Produces: `meta_client.recent_page_posts(limit=6) -> list[str]`; `anthropic_client.generate_captions(event, key_details, day_of_week, post_type, days_until=None, voice_examples=None, avoid_examples=None)` (renamed/expanded from `past_examples`); `generate_captions.py`'s `main()` fetches `voice_examples` once and threads `avoid_examples` per-row into `build_row()` and `generate_captions_for()`.

- [ ] **Step 1: Write the failing tests**

```python
# scripts/test_meta_client.py
from unittest.mock import patch

import meta_client


def test_recent_page_posts_returns_messages_only():
    fake_response = {"data": [{"message": "Bingo's back!"}, {"id": "123"}, {"message": "Poker night."}]}
    with patch("meta_client._get", return_value=fake_response):
        result = meta_client.recent_page_posts(limit=6)
    assert result == ["Bingo's back!", "Poker night."]


def test_recent_page_posts_returns_empty_on_failure():
    with patch("meta_client._get", side_effect=meta_client.MetaError("boom")):
        result = meta_client.recent_page_posts(limit=6)
    assert result == []
```

```python
# scripts/test_anthropic_client.py -- append these
def test_user_prompt_includes_avoid_examples():
    text = ac._user_prompt("Bingo Night", "details", "Monday", "today", None, None,
                           voice_examples=[], avoid_examples=["Old hook line"])
    assert "Old hook line" in text
    assert "do not" in text.lower() or "avoid" in text.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_meta_client.py test_anthropic_client.py -v`
Expected: FAIL (`meta_client.recent_page_posts` doesn't exist; `_user_prompt` doesn't accept `voice_examples`/`avoid_examples`)

- [ ] **Step 3: Add `recent_page_posts()` to meta_client.py**

Add near the bottom of `scripts/meta_client.py`, before the token-expiry section:

```python
# ---------------------------------------------------------------------------
# Real post history (voice anchor for caption generation)
# ---------------------------------------------------------------------------
def recent_page_posts(limit=6):
    """Best-effort pull of the Page's own recent post captions, for voice
    matching. Returns [] on any failure -- must never block generation."""
    try:
        pid = _page_id()
        res = _get(f"{pid}/posts", {"fields": "message", "limit": limit})
        return [p["message"] for p in res.get("data", []) if p.get("message")]
    except Exception as exc:
        print(f"[meta_client] could not pull recent page posts: {exc}")
        return []
```

- [ ] **Step 4: Update `_user_prompt()` and `generate_captions()` in anthropic_client.py**

Replace `_user_prompt()`:

```python
def _user_prompt(event, key_details, day_of_week, post_type, days_until,
                 angle, voice_examples, avoid_examples):
    parts = [
        f"EVENT: {event}",
        f"DAY: {day_of_week}",
        f"KEY DETAILS (work these facts in accurately): {key_details}",
        f"REAL OPEN HOURS that day: {config.HOURS.get(day_of_week, 'see website')}",
    ]
    if angle:
        parts.append(f"CONTENT ANGLE for this event: {angle}")
    parts.append(_framing(post_type, days_until))
    if voice_examples:
        joined = "\n---\n".join(voice_examples[:4])
        parts.append("REFERENCE -- some of the bar's real past captions for voice matching "
                     f"(match the vibe, do not copy):\n{joined}")
    if avoid_examples:
        joined = "\n---\n".join(avoid_examples[:4])
        parts.append("DO NOT REPEAT -- captions already used recently for this exact event. "
                     f"Write something with a genuinely different hook, phrasing, and structure:\n{joined}")
    parts.append('Write the two captions now. Return ONLY the JSON object.')
    return "\n\n".join(parts)
```

Replace `generate_captions()`:

```python
def generate_captions(event, key_details, day_of_week, post_type,
                      days_until=None, voice_examples=None, avoid_examples=None):
    """Generate {fb_caption, ig_caption} for one post.

    Falls back to a templated caption on any error. Never raises -- the Sunday
    job must keep going even if one caption fails.
    """
    angle = config.EVENT_ANGLES.get(event)
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if anthropic is None or not api_key:
        return fallback_captions(event, key_details, post_type, days_until)

    try:
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=1024,
            system=_system_prompt(),
            messages=[{
                "role": "user",
                "content": _user_prompt(event, key_details, day_of_week,
                                        post_type, days_until, angle,
                                        voice_examples or [], avoid_examples or []),
            }],
        )
        text = "".join(block.text for block in resp.content
                       if getattr(block, "type", None) == "text")
        data = _extract_json(text)
        fb = str(data.get("fb_caption", "")).strip()
        ig = str(data.get("ig_caption", "")).strip()
        if not fb or not ig:
            raise ValueError("model returned an empty caption")
        ig = re.sub(r"#\w+", "", ig).strip()
        fb = re.sub(r"#\w+", "", fb).strip()
        return {"fb_caption": fb, "ig_caption": ig, "_fallback": False}
    except Exception as exc:
        print(f"[anthropic_client] caption generation failed, using fallback: {exc}")
        return fallback_captions(event, key_details, post_type, days_until)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_meta_client.py test_anthropic_client.py -v`
Expected: PASS (all tests in both files)

- [ ] **Step 6: Wire voice_examples/avoid_examples through generate_captions.py**

In `scripts/generate_captions.py`:

Replace the `past_examples()` function entirely (delete it — superseded by real history) and update `build_row()`:

```python
def build_row(event_date, post_date, event, key_details, platforms,
              post_type, photo, enhance, owner_time="", days_until=None,
              voice_examples=None, avoid_examples=None):
    """Assemble one fully-generated posts.csv row (status = needs_review)."""
    dow_event = dow_name(event_date)
    row = store.blank_row()
    row["date"] = event_date.strftime(DATE_FMT)
    row["photos"] = photo or ""
    row["event"] = event
    row["key_details"] = key_details
    row["platforms"] = platforms or "both"
    row["post_type"] = post_type
    row["enhance"] = enhance
    row["scheduled_time"] = scheduled_string(post_date, dow_name(post_date),
                                             post_type, owner_time)
    caps = generate_captions(event, key_details, dow_event, post_type,
                             days_until=days_until,
                             voice_examples=voice_examples,
                             avoid_examples=avoid_examples)
    row["fb_caption"] = caps["fb_caption"]
    row["ig_caption"] = caps["ig_caption"]
    row["_fallback"] = caps.get("_fallback", False)
    row["status"] = config.STATUS_NEEDS_REVIEW
    return row
```

In `main()`, right after `run_date = today_local()`, add:

```python
    voice_examples = meta_client.recent_page_posts(limit=6)
```

And add `import meta_client` to the top imports of `generate_captions.py`.

Every call to `build_row(...)` inside `main()` that has access to `event` should now also pass `avoid_examples=store.recent_captions_for_event(posts, event, limit=4)` and `voice_examples=voice_examples`. Update the three call sites (campaign expansion loop, today-post block, teaser-post block) by adding these two keyword arguments to each existing `build_row(...)` call, e.g.:

```python
            generated.append(build_row(
                event_date, post_date, event, details, platforms,
                ptype, photo, enhance,
                days_until=(days_before if days_before >= 2 else None),
                voice_examples=voice_examples,
                avoid_examples=store.recent_captions_for_event(posts, event, limit=4)))
```

(Apply the same two extra keyword arguments to the other two `build_row(...)` call sites in `main()`.)

Also update `generate_captions_for()` (added in Task 3) to accept and forward these:

```python
def generate_captions_for(event, key_details, day_of_week, post_type,
                          voice_examples=None, avoid_examples=None):
    from anthropic_client import generate_captions as _gen
    return _gen(event, key_details, day_of_week, post_type,
               voice_examples=voice_examples, avoid_examples=avoid_examples)
```

And update `build_extra_rows()`'s `try_schedule()` inner function to pass these through too — add `voice_examples` as a parameter to `build_extra_rows(classified, existing_rows, run_date, voice_examples=None, avoid_examples_by_event=None)` and thread it into the `generate_captions_for(...)` call inside `try_schedule`. Update the `main()` call site accordingly:

```python
    extra_rows = build_extra_rows(classified, posts + generated, run_date,
                                  voice_examples=voice_examples)
```

- [ ] **Step 7: Run the full test suite**

Run: `cd scripts && python -m pytest -v`
Expected: PASS (every test file green)

- [ ] **Step 8: Commit**

```bash
git add scripts/meta_client.py scripts/anthropic_client.py scripts/generate_captions.py scripts/test_meta_client.py scripts/test_anthropic_client.py
git commit -m "Wire real voice-anchor and repetition-guard caption history into generation"
```

---

## Task 6: Carousel (Instagram) + multi-photo (Facebook) posting

**Files:**
- Modify: `scripts/meta_client.py`
- Test: `scripts/test_meta_client.py` (append)

**Interfaces:**
- Consumes: `meta_client._post`, `meta_client._get`, `meta_client._ig_id`, `meta_client._page_id`, `meta_client._find_ig_location_id`, `meta_client._wait_container_ready` (all existing)
- Produces: `meta_client.post_instagram_carousel(image_urls: list[str], caption: str, hashtags: str) -> str`, `meta_client.post_facebook_multi(image_urls: list[str], caption: str) -> str` — consumed by Task 7.

- [ ] **Step 1: Write the failing tests**

```python
# scripts/test_meta_client.py -- append
from unittest.mock import patch

import meta_client


def test_post_instagram_carousel_builds_children_then_publishes():
    calls = []

    def fake_post(path, data):
        calls.append((path, data))
        if path.endswith("/media") and data.get("is_carousel_item"):
            return {"id": f"child-{len(calls)}"}
        if path.endswith("/media") and data.get("media_type") == "CAROUSEL":
            return {"id": "parent-container"}
        if path.endswith("/media_publish"):
            return {"id": "published-123"}
        if path.endswith("/comments"):
            return {"id": "comment-1"}
        raise AssertionError(f"unexpected path {path}")

    with patch("meta_client._post", side_effect=fake_post), \
         patch("meta_client._get", return_value={"status_code": "FINISHED"}), \
         patch("meta_client._ig_id", return_value="ig123"), \
         patch("meta_client._find_ig_location_id", return_value=None):
        result = meta_client.post_instagram_carousel(
            ["https://x/1.jpg", "https://x/2.jpg", "https://x/3.jpg"], "caption", "#tags")

    assert result == "published-123"
    child_calls = [c for c in calls if c[1].get("is_carousel_item")]
    assert len(child_calls) == 3


def test_post_facebook_multi_uploads_unpublished_then_posts():
    calls = []

    def fake_post(path, data):
        calls.append((path, data))
        if path.endswith("/photos"):
            return {"id": f"photo-{len(calls)}"}
        if path.endswith("/feed"):
            return {"id": "feed-post-1"}
        raise AssertionError(f"unexpected path {path}")

    with patch("meta_client._post", side_effect=fake_post), \
         patch("meta_client._page_id", return_value="page123"):
        result = meta_client.post_facebook_multi(["https://x/1.jpg", "https://x/2.jpg"], "caption")

    assert result == "feed-post-1"
    photo_calls = [c for c in calls if c[0].endswith("/photos")]
    assert len(photo_calls) == 2
    assert all(c[1].get("published") == "false" for c in photo_calls)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_meta_client.py -v`
Expected: FAIL with `AttributeError: module 'meta_client' has no attribute 'post_instagram_carousel'`

- [ ] **Step 3: Implement both functions**

Add `import json` to the top imports of `scripts/meta_client.py` (alongside the existing `import os`, `import time`, `import urllib.parse`).

Add after `post_instagram()` in `scripts/meta_client.py`:

```python
def post_instagram_carousel(image_urls: list[str], caption: str, hashtags: str) -> str:
    """Publish an IG carousel (2-10 photos). Same location/hashtag behavior
    as a single post; the caption goes on the parent container, hashtags in
    the first comment on the published post."""
    iid = _ig_id()
    child_ids = [_post(f"{iid}/media", {"image_url": u, "is_carousel_item": "true"})["id"]
                for u in image_urls]
    loc = _find_ig_location_id()
    container = {"media_type": "CAROUSEL", "children": ",".join(child_ids), "caption": caption}
    if loc:
        container["location_id"] = loc
    try:
        created = _post(f"{iid}/media", container)
    except MetaError as exc:
        if loc:
            print(f"[meta_client] IG carousel with location failed, retrying untagged: {exc}")
            created = _post(f"{iid}/media", {"media_type": "CAROUSEL",
                                             "children": ",".join(child_ids), "caption": caption})
        else:
            raise
    creation_id = created["id"]
    _wait_container_ready(creation_id)
    published = _post(f"{iid}/media_publish", {"creation_id": creation_id})
    media_id = published["id"]
    if hashtags:
        try:
            _post(f"{media_id}/comments", {"message": hashtags})
        except MetaError as exc:
            print(f"[meta_client] IG carousel hashtag comment failed (post still live): {exc}")
    return media_id


def post_facebook_multi(image_urls: list[str], caption: str) -> str:
    """Publish a single FB post with several attached photos (album-style)."""
    pid = _page_id()
    photo_ids = [_post(f"{pid}/photos", {"url": u, "published": "false"})["id"] for u in image_urls]
    attached_media = json.dumps([{"media_fbid": pid_} for pid_ in photo_ids])
    data = {"message": caption, "place": pid, "attached_media": attached_media}
    try:
        res = _post(f"{pid}/feed", data)
    except MetaError as exc:
        print(f"[meta_client] FB multi-photo post with place failed, retrying untagged: {exc}")
        data.pop("place")
        res = _post(f"{pid}/feed", data)
    return res.get("post_id") or res.get("id", "")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_meta_client.py -v`
Expected: PASS (all tests in the file)

- [ ] **Step 5: Commit**

```bash
git add scripts/meta_client.py scripts/test_meta_client.py
git commit -m "Add Instagram carousel and Facebook multi-photo posting"
```

---

## Task 7: Multi-photo row handling in the hourly posting job

**Files:**
- Modify: `scripts/post_to_meta.py`
- Test: `scripts/test_post_to_meta.py` (new)

**Interfaces:**
- Consumes: `meta_client.post_instagram_carousel`, `meta_client.post_facebook_multi` (Task 6), `process_photos.process`, `process_photos.output_name` (existing, unchanged)
- Produces: `post_to_meta.source_photo_paths(row) -> list[str]` (replaces single-path lookup), updated `post_to_meta.post_row(row)` that posts a carousel/multi-photo when a row has more than one filename.

- [ ] **Step 1: Write the failing tests**

```python
# scripts/test_post_to_meta.py
import os
from unittest.mock import patch

import config
import post_to_meta as ptm
import store


def _row(photos, platforms="both", post_type="today"):
    row = store.blank_row()
    row.update(photos=photos, platforms=platforms, post_type=post_type,
               event="Bingo Night", date="2026-06-01", key_details="",
               fb_caption="FB caption", ig_caption="IG caption",
               scheduled_time="2026-06-01 12:00", status=config.STATUS_APPROVED)
    return row


def test_source_photo_paths_returns_all_existing_files(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "a.jpg").write_bytes(b"x")
    (tmp_path / "b.jpg").write_bytes(b"x")
    row = _row("a.jpg, b.jpg, missing.jpg")
    result = ptm.source_photo_paths(row)
    assert len(result) == 2
    assert all(os.path.basename(p) in ("a.jpg", "b.jpg") for p in result)


def test_source_photo_paths_empty_when_none_exist(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    row = _row("missing.jpg")
    assert ptm.source_photo_paths(row) == []


def test_post_row_uses_carousel_path_for_multi_photo_ig(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    monkeypatch.setattr(config, "GENERATED_DIR", str(tmp_path / "_generated"))
    monkeypatch.setattr(ptm, "DRY_RUN", True)
    for name in ("a.jpg", "b.jpg", "c.jpg"):
        (tmp_path / name).write_bytes(b"\xff\xd8\xff\xe0" + b"0" * 100)
    row = _row("a.jpg, b.jpg, c.jpg", platforms="ig")
    with patch("post_to_meta.wait_url_live", return_value=True), \
         patch("post_to_meta.push_images"):
        succeeded = ptm.post_row(row)
    assert succeeded == {"ig"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_post_to_meta.py -v`
Expected: FAIL with `AttributeError: module 'post_to_meta' has no attribute 'source_photo_paths'`

- [ ] **Step 3: Replace `source_photo_path` and rewrite `post_row`**

In `scripts/post_to_meta.py`, replace `source_photo_path()`:

```python
def source_photo_paths(row):
    """All filenames in the photos column that actually exist -> absolute paths."""
    names = [n.strip() for n in (row["photos"] or "").split(",") if n.strip()]
    paths = [os.path.join(config.PHOTOS_DIR, n) for n in names]
    return [p for p in paths if os.path.exists(p)]
```

Replace `post_row()`:

```python
def post_row(row):
    """Post one row (single photo or multi-photo carousel/album). Returns the
    set of platform codes that succeeded."""
    srcs = source_photo_paths(row)
    if not srcs:
        store.log(f"MISSING PHOTO for '{row['event']}' {row['scheduled_time']} "
                  f"-> '{row['photos']}' not in /photos/. Left approved for retry.")
        return set()

    succeeded = set()
    to_push, jobs = [], []

    if wants(row["platforms"], "fb"):
        fb_rels = []
        for i, src in enumerate(srcs):
            label = f"fb{i}" if len(srcs) > 1 else "fb"
            _, rel = render_variant(src, row, "fb_feed", label)
            fb_rels.append(rel)
        to_push += fb_rels
        jobs.append(("fb", fb_rels))

    if wants(row["platforms"], "ig"):
        ig_feed_rels = []
        for i, src in enumerate(srcs):
            label = f"ig-feed{i}" if len(srcs) > 1 else "ig-feed"
            _, rel = render_variant(src, row, "ig_feed", label)
            ig_feed_rels.append(rel)
        _, story_rel = render_variant(srcs[0], row, "ig_story", "ig-story")
        to_push += ig_feed_rels + [story_rel]
        jobs.append(("ig", (ig_feed_rels, story_rel)))

    push_images(to_push)

    for code, payload in jobs:
        try:
            if code == "fb":
                urls = [meta_client.public_image_url(p) for p in payload]
                for u in urls:
                    if not wait_url_live(u):
                        raise meta_client.MetaError(f"image URL not live yet: {u}")
                if DRY_RUN:
                    store.log(f"[DRY RUN] would post FB ({len(urls)} photo(s)): {row['event']}")
                elif len(urls) > 1:
                    meta_client.post_facebook_multi(urls, row["fb_caption"])
                else:
                    meta_client.post_facebook(urls[0], row["fb_caption"])
                succeeded.add("fb")
            else:  # ig
                feed_rels, story_rel = payload
                feed_urls = [meta_client.public_image_url(p) for p in feed_rels]
                story_url = meta_client.public_image_url(story_rel)
                for u in feed_urls + [story_url]:
                    if not wait_url_live(u):
                        raise meta_client.MetaError("IG image URL not live yet")
                if DRY_RUN:
                    store.log(f"[DRY RUN] would post IG ({len(feed_urls)} photo(s)) "
                             f"feed+story+hashtags: {row['event']}")
                else:
                    if len(feed_urls) > 1:
                        meta_client.post_instagram_carousel(feed_urls, row["ig_caption"], hashtags_for(row))
                    else:
                        meta_client.post_instagram(feed_urls[0], row["ig_caption"], hashtags_for(row))
                    try:
                        meta_client.post_instagram_story(story_url)
                    except meta_client.MetaError as exc:
                        store.log(f"IG story repost failed (feed post is live): {exc}")
                succeeded.add("ig")
        except Exception as exc:
            store.log(f"POST FAILED [{code}] '{row['event']}' {row['scheduled_time']}: {exc}")

    return succeeded
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_post_to_meta.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Run the entire project test suite**

Run: `cd scripts && python -m pytest -v`
Expected: PASS (every test across every file in `scripts/`)

- [ ] **Step 6: Commit**

```bash
git add scripts/post_to_meta.py scripts/test_post_to_meta.py
git commit -m "Handle multi-photo rows via IG carousel / FB album posting in the hourly job"
```

---

## Task 8: End-to-end dry run

**Files:**
- None created/modified — verification only.

- [ ] **Step 1: Run the full test suite one final time**

Run: `cd scripts && python -m pytest -v`
Expected: PASS, zero failures, across `test_store.py`, `test_classify_photos.py`, `test_generate_captions.py`, `test_anthropic_client.py`, `test_meta_client.py`, `test_post_to_meta.py`.

- [ ] **Step 2: Dry-run the Sunday job locally (no live API calls needed for structure check)**

Run: `cd scripts && ANTHROPIC_API_KEY= python generate_captions.py`
Expected: Exits cleanly; with no API key set, all captions fall back to templates (per existing fallback behavior) and `posts.csv` gains new rows without error, including any classified carousel/vibe/spotlight rows if eligible test photos are present in `/photos/`. Check `status.log` for a `Sunday job done` line.

- [ ] **Step 3: Dry-run the hourly job**

Run: `cd scripts && DRY_RUN=1 python post_to_meta.py`
Expected: Exits cleanly; any `approved` + past-due rows (including multi-photo ones) log `[DRY RUN] would post ...` lines without making real network calls to Meta.

- [ ] **Step 4: Commit final state (if any local-only files like `__pycache__` need a .gitignore touch-up, otherwise skip)**

```bash
git status
# If clean, nothing to commit here -- this task is verification-only.
```

---

## Self-Review Notes

- **Spec coverage:** All spec sections have a task — classification/no-renaming (Task 2), hard daily cap + scheduling (Task 3), shared-voice framings (Task 4), caption-freshness voice-anchor + repetition-guard (Task 5), carousel/FB-multi posting mechanics (Task 6), row-driving in the hourly job (Task 7), end-to-end check (Task 8). Photo-consumption tracking (`used_photo_filenames`) is folded into Task 1 rather than a separate task, per the "fold setup into the task whose deliverable needs it" rule.
- **Placeholder scan:** no TBD/TODO; every step contains real, complete code, not descriptions of code.
- **Type consistency:** `generate_captions()`'s signature changes once, cleanly, in Task 5 (from the Task-1-era `past_examples` param used nowhere until then, straight to `voice_examples`/`avoid_examples`) — no task after Task 5 references the old name. `source_photo_path` (singular) is fully replaced by `source_photo_paths` (plural) in Task 7, with no leftover caller of the old name (the only caller, `render_variant`'s invocation inside `post_row`, is rewritten in the same task).
