# Undated Event/Food Photo Pool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let any undated photo whose filename contains an event or food keyword automatically enter a rotating pool for that event, instead of the system always falling back to the same static default poster.

**Architecture:** A shared LRU-selection helper in `generate_captions.py` picks the least-recently-used eligible photo for a keyword set, reusing `classify_photos`'s existing filename/video-exclusion helpers. It's wired into `find_photo()` as a new middle tier (between exact dated match and the static default) and into a new `find_food_photo()` that attaches a second "food" photo to a recurring event's "today" post. Pool-claimed filenames are excluded from vision classification so nothing is double-charged or double-purposed.

**Tech Stack:** Python 3.11, pytest, existing repo conventions (no new dependencies).

## Global Constraints

- Case-insensitive substring match anywhere in the filename for all keyword matching.
- LRU rule: a never-used photo always wins over any previously-used photo; among never-used candidates, ties break toward the newest real photo capture time (`classify_photos.read_capture_time`); among previously-used candidates, the one used longest ago wins. No photo is ever permanently retired from a pool.
- An event's own static `default_photo` filename (e.g. `Bingo_default_art.jpg`) must never be treated as a pool candidate for its own event, even though its filename contains that event's keyword.
- Feature is scoped to the six recurring events in `recurring_events.csv` only — no change to one-off/pending/campaign event photo handling, no Sunday recurring event, no `_deal`-suffix change.
- Food second-slide only attaches to a recurring event's "today" post, never a teaser, and never blocks the main post when no eligible food photo exists.
- `pizza` is served every day at the bar (per the owner) — unlike other food keywords, it maps to all six recurring events but only attaches on one deterministically-rotating day per week, so it doesn't show up on every single post.
- No new dependencies, no CI/workflow changes.

---

### Task 1: Config keyword maps + exclude pool-claimed photos from vision classification

**Files:**
- Modify: `scripts/config.py` (add near the bottom, after `TRAIL_HIGHLIGHTS`, before `pick_hashtags`)
- Modify: `scripts/classify_photos.py:32-48` (near `MANUAL_KIND_SUFFIXES`/`manual_kind`)
- Test: `scripts/test_classify_photos.py`

**Interfaces:**
- Produces: `config.EVENT_PHOTO_KEYWORDS: dict[str, list[str]]`, `config.FOOD_PHOTO_KEYWORDS: dict[str, list[str]]`, `config.OCCASIONAL_FOOD_KEYWORDS: set[str]`, `config.RECURRING_DAYS: list[str]`, `classify_photos.pool_claimed(filename: str) -> bool`

- [ ] **Step 1: Write the failing tests**

Add to `scripts/test_classify_photos.py` (after the existing `manual_kind` tests):

```python
def test_pool_claimed_matches_event_keyword():
    assert classify_photos.pool_claimed("party_bingo.jpg") is True
    assert classify_photos.pool_claimed("randomname.jpg") is False


def test_pool_claimed_matches_food_keyword():
    assert classify_photos.pool_claimed("wednesday_taco_special.jpg") is True
    assert classify_photos.pool_claimed("fresh_pizza_pie.jpg") is True


def test_pool_claimed_recognizes_an_events_own_default_art_filename():
    # Already excluded from classification by the existing "_art" check in
    # needs_classification() -- pool_claimed() should also recognize it as
    # claimed, never mistakenly report False.
    assert classify_photos.pool_claimed("Bingo_default_art.jpg") is True


def test_classify_new_photos_skips_pool_claimed_filenames(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CLASSIFICATION_CACHE", str(tmp_path / "cache.json"))
    photo_dir = tmp_path / "photos"
    photo_dir.mkdir()
    (photo_dir / "party_bingo.jpg").write_bytes(b"x")
    with patch("classify_photos.classify_photo") as mock_classify:
        result = classify_photos.classify_new_photos(
            str(photo_dir), ["Bingo Night"], used_filenames=set())
    mock_classify.assert_not_called()
    assert result == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_classify_photos.py -v -k "pool_claimed or skips_pool_claimed"`
Expected: FAIL with `AttributeError: module 'classify_photos' has no attribute 'pool_claimed'`

- [ ] **Step 3: Add the config keyword maps**

In `scripts/config.py`, add this block immediately after the `TRAIL_HIGHLIGHTS` list (after line 256, before `def pick_hashtags`):

```python
# ---------------------------------------------------------------------------
# Undated event/food photo pools. A photo whose filename contains one of
# these keywords (case-insensitive substring, anywhere) automatically enters
# that event's rotation instead of the system always falling back to the
# same static default poster. See generate_captions._pick_pool_photo().
# ---------------------------------------------------------------------------
EVENT_PHOTO_KEYWORDS = {
    "Bingo Night": ["bingo"],
    "Pickleball Open Play": ["pickleball"],
    "Tacos + Poker Club": ["poker"],
    "Ladies Night + Line Dancing": ["linedancing", "ladiesnight", "ladies"],
    "Karaoke Night": ["karaoke"],
    "Pool Night": ["pool"],
}

# Food photos attach as a SECOND photo on the mapped event's "today" post
# (never replacing the main event photo, never on teasers). "pizza" is
# served every day at the bar, so unlike the others it maps to every event
# but only actually attaches on one rotating day per week -- see
# OCCASIONAL_FOOD_KEYWORDS and generate_captions.find_food_photo().
RECURRING_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

FOOD_PHOTO_KEYWORDS = {
    "hotdog": ["Bingo Night", "Pickleball Open Play"],
    "taco": ["Tacos + Poker Club"],
    "nachos": ["Tacos + Poker Club"],
    "quesadilla": ["Tacos + Poker Club"],
    "breakfastburrito": ["Pool Night"],
    "pizza": list(EVENT_PHOTO_KEYWORDS.keys()),
}

OCCASIONAL_FOOD_KEYWORDS = {"pizza"}
```

- [ ] **Step 4: Add `pool_claimed()` and wire it into `classify_new_photos()`**

In `scripts/classify_photos.py`, add this function right after `manual_kind()` (after line 48, before the `VIDEO_EXTENSIONS` comment on line 50):

```python
def pool_claimed(filename: str) -> bool:
    """True if this filename's stem contains a keyword from
    config.EVENT_PHOTO_KEYWORDS or config.FOOD_PHOTO_KEYWORDS -- these
    photos are handled by the event/food photo pool (generate_captions.py),
    not by vision classification, so they must never also become a
    vibe/spotlight/carousel candidate (one job per photo, no wasted call)."""
    stem = os.path.splitext(filename)[0].lower()
    for keywords in config.EVENT_PHOTO_KEYWORDS.values():
        if any(kw.lower() in stem for kw in keywords):
            return True
    for keyword in config.FOOD_PHOTO_KEYWORDS:
        if keyword.lower() in stem:
            return True
    return False
```

Then in `classify_new_photos()` (around line 192-198), insert a `pool_claimed` check right after the `manual_kind` block and before the `needs_classification` check:

```python
        kind = manual_kind(filename)
        if kind:
            out.append({"filename": filename, "capture_time": read_capture_time(path),
                       "match": None, "kind": kind, "confidence": "high"})
            continue
        if pool_claimed(filename):
            continue
        if not needs_classification(filename):
            continue
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_classify_photos.py -v`
Expected: PASS (all tests, including the new ones)

- [ ] **Step 6: Commit**

```bash
git add scripts/config.py scripts/classify_photos.py scripts/test_classify_photos.py
git commit -m "Add event/food photo keyword config and exclude pool-claimed photos from vision classification"
```

---

### Task 2: Shared LRU pool-selection engine

**Files:**
- Modify: `scripts/generate_captions.py` (add after `find_deal_photo`, before `render_generated_images`, i.e. after line 105)
- Test: `scripts/test_generate_captions.py`

**Interfaces:**
- Consumes: `config.PHOTOS_DIR`, `classify_photos.VIDEO_EXTENSIONS`, `classify_photos.read_capture_time(path) -> datetime | None`, `list_photos() -> list[str]` (already defined in this file)
- Produces: `_photo_last_used(rows: list[dict]) -> dict[str, str]`, `_pool_candidates(keywords: list[str], exclude_filenames: set[str], posts_history: list[dict]) -> list[tuple[str, str | None]]`, `_pick_pool_photo(keywords: list[str], exclude_filenames: set[str], posts_history: list[dict]) -> str | None`

- [ ] **Step 1: Write the failing tests**

Add to `scripts/test_generate_captions.py`. First, add `from datetime import datetime` to the existing `from datetime import date` import line at the top of the file (change it to `from datetime import date, datetime`). Then add:

```python
def test_photo_last_used_returns_most_recent_date_per_filename():
    rows = [
        {**store.blank_row(), "date": "2026-06-01", "photos": "a.jpg"},
        {**store.blank_row(), "date": "2026-06-08", "photos": "a.jpg, b.jpg"},
    ]
    last_used = gc._photo_last_used(rows)
    assert last_used["a.jpg"] == "2026-06-08"
    assert last_used["b.jpg"] == "2026-06-08"


def test_pick_pool_photo_prefers_never_used_photo(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "bingo_old.jpg").write_bytes(b"x")
    (tmp_path / "bingo_new.jpg").write_bytes(b"x")
    posts_history = [{**store.blank_row(), "date": "2026-06-01", "photos": "bingo_old.jpg"}]
    pick = gc._pick_pool_photo(["bingo"], exclude_filenames=set(), posts_history=posts_history)
    assert pick == "bingo_new.jpg"


def test_pick_pool_photo_picks_oldest_last_used_when_all_used_photos(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "bingo_a.jpg").write_bytes(b"x")
    (tmp_path / "bingo_b.jpg").write_bytes(b"x")
    posts_history = [
        {**store.blank_row(), "date": "2026-06-01", "photos": "bingo_a.jpg"},
        {**store.blank_row(), "date": "2026-06-08", "photos": "bingo_b.jpg"},
    ]
    pick = gc._pick_pool_photo(["bingo"], exclude_filenames=set(), posts_history=posts_history)
    assert pick == "bingo_a.jpg"  # used longest ago wins


def test_pick_pool_photo_breaks_never_used_ties_toward_newest_capture_time(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "bingo_a.jpg").write_bytes(b"x")
    (tmp_path / "bingo_b.jpg").write_bytes(b"x")

    def fake_capture_time(path):
        return datetime(2026, 1, 1) if path.endswith("bingo_a.jpg") else datetime(2026, 6, 1)

    monkeypatch.setattr(classify_photos, "read_capture_time", fake_capture_time)
    pick = gc._pick_pool_photo(["bingo"], exclude_filenames=set(), posts_history=[])
    assert pick == "bingo_b.jpg"


def test_pick_pool_photo_excludes_the_events_own_default_photo(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "Bingo_default_art.jpg").write_bytes(b"x")
    pick = gc._pick_pool_photo(["bingo"], exclude_filenames={"Bingo_default_art.jpg"}, posts_history=[])
    assert pick is None


def test_pick_pool_photo_returns_none_when_no_candidates(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    pick = gc._pick_pool_photo(["bingo"], exclude_filenames=set(), posts_history=[])
    assert pick is None


def test_pick_pool_photo_excludes_video_files(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "bingo_clip.mp4").write_bytes(b"x")
    pick = gc._pick_pool_photo(["bingo"], exclude_filenames=set(), posts_history=[])
    assert pick is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_generate_captions.py -v -k "pick_pool_photo or photo_last_used"`
Expected: FAIL with `AttributeError: module 'generate_captions' has no attribute '_pick_pool_photo'` (and `_photo_last_used`)

- [ ] **Step 3: Implement the LRU engine**

In `scripts/generate_captions.py`, add this block after `find_deal_photo` (after line 105, before `def render_generated_images`):

```python
def _photo_last_used(rows):
    """filename -> most recent 'date' value (YYYY-MM-DD) it appeared in any
    row's photos column, across all given rows. Absent if never used."""
    last_used = {}
    for r in rows:
        d = r.get("date") or ""
        if not d:
            continue
        for name in (r.get("photos") or "").split(","):
            name = name.strip()
            if not name:
                continue
            if name not in last_used or d > last_used[name]:
                last_used[name] = d
    return last_used


def _pool_candidates(keywords, exclude_filenames, posts_history):
    """Every eligible photo in config.PHOTOS_DIR whose filename contains any
    of `keywords` (case-insensitive substring), excluding anything in
    exclude_filenames and any video file, paired with when it was last used
    (None if never). Returns a list of (filename, last_used_date_or_None)."""
    last_used = _photo_last_used(posts_history)
    candidates = []
    for filename in list_photos():
        if filename in exclude_filenames:
            continue
        if filename.lower().endswith(classify_photos.VIDEO_EXTENSIONS):
            continue
        stem = os.path.splitext(filename)[0].lower()
        if not any(kw.lower() in stem for kw in keywords):
            continue
        candidates.append((filename, last_used.get(filename)))
    return candidates


def _pick_pool_photo(keywords, exclude_filenames, posts_history):
    """None if no eligible candidate. Otherwise the filename to use this
    run: a never-used candidate always wins (ties toward newest real photo
    capture time); otherwise whichever was used longest ago wins. No photo
    is ever permanently excluded -- once everything has had a turn, the
    LRU rule naturally starts the cycle over."""
    candidates = _pool_candidates(keywords, exclude_filenames, posts_history)
    if not candidates:
        return None
    never_used = [f for f, last in candidates if last is None]
    if never_used:
        never_used.sort(
            key=lambda f: classify_photos.read_capture_time(
                os.path.join(config.PHOTOS_DIR, f)) or datetime.min,
            reverse=True)
        return never_used[0]
    used = [(f, last) for f, last in candidates if last is not None]
    used.sort(key=lambda pair: pair[1])
    return used[0][0]
```

This requires `datetime` (not just `date`/`timedelta`) from the `datetime` module. Update the existing import line near the top of `scripts/generate_captions.py`:

```python
from datetime import datetime, timedelta
```

(It's currently `from datetime import datetime, timedelta` already — confirm this import already covers `datetime`; if the file only imports `timedelta`, add `datetime` to it.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_generate_captions.py -v -k "pick_pool_photo or photo_last_used"`
Expected: PASS (all tests)

- [ ] **Step 5: Run the full test suite to check for regressions**

Run: `cd scripts && python -m pytest -q`
Expected: all tests pass, no regressions

- [ ] **Step 6: Commit**

```bash
git add scripts/generate_captions.py scripts/test_generate_captions.py
git commit -m "Add shared LRU pool-selection engine for event/food photo pools"
```

---

### Task 3: Wire the event photo pool into `find_photo()`

**Files:**
- Modify: `scripts/generate_captions.py:71-92` (`find_photo`) and the two call sites in `main()` (today post ~line 296, teaser post ~line 311)
- Test: `scripts/test_generate_captions.py`

**Interfaces:**
- Consumes: `_pick_pool_photo` (Task 2), `config.EVENT_PHOTO_KEYWORDS`
- Produces: `find_photo(post_date_str, slug, want_teaser, default_photo, event=None, posts_history=None) -> str`

- [ ] **Step 1: Write the failing tests**

Add to `scripts/test_generate_captions.py`:

```python
def test_find_photo_dated_match_still_wins_over_pool(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "2026-07-13_bingo.jpg").write_bytes(b"x")
    (tmp_path / "party_bingo.jpg").write_bytes(b"x")
    photo = gc.find_photo("2026-07-13", "bingo", want_teaser=False,
                          default_photo="Bingo_default_art.jpg",
                          event="Bingo Night", posts_history=[])
    assert photo == "2026-07-13_bingo.jpg"


def test_find_photo_falls_through_to_pool_when_no_dated_match(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "party_bingo.jpg").write_bytes(b"x")
    photo = gc.find_photo("2026-07-13", "bingo", want_teaser=False,
                          default_photo="Bingo_default_art.jpg",
                          event="Bingo Night", posts_history=[])
    assert photo == "party_bingo.jpg"


def test_find_photo_falls_back_to_default_when_pool_empty(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    photo = gc.find_photo("2026-07-13", "bingo", want_teaser=False,
                          default_photo="Bingo_default_art.jpg",
                          event="Bingo Night", posts_history=[])
    assert photo == "Bingo_default_art.jpg"


def test_find_photo_without_event_keeps_old_behavior(monkeypatch, tmp_path):
    """One-off/campaign callers don't pass event/posts_history -- must
    behave exactly as before (no pool tier attempted)."""
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "party_bingo.jpg").write_bytes(b"x")
    photo = gc.find_photo("2026-07-13", "bingo", want_teaser=False,
                          default_photo="Bingo_default_art.jpg")
    assert photo == "Bingo_default_art.jpg"


def test_main_uses_pool_photo_for_recurring_event_when_no_dated_photo(tmp_path, monkeypatch):
    run_date = date(2026, 5, 31)  # a Sunday; Monday 2026-06-01 is Bingo Night
    monkeypatch.setattr(gc, "today_local", lambda: run_date)
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "party_bingo.jpg").write_bytes(b"x")

    monkeypatch.setattr(store, "load_posts", lambda: [])
    monkeypatch.setattr(store, "load_recurring", lambda: [
        {"day_of_week": "Monday", "event": "Bingo Night",
         "key_details": "details", "default_photos": "Bingo_default_art.jpg",
         "platforms": "both"},
    ])
    written = []
    monkeypatch.setattr(store, "write_posts", lambda rows: written.extend(rows))
    monkeypatch.setattr(store, "log", lambda message: None)
    monkeypatch.setattr(build_preview, "write_preview", lambda rows: "")
    monkeypatch.setattr(classify_photos, "classify_new_photos", lambda *a, **k: [])
    monkeypatch.setattr(gc, "render_generated_images", lambda rows: None)

    gc.main()

    bingo_today = [r for r in written
                  if r["event"] == "Bingo Night" and r["post_type"] == "today"]
    assert len(bingo_today) == 1
    assert bingo_today[0]["photos"] == "party_bingo.jpg"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_generate_captions.py -v -k "find_photo or pool_photo_for_recurring"`
Expected: FAIL (`find_photo() got an unexpected keyword argument 'event'`)

- [ ] **Step 3: Add the pool tier to `find_photo()`**

Replace the existing `find_photo` function (lines 71-92 of `scripts/generate_captions.py`) with:

```python
def find_photo(post_date_str, slug, want_teaser, default_photo, event=None, posts_history=None):
    """Pick the right photo filename for a post.

    Preference order:
      today post:   {date}_{slug}[_art]  ->  pool photo (event keyword, LRU)  ->  default_photo
      teaser/remind {date}_{slug}_teaser[_art]  ->  {date}_{slug}[_art]  ->  pool  ->  default
    Returns a filename (not a full path). Never returns empty if a default exists.

    `event`/`posts_history` are optional -- one-off/campaign callers that
    don't pass them get the exact pre-pool behavior (dated match or
    default), since this feature is scoped to the six recurring events.
    """
    files = list_photos()
    dated_base, dated_teaser = None, None
    for f in files:
        stem = os.path.splitext(f)[0].lower()
        tokens = stem.split("_")
        if post_date_str not in stem or slug not in stem:
            continue
        if "teaser" in tokens:
            dated_teaser = dated_teaser or f
        else:
            dated_base = dated_base or f
    if want_teaser and dated_teaser:
        return dated_teaser
    if dated_base:
        return dated_base
    if event and posts_history is not None:
        keywords = config.EVENT_PHOTO_KEYWORDS.get(event)
        if keywords:
            pool_pick = _pick_pool_photo(keywords, exclude_filenames={default_photo},
                                         posts_history=posts_history)
            if pool_pick:
                return pool_pick
    return default_photo
```

- [ ] **Step 4: Wire the real call sites in `main()`**

In `scripts/generate_captions.py`'s `main()`, update the today-post call (around line 296):

```python
            photo = find_photo(dstr, slug, want_teaser=False, default_photo=default_photo,
                               event=event, posts_history=posts + generated)
```

And the teaser-post call (around line 311):

```python
            photo = find_photo(dstr, slug, want_teaser=True, default_photo=default_photo,
                               event=event, posts_history=posts + generated)
```

Leave the campaign-expansion `find_photo` call (around line 243) unchanged — it's out of scope per the Global Constraints.

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_generate_captions.py -v`
Expected: PASS (all tests)

- [ ] **Step 6: Run the full test suite to check for regressions**

Run: `cd scripts && python -m pytest -q`
Expected: all tests pass, no regressions

- [ ] **Step 7: Commit**

```bash
git add scripts/generate_captions.py scripts/test_generate_captions.py
git commit -m "Wire event photo pool into find_photo() for recurring events"
```

---

### Task 4: Food photo second slide (with pizza's occasional-day rotation)

**Files:**
- Modify: `scripts/generate_captions.py` (new `find_food_photo` function + wiring in `main()`'s today-post block, around line 294-306)
- Test: `scripts/test_generate_captions.py`

**Interfaces:**
- Consumes: `_pick_pool_photo` (Task 2), `config.FOOD_PHOTO_KEYWORDS`, `config.OCCASIONAL_FOOD_KEYWORDS`, `config.RECURRING_DAYS`, `dow_name` (already defined in this file)
- Produces: `find_food_photo(event: str, event_date: date, run_date: date, posts_history: list[dict]) -> str | None`

- [ ] **Step 1: Write the failing tests**

Add to `scripts/test_generate_captions.py`:

```python
def test_find_food_photo_attaches_mapped_food_photo(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "weds_taco.jpg").write_bytes(b"x")
    run_date = date(2026, 5, 31)  # Sunday
    event_date = date(2026, 6, 3)  # Wednesday
    pick = gc.find_food_photo("Tacos + Poker Club", event_date, run_date, posts_history=[])
    assert pick == "weds_taco.jpg"


def test_find_food_photo_returns_none_when_event_has_no_mapped_food(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    run_date = date(2026, 5, 31)
    pick = gc.find_food_photo("Karaoke Night", date(2026, 6, 5), run_date, posts_history=[])
    assert pick is None


def test_find_food_photo_gates_occasional_keyword_to_one_day_per_week(monkeypatch, tmp_path):
    """pizza is served every day, so it must not attach on every event's
    'today' post -- only on the one day per week the rotation lands on."""
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "fresh_pizza.jpg").write_bytes(b"x")
    run_date = date(2026, 5, 31)  # Sunday
    chosen_day = config.RECURRING_DAYS[run_date.isocalendar()[1] % len(config.RECURRING_DAYS)]
    other_day = next(d for d in config.RECURRING_DAYS if d != chosen_day)
    day_dates = {
        "Monday": date(2026, 6, 1), "Tuesday": date(2026, 6, 2),
        "Wednesday": date(2026, 6, 3), "Thursday": date(2026, 6, 4),
        "Friday": date(2026, 6, 5), "Saturday": date(2026, 6, 6),
    }
    event_by_day = {
        "Monday": "Bingo Night", "Tuesday": "Pickleball Open Play",
        "Wednesday": "Tacos + Poker Club", "Thursday": "Ladies Night + Line Dancing",
        "Friday": "Karaoke Night", "Saturday": "Pool Night",
    }
    chosen_pick = gc.find_food_photo(event_by_day[chosen_day], day_dates[chosen_day],
                                     run_date, posts_history=[])
    other_pick = gc.find_food_photo(event_by_day[other_day], day_dates[other_day],
                                    run_date, posts_history=[])
    assert chosen_pick == "fresh_pizza.jpg"
    assert other_pick is None


def test_main_attaches_food_photo_as_second_slide_for_recurring_event(tmp_path, monkeypatch):
    run_date = date(2026, 5, 31)  # Sunday; Wednesday 2026-06-03 is Tacos + Poker Club
    monkeypatch.setattr(gc, "today_local", lambda: run_date)
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "2026-06-03_poker.jpg").write_bytes(b"x")  # exact dated match, main photo
    (tmp_path / "weds_taco.jpg").write_bytes(b"x")          # food second slide

    monkeypatch.setattr(store, "load_posts", lambda: [])
    monkeypatch.setattr(store, "load_recurring", lambda: [
        {"day_of_week": "Wednesday", "event": "Tacos + Poker Club",
         "key_details": "details", "default_photos": "Poker_default_art.jpg",
         "platforms": "both"},
    ])
    written = []
    monkeypatch.setattr(store, "write_posts", lambda rows: written.extend(rows))
    monkeypatch.setattr(store, "log", lambda message: None)
    monkeypatch.setattr(build_preview, "write_preview", lambda rows: "")
    monkeypatch.setattr(classify_photos, "classify_new_photos", lambda *a, **k: [])
    monkeypatch.setattr(gc, "render_generated_images", lambda rows: None)

    gc.main()

    taco_today = [r for r in written
                 if r["event"] == "Tacos + Poker Club" and r["post_type"] == "today"]
    assert len(taco_today) == 1
    assert taco_today[0]["photos"] == "2026-06-03_poker.jpg, weds_taco.jpg"


def test_main_never_attaches_food_photo_to_teaser(tmp_path, monkeypatch):
    run_date = date(2026, 5, 31)  # Sunday; Wednesday 2026-06-03 is Tacos + Poker Club
    monkeypatch.setattr(gc, "today_local", lambda: run_date)
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "weds_taco.jpg").write_bytes(b"x")

    monkeypatch.setattr(store, "load_posts", lambda: [])
    monkeypatch.setattr(store, "load_recurring", lambda: [
        {"day_of_week": "Wednesday", "event": "Tacos + Poker Club",
         "key_details": "details", "default_photos": "Poker_default_art.jpg",
         "platforms": "both"},
    ])
    written = []
    monkeypatch.setattr(store, "write_posts", lambda rows: written.extend(rows))
    monkeypatch.setattr(store, "log", lambda message: None)
    monkeypatch.setattr(build_preview, "write_preview", lambda rows: "")
    monkeypatch.setattr(classify_photos, "classify_new_photos", lambda *a, **k: [])
    monkeypatch.setattr(gc, "render_generated_images", lambda rows: None)

    gc.main()

    taco_teaser = [r for r in written
                  if r["event"] == "Tacos + Poker Club" and r["post_type"] == "teaser"]
    assert len(taco_teaser) == 1
    assert "," not in taco_teaser[0]["photos"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_generate_captions.py -v -k "find_food_photo or food_photo_as_second_slide or never_attaches_food"`
Expected: FAIL with `AttributeError: module 'generate_captions' has no attribute 'find_food_photo'`

- [ ] **Step 3: Implement `find_food_photo`**

In `scripts/generate_captions.py`, add this function right after `find_photo` (after the function added/modified in Task 3, before `find_deal_photo`):

```python
def find_food_photo(event, event_date, run_date, posts_history):
    """Return a filename to attach as a second photo on this recurring
    event's 'today' post, or None. Independent LRU rotation from the event
    photo pool -- never blocks or delays the main post.

    'Occasional' keywords (config.OCCASIONAL_FOOD_KEYWORDS, e.g. pizza --
    served every day at the bar) only attach on one deterministically
    rotating day per week (based on the run's ISO week number), so they
    don't show up on every single post just because they're always
    technically available.
    """
    for keyword, events in config.FOOD_PHOTO_KEYWORDS.items():
        if event not in events:
            continue
        if keyword in config.OCCASIONAL_FOOD_KEYWORDS:
            chosen_day = config.RECURRING_DAYS[run_date.isocalendar()[1] % len(config.RECURRING_DAYS)]
            if dow_name(event_date) != chosen_day:
                continue
        pick = _pick_pool_photo([keyword], exclude_filenames=set(), posts_history=posts_history)
        if pick:
            return pick
    return None
```

- [ ] **Step 4: Wire it into `main()`'s today-post block**

In `scripts/generate_captions.py`'s `main()`, the today-post block (around lines 294-306) currently reads:

```python
        # today post (event day)
        if (dstr, event, "today") not in existing:
            photo = find_photo(dstr, slug, want_teaser=False, default_photo=default_photo,
                               event=event, posts_history=posts + generated)
            enhance = suggest_enhance(event, details, is_promo=bool(one))
            row = build_row(d, d, event, details, platforms, "today",
                            photo, enhance, owner_time=owner_time,
                            avoid_examples=store.recent_captions_for_event(posts, event, limit=4))
            if one:
                # Repurpose the owner's original row into this today post
                # (no orphan pending row left behind).
                one.update(row)
            else:
                generated.append(row)
```

Change it to attach a food photo for genuine recurring events only (`not one`), after `row` is built:

```python
        # today post (event day)
        if (dstr, event, "today") not in existing:
            photo = find_photo(dstr, slug, want_teaser=False, default_photo=default_photo,
                               event=event, posts_history=posts + generated)
            enhance = suggest_enhance(event, details, is_promo=bool(one))
            row = build_row(d, d, event, details, platforms, "today",
                            photo, enhance, owner_time=owner_time,
                            avoid_examples=store.recent_captions_for_event(posts, event, limit=4))
            if not one:
                food_photo = find_food_photo(event, d, run_date, posts + generated)
                if food_photo:
                    row["photos"] = f"{row['photos']}, {food_photo}"
            if one:
                # Repurpose the owner's original row into this today post
                # (no orphan pending row left behind).
                one.update(row)
            else:
                generated.append(row)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_generate_captions.py -v`
Expected: PASS (all tests)

- [ ] **Step 6: Run the full test suite to check for regressions**

Run: `cd scripts && python -m pytest -q`
Expected: all tests pass, no regressions

- [ ] **Step 7: Commit**

```bash
git add scripts/generate_captions.py scripts/test_generate_captions.py
git commit -m "Add food photo second-slide with pizza's occasional-day rotation"
```

---

### Task 5: Show the second photo in the preview page

**Files:**
- Modify: `scripts/build_preview.py:18-46` (CSS + `_card_html`)
- Test: `scripts/test_build_preview.py`

**Interfaces:**
- Consumes: `row["photos"]` (comma-separated filenames, already present in every row)
- Produces: `_card_html(row: dict) -> str` (unchanged signature, new behavior for rows with 2+ photos)

- [ ] **Step 1: Write the failing tests**

Add to `scripts/test_build_preview.py`:

```python
def test_build_preview_renders_additional_photos_beyond_the_first():
    row = _row(event="Tacos + Poker Club", fb_caption="x", ig_caption="y",
              scheduled_time="2026-07-15 11:00",
              generated_image="photos/_generated/main.png",
              photos="2026-07-15_poker.jpg, weds_taco.jpg")
    html_out = build_preview.build_preview([row])
    assert "../photos/_generated/main.png" in html_out
    assert "../photos/weds_taco.jpg" in html_out


def test_build_preview_one_photo_row_unchanged():
    row = _row(event="Bingo Night", fb_caption="x", ig_caption="y",
              scheduled_time="2026-07-13 11:00",
              generated_image="photos/_generated/main.png",
              photos="2026-07-13_bingo.jpg")
    html_out = build_preview.build_preview([row])
    assert html_out.count("<img") == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_build_preview.py -v -k "additional_photos or one_photo_row_unchanged"`
Expected: FAIL (`assert "../photos/weds_taco.jpg" in html_out` fails -- the second photo isn't rendered yet)

- [ ] **Step 3: Update the CSS and `_card_html`**

In `scripts/build_preview.py`, update the `CSS` constant (lines 18-28) to add rules for the new elements:

```python
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
```

Then replace `_card_html` (lines 31-46) with:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_build_preview.py -v`
Expected: PASS (all tests)

- [ ] **Step 5: Run the full test suite to check for regressions**

Run: `cd scripts && python -m pytest -q`
Expected: all tests pass, no regressions

- [ ] **Step 6: Commit**

```bash
git add scripts/build_preview.py scripts/test_build_preview.py
git commit -m "Show additional (food) photos in the weekly preview page"
```

---

### Task 6: Documentation + end-to-end verification

**Files:**
- Modify: `HOW-TO-USE-WEEKLY.md`
- No new test file -- this task is verification + documentation only.

- [ ] **Step 1: Run the full test suite one final time**

Run: `cd scripts && python -m pytest -q`
Expected: all tests pass (should be the full suite from before this plan, plus every test added in Tasks 1-5)

- [ ] **Step 2: Local smoke test of the real pipeline**

Run: `cd scripts && python generate_captions.py`
Expected: exits cleanly, prints a "Sunday job done" line (no `ANTHROPIC_API_KEY` is set locally, so captions fall back to templates -- that's expected and fine, this step is only checking the pool/food-photo wiring doesn't crash the real entry point against the real `photos/`/`recurring_events.csv`).

Then check `git status` / `git diff` for `posts.csv`, `status.log`, `photo_classifications.json`, and anything under `photos/_generated/` or `preview/` -- **revert all of these** (`git checkout -- posts.csv status.log photo_classifications.json` and `git clean` any new generated files) so this smoke test doesn't pollute real tracked data, matching the project's existing convention for local dry runs.

- [ ] **Step 3: Update the naming guide in `HOW-TO-USE-WEEKLY.md`**

In the "During the week" section, find the block that currently reads (added earlier this session):

```
*Tied to a specific night's event:* name it `{date}_{event keyword}[.jpg/.png]`:
```

Add a new paragraph immediately after the existing "special one-off event" line and before the "*Not tied to a specific dated event*" block, documenting the new no-date pool behavior:

```markdown
*Have a photo but don't know (or don't care) which specific date it'll get
used on?* Just include the event keyword in the filename with **no date at
all** (e.g. `party_bingo.jpg`, `saturday_pool_game.jpg`). It automatically
enters that event's rotation pool and gets used on some future week whenever
there's no exact dated match to prefer -- no need to plan ahead. A photo is
never permanently used up: the system just avoids repeating the same one
back-to-back, picking whichever eligible photo hasn't been used in the
longest time.

**Food photos** (no date needed, same rotation logic) ride along as a
second photo on the day that food is actually served, without replacing the
event's own photo:

| Keyword | Attaches to |
|---|---|
| `hotdog` | Monday (Bingo) and Tuesday (Pickleball) |
| `taco`, `nachos`, `quesadilla` | Wednesday (Tacos + Poker Club) |
| `breakfastburrito` | Saturday (Pool Night) |
| `pizza` | Any day -- pizza's on the menu every day, so it only actually shows up on one rotating day per week rather than every single post |
```

- [ ] **Step 4: Commit**

```bash
git add HOW-TO-USE-WEEKLY.md
git commit -m "Document the event/food photo pool naming convention"
```
