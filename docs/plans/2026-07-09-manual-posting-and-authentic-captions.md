# Manual-Posting Workflow, Authentic Captions, Real-Photo Flyers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Retire all Meta API involvement (posting AND the voice-anchor read call) in favor of a Sunday review-and-manually-schedule workflow, fix the caption generator's formulaic "AI voice," guarantee 2-3 posts/day at reasoned times, add real-photo flyer template variety + deal-photo compositing + new evergreen content types, and generate a static visual preview page so the owner can scan the week at a glance.

**Architecture:** The Sunday GitHub Action (`generate_captions.py`) becomes the only automated job. It now also renders each row's flyer image (via `process_photos.py`, extended with template variety + deal compositing), computes a guaranteed per-day post cadence (new `scheduling.py`), optionally pulls a weather blurb for one evergreen content type (new `weather.py`), and writes a static HTML snapshot (new `build_preview.py`) alongside `posts.csv`. All Meta Graph API code (`meta_client.py`, `post_to_meta.py`, the hourly workflow) is deleted outright.

**Tech Stack:** Python 3.11, pytest, PIL/Pillow (image compositing), `requests` (Open-Meteo only, no key), GitHub Actions.

## Global Constraints

- No AI image-generation API — all visuals are real-photo compositing only (PIL), per the owner's authenticity requirement.
- Zero Meta developer-console involvement of any kind — no tokens, no App Review, no `META_*` secrets anywhere.
- Every new external call (weather) must degrade gracefully to `None`/a generic fallback on any failure — never block a row from generating.
- `posts.csv` remains the single source of truth the owner edits; the new preview page is a read-only convenience view generated from it.
- Every function that can fail on bad/missing input (missing photo, malformed date, network error) must log via `store.log()` and continue — never crash the whole Sunday run over one bad row.
- Follow existing code style: plain module-level functions (no classes except `MetaError`-style exceptions), docstrings explaining *why*, `from __future__ import annotations` at the top of new modules.

---

### Task 1: Delete all Meta API involvement (posting + voice-anchor) and the hourly workflow

**Files:**
- Delete: `.github/workflows/hourly-post.yml`
- Delete: `scripts/post_to_meta.py`
- Delete: `scripts/test_post_to_meta.py`
- Delete: `scripts/meta_client.py`
- Delete: `scripts/test_meta_client.py`

**Interfaces:**
- Produces: nothing (pure deletion). Later tasks must not import `meta_client` or `post_to_meta` anywhere.

- [ ] **Step 1: Delete the five files/workflow**

```bash
git rm .github/workflows/hourly-post.yml scripts/post_to_meta.py scripts/test_post_to_meta.py scripts/meta_client.py scripts/test_meta_client.py
```

- [ ] **Step 2: Confirm nothing else references the deleted modules**

Run: `grep -rn "meta_client\|post_to_meta" --include=*.py --include=*.yml .`
Expected: no output (Task 5 will remove the remaining `generate_captions.py` references — if this grep finds hits there right now, that's expected and gets fixed in Task 5; there should be no hits anywhere else).

- [ ] **Step 3: Run the full test suite to confirm no import-time breakage from the deletion**

Run: `cd scripts && python -m pytest -x`
Expected: `test_generate_captions.py` may fail on `import meta_client` — that's fixed in Task 5. All other test files should collect and pass.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "Delete Meta API posting and voice-anchor code, retire hourly workflow"
```

---

### Task 2: Config & CSV schema updates for the new workflow

**Files:**
- Modify: `scripts/config.py`
- Modify: `scripts/store.py:56-58`

**Interfaces:**
- Produces: `config.STATUS_SCHEDULED`, `config.MIN_DAILY_POSTS`, `config.MAX_DAILY_POSTS`, `config.BONUS_POSTS_PER_WEEK`, `config.EXTRA_POST_TIME_AFTERNOON`, `config.EVERGREEN_LABELS`, `config.FEATURED_DRINKS`, `config.TRAIL_HIGHLIGHTS`, `"generated_image"` in `config.POSTS_COLUMNS`.
- Consumes: nothing new (pure config).

- [ ] **Step 1: Replace the status block in `scripts/config.py`**

Replace:
```python
# ---------------------------------------------------------------------------
# Valid values for the status column, documented for the owner.
# pending      -> owner just added a one-off; Sunday job will process it
# needs_review -> system generated it; owner should review/approve
# approved     -> owner OK'd it; hourly job will post when its time passes
# skip         -> suppress this post entirely
# posted       -> already published (set by the system)
# campaign_source -> a promote_from row that was expanded into reminders; ignore
# ---------------------------------------------------------------------------
STATUS_PENDING = "pending"
STATUS_NEEDS_REVIEW = "needs_review"
STATUS_APPROVED = "approved"
STATUS_SKIP = "skip"
STATUS_POSTED = "posted"
STATUS_CAMPAIGN_SOURCE = "campaign_source"

# The exact column order for posts.csv. Keep in sync with the header row.
POSTS_COLUMNS = [
    "date", "time", "photos", "event", "key_details", "platforms",
    "promote_from", "post_type", "enhance", "fb_caption", "ig_caption",
    "scheduled_time", "status",
]

# Long-lived Meta tokens last ~60 days. Warn when fewer than this many days
# are estimated to remain so the owner refreshes before it expires.
TOKEN_WARN_DAYS = 10
```

With:
```python
# ---------------------------------------------------------------------------
# Valid values for the status column, documented for the owner.
# pending      -> owner just added a one-off; Sunday job will process it
# needs_review -> system generated it; owner should review/edit it
# skip         -> suppress this post entirely
# scheduled    -> owner manually pasted this into FB/IG's native scheduler
#                 (bookkeeping only -- nothing in the system reads this back)
# posted       -> legacy value from the old auto-posting job; still
#                 recognized as "already used" history, nothing sets it now
# campaign_source -> a promote_from row that was expanded into reminders; ignore
# ---------------------------------------------------------------------------
STATUS_PENDING = "pending"
STATUS_NEEDS_REVIEW = "needs_review"
STATUS_SKIP = "skip"
STATUS_SCHEDULED = "scheduled"
STATUS_POSTED = "posted"
STATUS_CAMPAIGN_SOURCE = "campaign_source"

# The exact column order for posts.csv. Keep in sync with the header row.
POSTS_COLUMNS = [
    "date", "time", "photos", "event", "key_details", "platforms",
    "promote_from", "post_type", "enhance", "fb_caption", "ig_caption",
    "scheduled_time", "generated_image", "status",
]
```

- [ ] **Step 2: Replace the extra-post-type block in `scripts/config.py`**

Replace:
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

With:
```python
# ---------------------------------------------------------------------------
# Extra post types (carousel / vibe / spotlight / evergreen) -- fill content
# used to guarantee the daily posting cadence below.
# ---------------------------------------------------------------------------
EXTRA_POST_TYPES = ("carousel", "vibe", "spotlight")

# Guaranteed posting cadence: every day of the week should reach at least
# MIN_DAILY_POSTS; BONUS_POSTS_PER_WEEK days additionally get bumped up to
# MAX_DAILY_POSTS for the "occasionally 3" the owner asked for. Never forced
# past what real/evergreen material actually supports that week.
MIN_DAILY_POSTS = 2
MAX_DAILY_POSTS = 3
BONUS_POSTS_PER_WEEK = 3

EXTRA_POST_TIME_MORNING = "11:30"
EXTRA_POST_TIME_AFTERNOON = "14:30"   # primary slot for the occasional 3rd post
EXTRA_POST_TIME_EVENING = "19:30"

# Evergreen content angles rotated through for "vibe"-kind classified photos
# (no dedicated event tie-in) so the fill content doesn't repeat the same
# label every week. "Weather Vibes" pulls a live forecast blurb (weather.py);
# all four reuse whatever real vibe-classified photo is available.
EVERGREEN_LABELS = ["Behind The Scenes", "Wisconsin Spotlight",
                    "Course & Trail Feature", "Weather Vibes"]

# Rotated by date so the same drink/trail isn't featured every single week.
# Edit these to match the bar's actual current menu/trails whenever they change.
FEATURED_DRINKS = [
    "our seasonal Wisconsin Marzen lager",
    "a crisp Wisconsin-brewed IPA",
    "our local Door County cherry wine",
    "a Wisconsin craft hard seltzer",
    "our small-batch Wisconsin cider",
]
TRAIL_HIGHLIGHTS = [
    "the front nine disc golf holes",
    "the back nine disc golf holes",
    "the north hiking loop through the woods",
    "the sunset overlook trail",
    "the beginner-friendly nature loop",
]
```

- [ ] **Step 3: Update `DEFAULT_TIMES` "today" values to the formalized late-morning slot**

Replace:
```python
DEFAULT_TIMES = {
    ("Monday", "today"): "12:00",
    ("Tuesday", "today"): "12:00",
    ("Wednesday", "today"): "12:00",
    ("Thursday", "today"): "12:00",
    ("Friday", "today"): "12:30",
    ("Saturday", "today"): "11:00",
    ("Sunday", "today"): "12:00",   # only used if a Sunday one-off exists
```

With:
```python
DEFAULT_TIMES = {
    ("Monday", "today"): "11:00",
    ("Tuesday", "today"): "11:00",
    ("Wednesday", "today"): "11:00",
    ("Thursday", "today"): "11:00",
    ("Friday", "today"): "11:00",
    ("Saturday", "today"): "11:00",
    ("Sunday", "today"): "11:00",   # only used if a Sunday one-off exists
```

- [ ] **Step 4: Add three evergreen-specific entries to `EVENT_ANGLES` in `scripts/config.py`**

Replace:
```python
EVENT_ANGLES = {
    "Bingo Night": "Prize-reveal angle -- what are we playing for this week?",
    "Pickleball Open Play": "Challenge/competitive angle -- think you can beat the regulars?",
    "Tacos + Poker Club": "Food first, then the game -- the tacos are the hook.",
    "Disc Golf League + Ladies Night": "Calling all ladies + league leaderboard hype -- two angles, alternate or combine.",
    "Line Dancing + Karaoke Night": "'Weekend starts NOW' energy.",
    "Pool Night": "Tournament angle -- beat the bartender, win a flight.",
}
```

With:
```python
EVENT_ANGLES = {
    "Bingo Night": "Prize-reveal angle -- what are we playing for this week?",
    "Pickleball Open Play": "Challenge/competitive angle -- think you can beat the regulars?",
    "Tacos + Poker Club": "Food first, then the game -- the tacos are the hook.",
    "Disc Golf League + Ladies Night": "Calling all ladies + league leaderboard hype -- two angles, alternate or combine.",
    "Line Dancing + Karaoke Night": "'Weekend starts NOW' energy.",
    "Pool Night": "Tournament angle -- beat the bartender, win a flight.",
    "Wisconsin Spotlight": "Feature the specific drink named in key_details -- pure appreciation, no CTA pressure.",
    "Course & Trail Feature": "Feature the specific trail/course detail named in key_details -- outdoorsy pride angle.",
    "Weather Vibes": "Tie the specific weather named in key_details to disc golf/hiking/patio appeal.",
}
```

- [ ] **Step 5: Update the repetition-guard status filter in `scripts/store.py`**

Replace (line 56-58):
```python
    matches = [r for r in rows
               if r["event"] == event and r["status"] in (config.STATUS_APPROVED, config.STATUS_POSTED)
               and r["ig_caption"]]
```

With:
```python
    matches = [r for r in rows
               if r["event"] == event and r["status"] in (config.STATUS_SCHEDULED, config.STATUS_POSTED)
               and r["ig_caption"]]
```

- [ ] **Step 6: Run the existing store test to confirm nothing broke**

Run: `cd scripts && python -m pytest test_store.py -v`
Expected: PASS (test_store.py doesn't reference `STATUS_APPROVED`, so this should be unaffected — if it fails, check for a stale reference and update it to `STATUS_SCHEDULED`).

- [ ] **Step 7: Commit**

```bash
git add scripts/config.py scripts/store.py
git commit -m "Update config/schema for manual posting: new status, cadence constants, evergreen content"
```

---

### Task 3: `scheduling.py` — pure fill-target computation for the guaranteed cadence

**Files:**
- Create: `scripts/scheduling.py`
- Test: `scripts/test_scheduling.py`

**Interfaces:**
- Consumes: `config.MIN_DAILY_POSTS`, `config.MAX_DAILY_POSTS`, `config.BONUS_POSTS_PER_WEEK`, `config.EXTRA_POST_TIME_MORNING/AFTERNOON/EVENING`.
- Produces: `scheduling.compute_fill_targets(counts: dict[str, int], week_dates: list[str], min_posts=None, max_posts=None, bonus_budget=None) -> dict[str, int]` and `scheduling.time_for_fill_slot(index: int) -> str`. Consumed by Task 6's `build_extra_rows`.

- [ ] **Step 1: Write the failing tests**

Create `scripts/test_scheduling.py`:
```python
import config
import scheduling


def test_compute_fill_targets_fills_empty_days_to_minimum():
    week_dates = ["2026-06-01", "2026-06-02", "2026-06-03"]
    counts = {}
    targets = scheduling.compute_fill_targets(counts, week_dates, min_posts=2,
                                              max_posts=3, bonus_budget=0)
    assert targets == {"2026-06-01": 2, "2026-06-02": 2, "2026-06-03": 2}


def test_compute_fill_targets_only_tops_up_short_days():
    week_dates = ["2026-06-01", "2026-06-02"]
    counts = {"2026-06-01": 2, "2026-06-02": 1}
    targets = scheduling.compute_fill_targets(counts, week_dates, min_posts=2,
                                              max_posts=3, bonus_budget=0)
    assert targets == {"2026-06-01": 0, "2026-06-02": 1}


def test_compute_fill_targets_never_exceeds_max_posts_via_bonus():
    week_dates = ["2026-06-01", "2026-06-02"]
    counts = {"2026-06-01": 2, "2026-06-02": 2}
    targets = scheduling.compute_fill_targets(counts, week_dates, min_posts=2,
                                              max_posts=3, bonus_budget=5)
    # Only 1 bonus slot exists per day (2 -> 3), even though budget is 5.
    assert targets == {"2026-06-01": 1, "2026-06-02": 1}


def test_compute_fill_targets_spends_bonus_budget_on_most_headroom_first():
    week_dates = ["2026-06-01", "2026-06-02", "2026-06-03"]
    counts = {"2026-06-01": 2, "2026-06-02": 2, "2026-06-03": 2}
    targets = scheduling.compute_fill_targets(counts, week_dates, min_posts=2,
                                              max_posts=3, bonus_budget=1)
    assert sum(targets.values()) == 1
    assert targets["2026-06-01"] == 1  # earliest date wins the tiebreak


def test_compute_fill_targets_uses_config_defaults_when_not_overridden():
    week_dates = ["2026-06-01"]
    targets = scheduling.compute_fill_targets({}, week_dates)
    assert targets["2026-06-01"] == config.MIN_DAILY_POSTS


def test_time_for_fill_slot_rotates_afternoon_first():
    assert scheduling.time_for_fill_slot(0) == config.EXTRA_POST_TIME_AFTERNOON
    assert scheduling.time_for_fill_slot(1) == config.EXTRA_POST_TIME_MORNING
    assert scheduling.time_for_fill_slot(2) == config.EXTRA_POST_TIME_EVENING
    assert scheduling.time_for_fill_slot(3) == config.EXTRA_POST_TIME_AFTERNOON
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_scheduling.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scheduling'`

- [ ] **Step 3: Write `scripts/scheduling.py`**

```python
"""
scheduling.py - Pure fill-target math for the guaranteed daily posting
cadence (config.MIN_DAILY_POSTS minimum, occasional bonus up to
config.MAX_DAILY_POSTS). No I/O, no side effects -- generate_captions.py's
build_extra_rows() consumes this to decide how many fill posts each day of
the upcoming week needs and where to slot them in time.
"""

from __future__ import annotations

import config


def compute_fill_targets(counts: dict, week_dates: list,
                         min_posts: int = None, max_posts: int = None,
                         bonus_budget: int = None) -> dict:
    """Return {date: extra_posts_needed} for every date in week_dates.

    First pass: top up any day below min_posts (using its existing baseline
    count from `counts`) to exactly min_posts.
    Second pass: spend bonus_budget bonus slots on the days with the most
    remaining headroom below max_posts, earliest date breaking ties, so a
    handful of days occasionally get a 3rd post instead of every day.
    """
    min_posts = config.MIN_DAILY_POSTS if min_posts is None else min_posts
    max_posts = config.MAX_DAILY_POSTS if max_posts is None else max_posts
    bonus_budget = config.BONUS_POSTS_PER_WEEK if bonus_budget is None else bonus_budget

    targets = {}
    for d in week_dates:
        baseline = counts.get(d, 0)
        targets[d] = max(0, min(min_posts, max_posts) - baseline)

    def headroom(d):
        filled = counts.get(d, 0) + targets[d]
        return max_posts - filled

    remaining_budget = bonus_budget
    while remaining_budget > 0:
        eligible = [d for d in week_dates if headroom(d) > 0]
        if not eligible:
            break
        eligible.sort(key=lambda d: (-headroom(d), week_dates.index(d)))
        chosen = eligible[0]
        targets[chosen] += 1
        remaining_budget -= 1

    return targets


def time_for_fill_slot(index: int) -> str:
    """Clock time for the Nth (0-indexed) fill post scheduled on one day.

    Afternoon first -- that's the documented "occasional 3rd post" slot --
    then morning, then evening, repeating if a single day somehow needs more
    than three (never happens under config.MAX_DAILY_POSTS, but keeps this
    function total rather than partial).
    """
    slots = [config.EXTRA_POST_TIME_AFTERNOON, config.EXTRA_POST_TIME_MORNING,
             config.EXTRA_POST_TIME_EVENING]
    return slots[index % len(slots)]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_scheduling.py -v`
Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/scheduling.py scripts/test_scheduling.py
git commit -m "Add scheduling.py: pure fill-target math for guaranteed daily cadence"
```

---

### Task 4: `weather.py` — free forecast lookup for the "Weather Vibes" evergreen post

**Files:**
- Create: `scripts/weather.py`
- Test: `scripts/test_weather.py`

**Interfaces:**
- Consumes: `config.BUSINESS["latitude"/"longitude"]`.
- Produces: `weather.forecast_blurb(for_date: datetime.date) -> str | None`. Consumed by Task 6's `build_extra_rows`.

- [ ] **Step 1: Write the failing tests**

Create `scripts/test_weather.py`:
```python
from datetime import date
from unittest.mock import Mock, patch

import weather


def _fake_response(weathercode, high_f):
    resp = Mock()
    resp.raise_for_status = Mock()
    resp.json.return_value = {
        "daily": {"weathercode": [weathercode], "temperature_2m_max": [high_f]}
    }
    return resp


def test_forecast_blurb_formats_known_weather_code():
    with patch("weather.requests.get", return_value=_fake_response(0, 74.2)):
        result = weather.forecast_blurb(date(2026, 7, 14))
    assert result == "clear skies and 74F"


def test_forecast_blurb_falls_back_to_generic_phrase_for_unknown_code():
    with patch("weather.requests.get", return_value=_fake_response(999, 60.0)):
        result = weather.forecast_blurb(date(2026, 7, 14))
    assert result == "good weather and 60F"


def test_forecast_blurb_returns_none_on_network_failure():
    with patch("weather.requests.get", side_effect=Exception("timeout")):
        result = weather.forecast_blurb(date(2026, 7, 14))
    assert result is None


def test_forecast_blurb_returns_none_on_malformed_response():
    resp = Mock()
    resp.raise_for_status = Mock()
    resp.json.return_value = {"daily": {}}
    with patch("weather.requests.get", return_value=resp):
        result = weather.forecast_blurb(date(2026, 7, 14))
    assert result is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_weather.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'weather'`

- [ ] **Step 3: Write `scripts/weather.py`**

```python
"""
weather.py - Free, no-key weather lookup for the "Weather Vibes" evergreen
post (see config.EVERGREEN_LABELS). Uses Open-Meteo's public forecast API --
no signup, no API key, no cost. Any failure degrades to None so a
weather-tied post can gracefully fall back to a generic vibe post instead of
blocking Sunday generation.
"""

from __future__ import annotations

from datetime import date

import requests

import config

WEATHER_CODES = {
    0: "clear skies", 1: "mostly clear", 2: "partly cloudy", 3: "overcast",
    45: "foggy", 48: "foggy", 51: "light drizzle", 53: "drizzle",
    55: "heavy drizzle", 61: "light rain", 63: "rain", 65: "heavy rain",
    71: "light snow", 73: "snow", 75: "heavy snow", 80: "rain showers",
    81: "rain showers", 82: "heavy rain showers", 95: "thunderstorms",
}


def forecast_blurb(for_date: date) -> str | None:
    """Return a short human phrase like 'sunny and 74F' for for_date, or
    None on any failure (network error, bad response, unsupported date)."""
    try:
        b = config.BUSINESS
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": b["latitude"],
                "longitude": b["longitude"],
                "daily": "weathercode,temperature_2m_max",
                "temperature_unit": "fahrenheit",
                "timezone": "America/Chicago",
                "start_date": for_date.isoformat(),
                "end_date": for_date.isoformat(),
            },
            timeout=15,
        )
        resp.raise_for_status()
        daily = resp.json()["daily"]
        code = daily["weathercode"][0]
        high = round(daily["temperature_2m_max"][0])
        desc = WEATHER_CODES.get(code, "good weather")
        return f"{desc} and {high}F"
    except Exception as exc:
        print(f"[weather] forecast lookup failed for {for_date}: {exc}")
        return None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_weather.py -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add scripts/weather.py scripts/test_weather.py
git commit -m "Add weather.py: free Open-Meteo lookup for the Weather Vibes evergreen post"
```

---

### Task 5: Remove voice-anchor plumbing and rework the caption prompt for authenticity

**Files:**
- Modify: `scripts/anthropic_client.py`
- Modify: `scripts/generate_captions.py` (imports, `main()`, `build_row()`, `generate_captions_for()`)
- Modify: `scripts/test_anthropic_client.py`
- Modify: `scripts/test_generate_captions.py`

**Interfaces:**
- Produces: `anthropic_client.generate_captions(event, key_details, day_of_week, post_type, days_until=None, avoid_examples=None)` (voice_examples parameter removed).
- Consumes: nothing new.

- [ ] **Step 1: Update the failing/changed tests in `scripts/test_anthropic_client.py`**

Replace the whole file with:
```python
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


def test_user_prompt_includes_avoid_examples():
    text = ac._user_prompt("Bingo Night", "details", "Monday", "today", None, None,
                           avoid_examples=["Old hook line"])
    assert "Old hook line" in text
    assert "do not" in text.lower() or "avoid" in text.lower()


def test_user_prompt_has_no_voice_examples_parameter():
    import inspect
    params = inspect.signature(ac._user_prompt).parameters
    assert "voice_examples" not in params


def test_system_prompt_instructs_varying_the_opening_move():
    text = ac._system_prompt()
    assert "vary" in text.lower() and "opening" in text.lower()


def test_system_prompt_instructs_rotating_share_mechanism():
    text = ac._system_prompt()
    assert "tag-a-friend" in text.lower() or "tag a friend" in text.lower()
```

- [ ] **Step 2: Run to verify the new tests fail**

Run: `cd scripts && python -m pytest test_anthropic_client.py -v`
Expected: FAIL on `test_user_prompt_has_no_voice_examples_parameter`,
`test_system_prompt_instructs_varying_the_opening_move`,
`test_system_prompt_instructs_rotating_share_mechanism`, and the
`test_user_prompt_includes_avoid_examples` call (old signature still takes
`voice_examples` positionally, so keyword-only `avoid_examples=` will
currently raise `TypeError` since the parameter order differs) — some may
also pass by luck; the goal is confirming they fail for the *right* reason
(old prompt/signature), not that every single one fails.

- [ ] **Step 3: Rewrite `_system_prompt()` and `_user_prompt()` in `scripts/anthropic_client.py`**

Replace:
```python
def _system_prompt() -> str:
    b = config.BUSINESS
    return f"""You write social captions for {b['name']}, {b['region']}'s most unique bar \
(bar + disc golf + hiking trails on 35 acres in {b['city']}, WI). Tagline: "{b['tagline']}".

VOICE (follow exactly):
- Energetic, community-first, outdoorsy, Wisconsin-proud, fun without being try-hard. \
Feels like a friend texting you about a cool spot -- never corporate.
- HOOK FIRST LINE, ALWAYS. The opening line must stop the scroll -- lead with the most \
surprising, specific, or urgency-driving detail. "Bingo's back" not "Hey everyone, don't forget".
- Wisconsin identity is the superpower -- SAY IT. Every beer, wine, seltzer is 100% \
Wisconsin-made, zero outside brands. That's rare and worth naming.
- WISCONSIN-ONLY IS NON-NEGOTIABLE. Never name-drop or reference any non-Wisconsin brand, \
chain, or product. Packers/Brewers/Green Bay references are welcome where natural.
- Promote the uniqueness: bar + disc golf + hiking, unlike anywhere else.
- Events need FOMO, not generic "join us" energy -- something you'd regret missing.
- Weave memberships in naturally and often (not a hard sell, just the obvious move): {config.MEMBERSHIPS}
- ONE clear foot-traffic CTA per post (a specific reason to come in), plus a rotated \
engagement bait (comment-bait "tag your ___", share-bait "send this to ___", or save-bait for \
info-dense posts). Specific CTAs only -- never a vague "come visit".
- No filler. Every word earns its place. Fragmented sentences over full paragraphs.
- Casual and warm, but keep spelling and grammar standard. No dropped word endings or \
slang contractions ("ya" for "you", "gonna", "y'all", etc.) -- friendly doesn't mean informal \
spelling. Write like a real person texting, not a caricature of one.
- On-brand emojis only, used naturally never spammed: {' '.join(config.EMOJIS)}
- Never post anything implying hours outside the real open hours.

FACEBOOK vs INSTAGRAM must be genuinely DIFFERENT posts, not repurposed copies:
- Facebook: conversational, event-focused, 80-150 words, full event details. NO hashtags.
- Instagram: punchy, ~100-150 characters above the fold, clean and short. NO hashtags in the \
caption (they are posted separately as the first comment).

Return ONLY valid JSON: {{"fb_caption": "...", "ig_caption": "..."}} -- no other text."""
```

With:
```python
def _system_prompt() -> str:
    b = config.BUSINESS
    return f"""You write social captions for {b['name']}, {b['region']}'s most unique bar \
(bar + disc golf + hiking trails on 35 acres in {b['city']}, WI). Tagline: "{b['tagline']}".

VOICE:
- Energetic, community-first, outdoorsy, Wisconsin-proud, fun without being try-hard. Feels \
like a friend texting you about a cool spot -- never corporate, never a copywriting checklist. \
No two posts should read like they came from the same template.
- The event info for that day (what, when, key details) must always be accurate and always \
included -- that's the one thing that never varies.
- VARY THE OPENING MOVE. Don't default to a rhetorical question every time -- mix in a flat \
statement, a fragment, an aside, an exclamation. Don't repeat the same opening style two posts \
in a row.
- Wisconsin identity is a real asset -- every beer, wine, seltzer is 100% Wisconsin-made, zero \
outside brands -- but don't recite it as a fixed line every post. Work it in naturally, and \
skip it entirely sometimes, the way a real person would.
- WISCONSIN-ONLY IS NON-NEGOTIABLE. Never name-drop or reference any non-Wisconsin brand, \
chain, or product. Packers/Brewers/Green Bay references are welcome where natural.
- Promote the uniqueness: bar + disc golf + hiking, unlike anywhere else.
- Events need FOMO, not generic "join us" energy -- something you'd regret missing.
- Membership plugs ({config.MEMBERSHIPS}) should show up often -- the owner wants them frequent \
-- but phrase them differently every time, like a person casually mentioning it mid-conversation, \
never the same sentence twice.
- DRIVE SHARING AND REACH ON EVERY POST -- this matters more than any single line. Every \
caption needs something that spreads it beyond people who already follow the page. Rotate the \
mechanism instead of reusing "tag your ___" every time -- mix across: tag-a-friend, a \
comment-bait question, a save-worthy specific detail, a genuinely quotable line, a "share this \
if" line. Pick whichever fits this specific post best, and pick a different one than recent \
posts used for this event.
- No filler. Every word earns its place. Fragmented sentences over full paragraphs.
- Casual and warm, but keep spelling and grammar standard. No dropped word endings or slang \
contractions ("ya" for "you", "gonna", "y'all", etc.) -- friendly doesn't mean informal \
spelling. Write like a real person texting, not a caricature of one.
- On-brand emojis only, used naturally never spammed: {' '.join(config.EMOJIS)}
- Never post anything implying hours outside the real open hours.

FACEBOOK vs INSTAGRAM must be genuinely DIFFERENT posts, not repurposed copies:
- Facebook: conversational, event-focused, 80-150 words, full event details. NO hashtags.
- Instagram: punchy, ~100-150 characters above the fold, clean and short. NO hashtags in the \
caption (they are posted separately as the first comment).

Return ONLY valid JSON: {{"fb_caption": "...", "ig_caption": "..."}} -- no other text."""
```

Replace:
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

With:
```python
def _user_prompt(event, key_details, day_of_week, post_type, days_until,
                 angle, avoid_examples):
    parts = [
        f"EVENT: {event}",
        f"DAY: {day_of_week}",
        f"KEY DETAILS (work these facts in accurately): {key_details}",
        f"REAL OPEN HOURS that day: {config.HOURS.get(day_of_week, 'see website')}",
    ]
    if angle:
        parts.append(f"CONTENT ANGLE for this event: {angle}")
    parts.append(_framing(post_type, days_until))
    if avoid_examples:
        joined = "\n---\n".join(avoid_examples[:4])
        parts.append("DO NOT REPEAT -- captions already used recently for this exact event, in "
                     "wording AND in structure/opening-move/engagement-mechanism. Write "
                     f"something with a genuinely different hook, phrasing, and structure:\n{joined}")
    parts.append('Write the two captions now. Return ONLY the JSON object.')
    return "\n\n".join(parts)
```

- [ ] **Step 4: Update `generate_captions()` in `scripts/anthropic_client.py` to drop `voice_examples`**

Replace:
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
```

With:
```python
def generate_captions(event, key_details, day_of_week, post_type,
                      days_until=None, avoid_examples=None):
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
                                        avoid_examples or []),
            }],
        )
```

- [ ] **Step 5: Run to verify anthropic_client tests pass**

Run: `cd scripts && python -m pytest test_anthropic_client.py -v`
Expected: PASS (9 tests)

- [ ] **Step 6: Remove `meta_client`/`voice_examples` plumbing from `scripts/generate_captions.py`**

Replace the import block:
```python
import classify_photos
import config
import meta_client
import store
from anthropic_client import generate_captions
```

With:
```python
import classify_photos
import config
import store
from anthropic_client import generate_captions
```

Replace `build_row()`'s signature and call:
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
```

With:
```python
def build_row(event_date, post_date, event, key_details, platforms,
              post_type, photo, enhance, owner_time="", days_until=None,
              avoid_examples=None):
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
                             avoid_examples=avoid_examples)
```

In `main()`, remove the `voice_examples` line and every `voice_examples=voice_examples,` keyword argument passed to `build_row(...)` calls (there are three: the campaign-expansion loop, the one-off "today" post, and the "teaser" post) and to `build_extra_rows(...)`:

Replace:
```python
def main():
    run_date = today_local()
    voice_examples = meta_client.recent_page_posts(limit=6)
    recurring = load_recurring_by_day()
```

With:
```python
def main():
    run_date = today_local()
    recurring = load_recurring_by_day()
```

Then remove every `voice_examples=voice_examples,` line that follows (in the three `build_row(...)` calls inside `main()`) — each of those calls keeps its other keyword arguments (`days_until=...` and/or `avoid_examples=...`) unchanged, just without the `voice_examples` line. `build_extra_rows(classified, posts + generated, run_date, voice_examples=voice_examples, avoid_examples_by_event=avoid_examples_by_event)` becomes `build_extra_rows(classified, posts + generated, run_date, avoid_examples_by_event=avoid_examples_by_event)` (this call site gets fully rewritten again in Task 6, so this is an intermediate correctness step).

Replace `generate_captions_for()`:
```python
def generate_captions_for(event, key_details, day_of_week, post_type,
                          voice_examples=None, avoid_examples=None):
    """Thin wrapper so build_extra_rows doesn't need to import anthropic_client
    directly -- keeps the caption-generation entry point in one place."""
    from anthropic_client import generate_captions as _gen
    return _gen(event, key_details, day_of_week, post_type,
               voice_examples=voice_examples, avoid_examples=avoid_examples)
```

With:
```python
def generate_captions_for(event, key_details, day_of_week, post_type,
                          avoid_examples=None):
    """Thin wrapper so build_extra_rows doesn't need to import anthropic_client
    directly -- keeps the caption-generation entry point in one place."""
    from anthropic_client import generate_captions as _gen
    return _gen(event, key_details, day_of_week, post_type,
               avoid_examples=avoid_examples)
```

Inside `build_extra_rows()`'s existing `try_schedule()` helper (this whole function is fully rewritten in Task 6, but to keep this task independently green, also strip its `voice_examples` parameter and the `voice_examples=voice_examples,` line passed to `generate_captions_for(...)` for now):

Replace:
```python
def build_extra_rows(classified, existing_rows, run_date, voice_examples=None,
                     avoid_examples_by_event=None):
```

With:
```python
def build_extra_rows(classified, existing_rows, run_date,
                     avoid_examples_by_event=None):
```

And remove the `voice_examples=voice_examples,` line from the `generate_captions_for(...)` call inside `try_schedule()`.

- [ ] **Step 7: Update `scripts/test_generate_captions.py`**

Remove `import meta_client` from the top of the file (it currently sits between `import config` and `import store`).

In `test_main_gives_vibe_spotlight_posts_the_repetition_guard`, remove the line
`monkeypatch.setattr(meta_client, "recent_page_posts", lambda limit=6: [])` entirely, and update `spy_generate_captions_for`'s signature to drop `voice_examples=None`:

Replace:
```python
    def spy_generate_captions_for(event, key_details, day_of_week, post_type,
                                   voice_examples=None, avoid_examples=None):
        if event == "Behind The Scenes":
            captured["avoid_examples"] = avoid_examples
        return real_generate_captions_for(event, key_details, day_of_week, post_type,
                                          voice_examples=voice_examples,
                                          avoid_examples=avoid_examples)
```

With:
```python
    def spy_generate_captions_for(event, key_details, day_of_week, post_type,
                                   avoid_examples=None):
        if event == "Behind The Scenes":
            captured["avoid_examples"] = avoid_examples
        return real_generate_captions_for(event, key_details, day_of_week, post_type,
                                          avoid_examples=avoid_examples)
```

- [ ] **Step 8: Run the full suite to confirm this task leaves everything green**

Run: `cd scripts && python -m pytest -x`
Expected: PASS (Task 6 will further rewrite `build_extra_rows` and its tests, but everything must pass with this task's intermediate state first)

- [ ] **Step 9: Commit**

```bash
git add scripts/anthropic_client.py scripts/generate_captions.py scripts/test_anthropic_client.py scripts/test_generate_captions.py
git commit -m "Remove Meta voice-anchor plumbing; rework caption prompt for shareable, varied, human-sounding captions"
```

---

### Task 6: Rewrite `build_extra_rows` for guaranteed cadence + evergreen content rotation

**Files:**
- Modify: `scripts/generate_captions.py` (imports, `build_extra_rows()`)
- Modify: `scripts/test_generate_captions.py`

**Interfaces:**
- Consumes: `scheduling.compute_fill_targets`, `scheduling.time_for_fill_slot`, `weather.forecast_blurb`, `config.EVERGREEN_LABELS`, `config.FEATURED_DRINKS`, `config.TRAIL_HIGHLIGHTS`, `config.MAX_DAILY_POSTS`.
- Produces: `generate_captions.build_extra_rows(classified, existing_rows, run_date, avoid_examples_by_event=None) -> list[dict]` (same name, new internals and guarantees).

- [ ] **Step 1: Update the two now-invalid assertions in `scripts/test_generate_captions.py`**

Replace:
```python
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

With:
```python
def test_build_extra_rows_never_exceeds_max_daily_posts():
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
    assert all(c <= config.MAX_DAILY_POSTS for c in counts.values())


def test_build_extra_rows_tops_up_a_zero_post_day_to_the_minimum():
    run_date = date(2026, 5, 31)  # a Sunday
    classified = [{"filename": f"vibe{i}.jpg", "match": None, "kind": "vibe", "confidence": "high"}
                  for i in range(4)]
    existing_rows = [_scheduled_row("2026-06-01 12:00"), _scheduled_row("2026-06-01 19:00")]
    rows = gc.build_extra_rows(classified, existing_rows, run_date)
    counts = gc.day_post_counts(existing_rows + rows)
    # Tuesday (2026-06-02) starts at 0 -- it must reach at least MIN_DAILY_POSTS
    # once enough fill material (4 vibe photos) exists.
    assert counts.get("2026-06-02", 0) >= config.MIN_DAILY_POSTS


def test_build_extra_rows_rotates_evergreen_labels_for_vibe_photos():
    run_date = date(2026, 5, 31)  # a Sunday
    classified = [{"filename": f"vibe{i}.jpg", "match": None, "kind": "vibe", "confidence": "high"}
                  for i in range(4)]
    rows = gc.build_extra_rows(classified, [], run_date)
    events = {r["event"] for r in rows if r["post_type"] == "vibe"}
    # With 4 vibe photos and 4 evergreen labels available, expect more than
    # one distinct label to show up rather than "Behind The Scenes" x4.
    assert len(events) > 1
    assert events <= set(config.EVERGREEN_LABELS)
```

- [ ] **Step 2: Run to verify the new tests fail against the current (pre-rewrite) `build_extra_rows`**

Run: `cd scripts && python -m pytest test_generate_captions.py -v`
Expected: `test_build_extra_rows_never_exceeds_max_daily_posts` likely passes by
coincidence (old cap of 1 extra/day is still `<= MAX_DAILY_POSTS`), but
`test_build_extra_rows_tops_up_a_zero_post_day_to_the_minimum` and
`test_build_extra_rows_rotates_evergreen_labels_for_vibe_photos` FAIL — the
old code only ever assigns the fixed "Behind The Scenes" label and caps
total extra posts at `config.MAX_EXTRA_POSTS_PER_WEEK` (4), which no longer
exists as an attribute after Task 2 deleted it, so this run should actually
error with `AttributeError: module 'config' has no attribute
'MAX_EXTRA_POSTS_PER_WEEK'` inside the old `try_schedule` — confirming the
rewrite in this task is required.

- [ ] **Step 3: Add the new imports to `scripts/generate_captions.py`**

Replace:
```python
import classify_photos
import config
import store
from anthropic_client import generate_captions
```

With:
```python
import classify_photos
import config
import scheduling
import store
import weather
from anthropic_client import generate_captions
```

- [ ] **Step 4: Replace `build_extra_rows()` (and its `try_schedule` helper) in `scripts/generate_captions.py`**

Replace the entire existing function:
```python
def build_extra_rows(classified, existing_rows, run_date,
                     avoid_examples_by_event=None):
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
        if preferred_date is not None and preferred_date in candidates:
            target = preferred_date
        else:
            target = quietest_day(candidates, counts)
        row = store.blank_row()
        row["date"] = target
        row["photos"] = ", ".join(filenames)
        row["event"] = event
        row["key_details"] = key_details
        row["platforms"] = "both"
        row["post_type"] = kind
        row["enhance"] = "none"
        row["scheduled_time"] = f"{target} {time_slot}"
        avoid_examples = (avoid_examples_by_event or {}).get(event)
        caps = generate_captions_for(event, key_details, dow_name(parse_date(target)), kind,
                                     avoid_examples=avoid_examples)
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
        try_schedule(kind, event_label, "", [item["filename"]], None, slot)

    return extra_rows
```

With:
```python
def _weather_vibes_key_details(target_date_str):
    blurb = weather.forecast_blurb(parse_date(target_date_str))
    return f"Weather: {blurb}" if blurb else ""


def build_extra_rows(classified, existing_rows, run_date,
                     avoid_examples_by_event=None):
    """Build carousel/vibe/spotlight/evergreen rows so every day of the
    upcoming week reaches config.MIN_DAILY_POSTS, with config.BONUS_POSTS_PER_WEEK
    days occasionally bumped to config.MAX_DAILY_POSTS. Never forces a post
    past what real/evergreen material actually supports that week -- thin
    material just means the guarantee isn't fully hit."""
    counts = dict(day_post_counts(existing_rows))
    week_dates = [(run_date + timedelta(days=i)).strftime(DATE_FMT) for i in range(1, 8)]
    targets = scheduling.compute_fill_targets(counts, week_dates)
    fills_placed = defaultdict(int)
    extra_rows = []

    def remaining_target_days():
        return [d for d in week_dates if targets.get(d, 0) > 0]

    def schedule_row(kind, event, key_details_fn, filenames, preferred_date):
        eligible = remaining_target_days()
        if not eligible:
            return False
        if preferred_date is not None and preferred_date in eligible:
            target = preferred_date
        else:
            target = quietest_day(eligible, counts)
        key_details = key_details_fn(target) if callable(key_details_fn) else key_details_fn
        time_slot = scheduling.time_for_fill_slot(fills_placed[target])
        row = store.blank_row()
        row["date"] = target
        row["photos"] = ", ".join(filenames)
        row["event"] = event
        row["key_details"] = key_details
        row["platforms"] = "both"
        row["post_type"] = kind
        row["enhance"] = "none"
        row["scheduled_time"] = f"{target} {time_slot}"
        avoid_examples = (avoid_examples_by_event or {}).get(event)
        caps = generate_captions_for(event, key_details, dow_name(parse_date(target)), kind,
                                     avoid_examples=avoid_examples)
        row["fb_caption"] = caps["fb_caption"]
        row["ig_caption"] = caps["ig_caption"]
        row["status"] = config.STATUS_NEEDS_REVIEW
        extra_rows.append(row)
        counts[target] = counts.get(target, 0) + 1
        targets[target] -= 1
        fills_placed[target] += 1
        return True

    # Carousels: real-photo event recaps, scheduled the day after the event.
    for group in group_carousel_candidates(classified):
        times = [t for t in group["capture_times"] if t]
        event_day = times[0].date() if times else run_date
        recap_date = (event_day + timedelta(days=1)).strftime(DATE_FMT)
        schedule_row("carousel", group["event"], "A look back at last night.",
                     group["filenames"], recap_date)

    # Vibe/spotlight singles: real classified photos. Spotlight always reads
    # as a community shoutout; vibe photos rotate through the evergreen
    # content angles for variety (Weather Vibes needs no dedicated photo
    # subject of its own -- any vibe shot works as its backdrop).
    singles = [i for i in classified if i["kind"] in ("vibe", "spotlight") and not i["match"]]
    vibe_idx = 0
    for item in singles:
        if not remaining_target_days():
            break
        if item["kind"] == "spotlight":
            schedule_row("spotlight", "Community Spotlight", "", [item["filename"]], None)
            continue
        label = config.EVERGREEN_LABELS[vibe_idx % len(config.EVERGREEN_LABELS)]
        vibe_idx += 1
        if label == "Wisconsin Spotlight":
            drinks = config.FEATURED_DRINKS
            key_details = f"Featuring {drinks[run_date.toordinal() % len(drinks)]}"
        elif label == "Course & Trail Feature":
            trails = config.TRAIL_HIGHLIGHTS
            key_details = f"Featuring {trails[run_date.toordinal() % len(trails)]}"
        elif label == "Weather Vibes":
            key_details = _weather_vibes_key_details
        else:
            key_details = ""
        schedule_row("vibe", label, key_details, [item["filename"]], None)

    return extra_rows
```

- [ ] **Step 5: Run the full test_generate_captions.py suite**

Run: `cd scripts && python -m pytest test_generate_captions.py -v`
Expected: PASS (all tests, including the three new/updated ones from Step 1
and the pre-existing `test_vibe_spotlight_lands_on_genuinely_quietest_day_not_tomorrow`,
which should still pass unchanged since `quietest_day` tiebreak behavior for
a single-candidate scenario is preserved by the rewrite)

- [ ] **Step 6: Run the full suite**

Run: `cd scripts && python -m pytest -x`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add scripts/generate_captions.py scripts/test_generate_captions.py
git commit -m "Rewrite build_extra_rows: guarantee 2-3 posts/day with evergreen content rotation"
```

---

### Task 7: Flyer template variety in `process_photos.py`

**Files:**
- Modify: `scripts/process_photos.py`
- Create: `scripts/test_process_photos.py`

**Interfaces:**
- Produces: `process_photos.choose_template(event: str, date_str: str) -> str`, `process_photos._build_flyer_minimal(...)`, `process_photos._build_flyer_poster(...)`, `process_photos.FLYER_TEMPLATES`. `process()` gains a `date_str=""` parameter (defaults to `""`, backward compatible for any caller that omits it, though Task 9 will always pass it).
- Consumes: existing `_fit_cover`, `_auto_polish`, `_headline_font`, `_font`, `_wrap`, `_hex`, `config.COLORS`.

- [ ] **Step 1: Write the failing tests**

Create `scripts/test_process_photos.py`:
```python
from PIL import Image

import config
import process_photos as pp


def _dummy_photo(color=(120, 150, 90), size=(800, 600)):
    return Image.new("RGB", size, color)


def test_choose_template_is_deterministic_for_same_input():
    a = pp.choose_template("Bingo Night", "2026-07-14")
    b = pp.choose_template("Bingo Night", "2026-07-14")
    assert a == b


def test_choose_template_varies_across_dates():
    templates = {pp.choose_template("Bingo Night", f"2026-07-{d:02d}") for d in range(1, 29)}
    assert len(templates) > 1
    assert templates <= set(pp.FLYER_TEMPLATES)


def test_build_flyer_minimal_returns_correct_size():
    result = pp._build_flyer_minimal(_dummy_photo(), "Bingo Night", "10 rounds, free to play",
                                     "Monday", (1080, 1080))
    assert result.size == (1080, 1080)


def test_build_flyer_poster_returns_correct_size():
    result = pp._build_flyer_poster(_dummy_photo(), "Pool Night", "beat the bartender",
                                    "Saturday", (1080, 1080))
    assert result.size == (1080, 1080)


def test_process_text_overlay_mode_picks_a_valid_template(tmp_path):
    src = tmp_path / "2026-07-14_bingo.jpg"
    _dummy_photo().save(src)
    out = tmp_path / "out.png"
    result_path = pp.process(str(src), str(out), "ig_feed", "text_overlay",
                             event="Bingo Night", key_details="10 rounds",
                             day_of_week="Monday", date_str="2026-07-14")
    assert result_path == str(out)
    result = Image.open(out)
    assert result.size == config.DIMENSIONS["ig_feed"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_process_photos.py -v`
Expected: FAIL with `AttributeError: module 'process_photos' has no attribute 'choose_template'` (and similar for the other new names)

- [ ] **Step 3: Add `hashlib` import, template list, selector, and two new builder functions to `scripts/process_photos.py`**

Replace the import block:
```python
from __future__ import annotations

import os
import urllib.request

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

import config
```

With:
```python
from __future__ import annotations

import hashlib
import os
import urllib.request

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

import config
```

Add this block directly after the existing `_build_flyer(...)` function (before `def process(...)`):
```python
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
    size_px = int(H * 0.09)
    while size_px > int(H * 0.045):
        hf = _headline_font(event, size_px)
        lines = _wrap(draw, event.upper(), hf, max_w)
        if len(lines) <= 2:
            break
        size_px -= 6
    hf = _headline_font(event, size_px)
    lines = _wrap(draw, event.upper(), hf, max_w)
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
    size_px = int(H * 0.11)
    while size_px > int(H * 0.05):
        hf = _headline_font(event, size_px)
        lines = _wrap(draw, event.upper(), hf, max_w)
        if len(lines) <= 2:
            break
        size_px -= 6
    hf = _headline_font(event, size_px)
    lines = _wrap(draw, event.upper(), hf, max_w)
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
```

- [ ] **Step 4: Wire template selection into `process()`**

Replace:
```python
def process(input_path, out_path, platform_key, enhance_col,
            event="", key_details="", day_of_week=""):
    """Process one image for one platform and save it to out_path.

    Returns out_path on success. Never raises on cosmetic issues -- worst case it
    still writes a correctly-sized image so a post is never blocked by a font.
    """
    ensure_fonts()
    size = config.DIMENSIONS[platform_key]
    mode = resolve_mode(input_path, enhance_col)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    img = Image.open(input_path)

    if mode == "premade_art":
        # Post exactly as supplied -- only fit to platform dims, no other edits.
        result = _fit_contain(img.convert("RGB"), size)
    elif mode == "none":
        result = _fit_cover(_auto_polish(img), size)
    elif mode == "text_overlay":
        result = _build_flyer(img, event, key_details, day_of_week, size)
    elif mode == "logo":
        result = _add_logo(_fit_cover(_auto_polish(img), size))
    elif mode == "both":
        flyer = _build_flyer(img, event, key_details, day_of_week, size)
        result = _add_logo(flyer)
    else:
        result = _fit_cover(_auto_polish(img), size)

    result.save(out_path, quality=92)
    return out_path
```

With:
```python
def process(input_path, out_path, platform_key, enhance_col,
            event="", key_details="", day_of_week="", date_str=""):
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

    result.save(out_path, quality=92)
    return out_path
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_process_photos.py -v`
Expected: PASS (5 tests)

- [ ] **Step 6: Run the full suite**

Run: `cd scripts && python -m pytest -x`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add scripts/process_photos.py scripts/test_process_photos.py
git commit -m "Add flyer template variety (badge/minimal/poster) with deterministic rotation"
```

---

### Task 8: Real-photo deal compositing in `process_photos.py`

**Files:**
- Modify: `scripts/process_photos.py`
- Modify: `scripts/test_process_photos.py`

**Interfaces:**
- Produces: `process_photos._add_deal_callout(img, deal_photo_path, key_details) -> Image.Image`. `process()` gains a `deal_photo_path=None` parameter.
- Consumes: `_fit_cover`, `_font`, `_hex`, `config.COLORS`.

- [ ] **Step 1: Write the failing tests**

Append to `scripts/test_process_photos.py`:
```python
def test_add_deal_callout_returns_same_size_image(tmp_path):
    base = _dummy_photo(size=(1080, 1080))
    deal_photo = tmp_path / "deal.jpg"
    _dummy_photo(color=(200, 50, 50)).save(deal_photo)
    result = pp._add_deal_callout(base, str(deal_photo), "$2 off Spotted Cow")
    assert result.size == base.size


def test_add_deal_callout_changes_pixels_near_the_badge(tmp_path):
    base = _dummy_photo(size=(1080, 1080), color=(0, 0, 0))
    deal_photo = tmp_path / "deal.jpg"
    _dummy_photo(color=(255, 255, 255)).save(deal_photo)
    result = pp._add_deal_callout(base, str(deal_photo), "$2 off Spotted Cow")
    # Bottom-left region should no longer be pure black once the badge lands there.
    sample = result.convert("RGB").getpixel((60, 1010))
    assert sample != (0, 0, 0)


def test_add_deal_callout_degrades_gracefully_on_missing_photo():
    base = _dummy_photo(size=(1080, 1080))
    result = pp._add_deal_callout(base, "/nonexistent/path.jpg", "$2 off Spotted Cow")
    assert result is base


def test_process_composites_deal_photo_when_provided(tmp_path):
    src = tmp_path / "2026-07-14_pickleball.jpg"
    _dummy_photo().save(src)
    deal_photo = tmp_path / "2026-07-14_pickleball_deal.jpg"
    _dummy_photo(color=(255, 255, 255)).save(deal_photo)
    out = tmp_path / "out.png"
    pp.process(str(src), str(out), "ig_feed", "text_overlay",
              event="Pickleball Open Play", key_details="$2 off Spotted Cow",
              day_of_week="Tuesday", date_str="2026-07-14",
              deal_photo_path=str(deal_photo))
    result = Image.open(out).convert("RGB")
    assert result.size == config.DIMENSIONS["ig_feed"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_process_photos.py -v`
Expected: FAIL with `AttributeError: module 'process_photos' has no attribute '_add_deal_callout'`

- [ ] **Step 3: Add `_add_deal_callout()` to `scripts/process_photos.py`**

Add this function directly after `_build_flyer_poster(...)` (before `def process(...)`):
```python
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
```

- [ ] **Step 4: Wire `deal_photo_path` into `process()`**

Replace:
```python
def process(input_path, out_path, platform_key, enhance_col,
            event="", key_details="", day_of_week="", date_str=""):
```

With:
```python
def process(input_path, out_path, platform_key, enhance_col,
            event="", key_details="", day_of_week="", date_str="",
            deal_photo_path=None):
```

Replace the final lines of `process()`:
```python
    else:
        result = _fit_cover(_auto_polish(img), size)

    result.save(out_path, quality=92)
    return out_path
```

With:
```python
    else:
        result = _fit_cover(_auto_polish(img), size)

    if deal_photo_path and mode in ("text_overlay", "both"):
        result = _add_deal_callout(result, deal_photo_path, key_details)

    result.save(out_path, quality=92)
    return out_path
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_process_photos.py -v`
Expected: PASS (9 tests)

- [ ] **Step 6: Run the full suite**

Run: `cd scripts && python -m pytest -x`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add scripts/process_photos.py scripts/test_process_photos.py
git commit -m "Add real-photo deal-callout compositing (_deal suffix), no drink-name library needed"
```

---

### Task 9: Wire flyer generation + `_deal` photo detection into the Sunday job

**Files:**
- Modify: `scripts/generate_captions.py`

**Interfaces:**
- Consumes: `process_photos.process(...)`, `process_photos.output_name(...)`, `config.GENERATED_DIR`, `config.PHOTOS_DIR`.
- Produces: `generate_captions.find_deal_photo(post_date_str, slug) -> str | None`, `generate_captions.render_generated_images(rows) -> None`. Every row gets `row["generated_image"]` populated when rendering succeeds.

- [ ] **Step 1: Write the failing test**

Add to `scripts/test_generate_captions.py`:
```python
def test_render_generated_images_sets_generated_image_and_skips_missing_photos(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    monkeypatch.setattr(config, "GENERATED_DIR", str(tmp_path / "_generated"))
    monkeypatch.setattr(config, "REPO_ROOT", str(tmp_path.parent))
    from PIL import Image
    Image.new("RGB", (800, 600), (10, 20, 30)).save(tmp_path / "2026-07-14_bingo.jpg")

    has_photo = {**store.blank_row(), "date": "2026-07-14", "photos": "2026-07-14_bingo.jpg",
                 "event": "Bingo Night", "key_details": "10 rounds", "enhance": "none"}
    missing_photo = {**store.blank_row(), "date": "2026-07-15", "photos": "nope.jpg",
                     "event": "Pool Night", "key_details": ""}
    rows = [dict(has_photo), dict(missing_photo)]

    gc.render_generated_images(rows)

    assert rows[0]["generated_image"], "expected a generated_image path for the row with a real photo"
    assert rows[1]["generated_image"] == ""


def test_find_deal_photo_matches_date_and_slug_with_deal_suffix(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "2026-07-14_pickleball_deal.jpg").write_bytes(b"fake")
    (tmp_path / "2026-07-14_pickleball.jpg").write_bytes(b"fake")
    assert gc.find_deal_photo("2026-07-14", "pickleball") == "2026-07-14_pickleball_deal.jpg"


def test_find_deal_photo_returns_none_when_absent(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "2026-07-14_pickleball.jpg").write_bytes(b"fake")
    assert gc.find_deal_photo("2026-07-14", "pickleball") is None
```

- [ ] **Step 2: Run to verify the new tests fail**

Run: `cd scripts && python -m pytest test_generate_captions.py -v`
Expected: FAIL with `AttributeError: module 'generate_captions' has no attribute 'render_generated_images'` (and `find_deal_photo`)

- [ ] **Step 3: Add `import process_photos` to `scripts/generate_captions.py`**

Replace:
```python
import classify_photos
import config
import scheduling
import store
import weather
from anthropic_client import generate_captions
```

With:
```python
import classify_photos
import config
import process_photos
import scheduling
import store
import weather
from anthropic_client import generate_captions
```

- [ ] **Step 4: Add `find_deal_photo()` directly after the existing `find_photo()` function**

```python
def find_deal_photo(post_date_str, slug):
    """The dated _deal photo for this date/event slug, if the owner dropped
    one (e.g. 2026-07-14_pickleball_deal.jpg). None if not present -- a
    missing deal photo just means no deal callout gets added, never blocks
    the post."""
    for f in list_photos():
        stem = os.path.splitext(f)[0].lower()
        tokens = stem.split("_")
        if post_date_str in stem and slug in stem and "deal" in tokens:
            return f
    return None
```

- [ ] **Step 5: Add `render_generated_images()` directly after `find_deal_photo()`**

```python
def render_generated_images(rows):
    """Render each row's flyer/photo to config.GENERATED_DIR and set
    generated_image to its repo-relative path. Never raises -- a render
    failure just leaves generated_image blank so the row still shows up for
    review with its original photo referenced in the photos column."""
    for row in rows:
        if row.get("generated_image") or not row.get("photos"):
            continue
        first_photo = row["photos"].split(",")[0].strip()
        src = os.path.join(config.PHOTOS_DIR, first_photo)
        if not os.path.isfile(src):
            continue
        try:
            event_date = parse_date(row["date"])
            slug = slug_from_event(row["event"])
            deal_photo = find_deal_photo(row["date"], slug)
            deal_path = os.path.join(config.PHOTOS_DIR, deal_photo) if deal_photo else None
            name = process_photos.output_name("post", row["event"], row["date"])
            out_path = os.path.join(config.GENERATED_DIR, name)
            process_photos.process(
                src, out_path, "ig_feed", row["enhance"],
                event=row["event"], key_details=row["key_details"],
                day_of_week=dow_name(event_date), date_str=row["date"],
                deal_photo_path=deal_path)
            row["generated_image"] = os.path.relpath(out_path, config.REPO_ROOT).replace("\\", "/")
        except Exception as exc:
            store.log(f"flyer render failed for '{row['event']}' {row['date']}: {exc} "
                      f"-- row will show its original photo instead.")
```

- [ ] **Step 6: Call `render_generated_images()` from `main()`, right before `store.write_posts(all_rows)`**

Replace:
```python
    # --- 6. Save --------------------------------------------------------------
    all_rows = posts + generated
    store.write_posts(all_rows)
```

With:
```python
    # --- 6. Render flyer images, then save -------------------------------------
    all_rows = posts + generated
    render_generated_images(all_rows)
    store.write_posts(all_rows)
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_generate_captions.py -v`
Expected: PASS

- [ ] **Step 8: Run the full suite**

Run: `cd scripts && python -m pytest -x`
Expected: PASS. If `test_main_gives_vibe_spotlight_posts_the_repetition_guard`
fails because `main()` now also calls `render_generated_images` against a
real `config.PHOTOS_DIR`/`config.GENERATED_DIR` that don't have matching
fixture photos, that's fine and expected — the function's `if not
os.path.isfile(src): continue` guard skips it silently since the test's
fake row has no real photo file on disk.

- [ ] **Step 9: Commit**

```bash
git add scripts/generate_captions.py scripts/test_generate_captions.py
git commit -m "Wire flyer generation and _deal photo detection into the Sunday job"
```

---

### Task 10: Visual weekly preview page

**Files:**
- Create: `scripts/build_preview.py`
- Create: `scripts/test_build_preview.py`
- Modify: `scripts/generate_captions.py`
- Modify: `scripts/test_generate_captions.py`

**Interfaces:**
- Produces: `build_preview.build_preview(rows: list) -> str` (HTML string), `build_preview.write_preview(rows: list) -> str` (path written, or `""` on failure).
- Consumes: `config.REPO_ROOT`.

- [ ] **Step 1: Write the failing tests**

Create `scripts/test_build_preview.py`:
```python
import build_preview
import config
import store


def _row(**overrides):
    row = {**store.blank_row(), **overrides}
    return row


def test_build_preview_includes_event_and_captions():
    rows = [_row(event="Bingo Night", fb_caption="FB text here", ig_caption="IG text here",
                scheduled_time="2026-07-13 11:00", generated_image="photos/_generated/x.png")]
    html_out = build_preview.build_preview(rows)
    assert "Bingo Night" in html_out
    assert "FB text here" in html_out
    assert "IG text here" in html_out
    assert "photos/_generated/x.png" in html_out


def test_build_preview_escapes_html_in_captions():
    rows = [_row(event="Bingo Night", fb_caption="<script>alert(1)</script>", ig_caption="ok")]
    html_out = build_preview.build_preview(rows)
    assert "<script>" not in html_out
    assert "&lt;script&gt;" in html_out


def test_build_preview_orders_by_scheduled_time():
    rows = [
        _row(event="Second", scheduled_time="2026-07-14 11:00"),
        _row(event="First", scheduled_time="2026-07-13 11:00"),
    ]
    html_out = build_preview.build_preview(rows)
    assert html_out.index("First") < html_out.index("Second")


def test_write_preview_creates_the_file(tmp_path, monkeypatch):
    monkeypatch.setattr(build_preview, "PREVIEW_DIR", str(tmp_path / "preview"))
    monkeypatch.setattr(build_preview, "PREVIEW_FILE", str(tmp_path / "preview" / "this-week.html"))
    rows = [_row(event="Bingo Night", fb_caption="x", ig_caption="y",
                scheduled_time="2026-07-13 11:00")]
    path = build_preview.write_preview(rows)
    assert path == str(tmp_path / "preview" / "this-week.html")
    assert (tmp_path / "preview" / "this-week.html").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_build_preview.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'build_preview'`

- [ ] **Step 3: Write `scripts/build_preview.py`**

```python
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
.card img { width: 260px; height: 260px; object-fit: cover; border-radius: 8px; }
.placeholder { width: 260px; height: 260px; background: #1c3450; border-radius: 8px; }
.meta { font-size: 14px; color: #F5C842; margin-bottom: 8px; }
.caption-label { font-weight: bold; color: #C8922A; margin-top: 10px; }
.caption-text { white-space: pre-wrap; }
"""


def _card_html(row: dict) -> str:
    img_rel = (row.get("generated_image") or "").replace("\\", "/")
    img_tag = (f'<img src="../{html.escape(img_rel)}" alt="post image">'
               if img_rel else '<div class="placeholder"></div>')
    return f"""
<div class="card">
  {img_tag}
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_build_preview.py -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Wire `build_preview` into `generate_captions.py`'s `main()`**

Replace:
```python
import classify_photos
import config
import process_photos
import scheduling
import store
import weather
from anthropic_client import generate_captions
```

With:
```python
import build_preview
import classify_photos
import config
import process_photos
import scheduling
import store
import weather
from anthropic_client import generate_captions
```

Replace:
```python
    # --- 6. Render flyer images, then save -------------------------------------
    all_rows = posts + generated
    render_generated_images(all_rows)
    store.write_posts(all_rows)
```

With:
```python
    # --- 6. Render flyer images, build the preview page, then save -----------
    all_rows = posts + generated
    render_generated_images(all_rows)
    week_rows = [r for r in all_rows if r["status"] == config.STATUS_NEEDS_REVIEW]
    build_preview.write_preview(week_rows)
    store.write_posts(all_rows)
```

- [ ] **Step 6: Prevent `test_main_gives_vibe_spotlight_posts_the_repetition_guard` from writing to the real repo's `preview/` folder**

In `scripts/test_generate_captions.py`, add `import build_preview` to the
top imports, and inside `test_main_gives_vibe_spotlight_posts_the_repetition_guard`
add this monkeypatch alongside the others already there:

```python
    monkeypatch.setattr(build_preview, "write_preview", lambda rows: "")
```

- [ ] **Step 7: Run the full suite**

Run: `cd scripts && python -m pytest -x`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add scripts/build_preview.py scripts/test_build_preview.py scripts/generate_captions.py scripts/test_generate_captions.py
git commit -m "Add static HTML weekly preview page (preview/this-week.html)"
```

---

### Task 11: Update the Sunday GitHub Actions workflow

**Files:**
- Modify: `.github/workflows/sunday-generate.yml`

**Interfaces:** none (CI config only).

- [ ] **Step 1: Remove the now-unused Meta secrets and commit the new generated directories**

Replace:
```yaml
      - name: Generate the week's captions
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          ANTHROPIC_MODEL: ${{ secrets.ANTHROPIC_MODEL }}   # optional override
          META_PAGE_ID: ${{ secrets.META_PAGE_ID }}
          META_PAGE_ACCESS_TOKEN: ${{ secrets.META_PAGE_ACCESS_TOKEN }}
        run: python scripts/generate_captions.py

      - name: Commit the generated posts
        run: |
          git config user.name "Backyard Brew Bot"
          git config user.email "actions@github.com"
          git add posts.csv status.log assets/fonts || true
          if ! git diff --cached --quiet; then
            git commit -m "Sunday job: generate weekly posts [skip ci]"
            git push
          else
            echo "No changes to commit."
          fi
```

With:
```yaml
      - name: Generate the week's captions
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          ANTHROPIC_MODEL: ${{ secrets.ANTHROPIC_MODEL }}   # optional override
        run: python scripts/generate_captions.py

      - name: Commit the generated posts
        run: |
          git config user.name "Backyard Brew Bot"
          git config user.email "actions@github.com"
          git add posts.csv status.log assets/fonts photos/_generated preview || true
          if ! git diff --cached --quiet; then
            git commit -m "Sunday job: generate weekly posts [skip ci]"
            git push
          else
            echo "No changes to commit."
          fi
```

- [ ] **Step 2: Validate the YAML parses**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/sunday-generate.yml'))"`
Expected: no output (valid YAML). If `yaml` isn't installed locally, instead
run `python -c "import yaml"` first to confirm, and if it's missing, visually
diff the file against the original for indentation consistency instead.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/sunday-generate.yml
git commit -m "Drop Meta secrets from Sunday workflow; commit generated images and preview page"
```

---

### Task 12: Rewrite `SETUP.md` and `HOW-TO-USE-WEEKLY.md` for the new workflow

**Files:**
- Modify: `SETUP.md`
- Modify: `HOW-TO-USE-WEEKLY.md`

**Interfaces:** none (documentation only).

- [ ] **Step 1: Replace `SETUP.md` in full**

```markdown
# Backyard Brew Social — One-Time Setup Guide

You only do this **once**. Total time: about 10 minutes. Nowhere in here do
you paste anything into a chat — your API key goes straight into GitHub's
locked "Secrets" box, which Part 2 points you to.

**The two parts:**
1. Put the folder on GitHub with GitHub Desktop
2. Get an Anthropic API key and paste it into GitHub Secrets

---

## Part 1 — GitHub Desktop (so you can drag photos, not use a website)

### 1a. Install it
1. Go to **https://desktop.github.com** and click the big **Download for Windows** button.
2. Run the downloaded `GitHubDesktopSetup.exe`. It installs and opens itself — no options to fuss with.
3. When it opens, click **Sign in to GitHub.com** and log in with your existing GitHub account.
4. It asks to "Configure Git" — just click **Continue** (your name/email are fine as-is).

### 1b. Add this folder as a repository
1. In GitHub Desktop's top-left menu: **File → Add local repository**.
2. Click **Choose…** and select this folder:
   `C:\Users\micah\OneDrive\Desktop\backyard-brew-social`
3. It'll say *"This directory does not appear to be a Git repository — Create a repository?"*
   Click the blue **create a repository** link.
4. On the next screen leave everything as-is and click **Create Repository**.

### 1c. Publish it to GitHub
1. Click the **Publish repository** button (top bar).
2. This repo doesn't post anywhere automatically anymore, so it's fine to leave
   **"Keep this code private"** checked if you'd rather it not be public.
3. Name can stay `backyard-brew-social`. Click **Publish Repository**.

Done. From now on, your normal rhythm is: drag photos into the `photos` folder,
edit the spreadsheets, then in GitHub Desktop click **Commit to main** (bottom-left)
and **Push origin** (top bar). That's how your changes reach the system.

---

## Part 2 — Get an Anthropic API key

This is what writes your captions every Sunday. No Meta/Facebook developer
setup exists anywhere in this system anymore — this is the only key you need.

1. Go to **https://console.anthropic.com** and sign up/log in.
2. **API Keys → Create Key**. Copy the key it shows you (you won't be able to
   see it again after leaving the page).
3. Add a little billing credit on the account — captions for this volume of
   posting cost roughly a few dollars a month at most.
4. In your repo on GitHub.com: **Settings** (top tab) → **Secrets and
   variables → Actions** → **New repository secret**.
5. Name: `ANTHROPIC_API_KEY`. Value: the key you copied. Click **Add secret**.

That's the entire setup. See **HOW-TO-USE-WEEKLY.md** for your simple every-week routine.
```

- [ ] **Step 2: Replace `HOW-TO-USE-WEEKLY.md` in full**

```markdown
# How To Use This Every Week (the whole job)

Once setup is done, your entire weekly involvement is **one Sunday sitting**:
drop photos during the week, review + manually schedule on Sunday, done.

---

## During the week

**Drop in this week's photos** (optional but recommended)
Drag photos into the `photos` folder in GitHub Desktop. Name them by date + event:

| You drop this | What it does |
|---|---|
| `2026-07-13_bingo.jpg` | Fresh photo for Monday's Bingo post |
| `2026-07-13_bingo_teaser.jpg` | Different photo for the night-before teaser |
| `2026-07-13_bingo_deal.jpg` | A photo of that day's featured drink deal — gets composited into a small callout badge on the flyer |
| `2026-07-13_bingo_art.png` | A finished graphic you made — posted exactly as-is, no editing |
| *(nothing)* | Falls back to the default photo — still works |

The event keyword to use in the filename is the first word the system knows:
`bingo`, `pickleball`, `poker`, `discgolf`, `friday`, `saturday`. For a special
event, just match whatever you named the photo in the `posts.csv` row.

**Add any special events** (only if you have one)
Open `posts.csv` and add ONE row for a party/guest/holiday. Fill in: `date`, `photos`,
`event`, `key_details`, `platforms`. Leave the rest blank.
- Want it promoted repeatedly leading up? Also fill **`promote_from`** with the date to
  start the hype. The system builds the whole countdown for you.
- Want to cancel one night this week? Add a row with that `date` and set `status` = `skip`.

Push it up (GitHub Desktop: **Commit to main** → **Push origin**) whenever convenient.

---

## Sunday: the ~1 hour review-and-schedule sitting

**1. Pull the week's generated content**
GitHub Desktop → **Fetch/Pull origin**. The Sunday job runs on its own and fills
in everything: captions, flyer images, and a visual preview page.

**2. Open `preview/this-week.html` in your browser**
Double-click the file (or open it from File Explorer). You'll see every post
for the week as a card: the finished image, the scheduled time, and both
captions underneath, in order. This is your at-a-glance review — no
spreadsheet-reading required for a normal week.

**3. Edit anything you want in `posts.csv`**
Only open the spreadsheet if you want to change a caption's wording or a
`scheduled_time`. Every column is already filled in for you:
- `fb_caption` / `ig_caption` — edit any wording you want, just type over it.
- `scheduled_time` — change it if you want a different time (format: exact `YYYY-MM-DD HH:MM`).
- `generated_image` — the finished flyer image for that row; this is what you'll attach.
- Don't want a post to go out? Set its `status` to `skip`.

**4. Manually schedule each post**
For each post (in the order shown in the preview page): open Facebook or
Instagram's own **"Schedule Post"** feature (in the app, or in Meta Business
Suite), paste the caption, attach the image at the path shown in
`generated_image`, and set the date/time already suggested. Repeat for each
post — with 2-3 posts/day, expect roughly 15-20 posts to schedule most weeks,
a couple minutes each.

**5. Mark it done and push**
Change that row's `status` from `needs_review` to `scheduled` (just for your
own tracking — nothing reads this back). Once you're through the list,
**Commit + Push** one more time. That's it for the week.

---

## What happens automatically (you do nothing)

- **Every Sunday**, the system generates the whole week's captions, flyer
  images (with real-photo template variety), and the visual preview page.
- **You get 2 posts a day minimum, occasionally 3** — the system fills quiet
  days with real-photo content (behind-the-scenes shots, community
  spotlights, event recaps) and evergreen content (a featured Wisconsin
  drink, a course/trail feature, or a weather-tied post), so posting is
  never sparse even on days without a scheduled event.
- **Suggested posting times** are already baked in (late-morning for the
  day's main post, afternoon for the occasional 3rd post, evening for the
  next day's teaser) — you're free to change any of them.

---

## How to know it's working

- **`status.log`** in the repo is a plain-English diary: "Sunday job done:
  generated N new post rows" means success; a "flyer render failed" line
  tells you exactly which row fell back to its plain photo and why.
- **GitHub → Actions tab** shows a green check for the Sunday run.
- If `preview/this-week.html` looks thin some week (only 1-2 posts on a
  quiet day), that's the "never forces a post" safety net — drop a couple
  more real photos into `photos/` and next Sunday will have more to work with.

---

## The golden rules

- You **only edit** `recurring_events.csv` (when your schedule changes) and
  `posts.csv` (special events, caption tweaks, `scheduled`/`skip` status).
  Everything in `scripts/` runs itself.
- **Nothing posts automatically anywhere.** You paste every post yourself
  into Facebook/Instagram's own scheduler — the system's whole job is to get
  the caption + image ready for you, not to touch your accounts.
- There is **no Meta/Facebook developer setup anywhere in this system** —
  only your Anthropic API key (`ANTHROPIC_API_KEY` in GitHub Secrets).
```

- [ ] **Step 3: Confirm no stray references to the removed Meta setup remain in the docs**

Run: `grep -n "developers.facebook.com\|META_PAGE\|META_IG\|App Review\|hourly" SETUP.md HOW-TO-USE-WEEKLY.md README.md`
Expected: no output. If `README.md` has stale references, note them for a
follow-up (README.md is out of scope for this plan unless it duplicates the
removed Meta setup steps — if it does, apply the same trim there).

- [ ] **Step 4: Commit**

```bash
git add SETUP.md HOW-TO-USE-WEEKLY.md
git commit -m "Rewrite setup/weekly docs for the manual-posting, preview-page workflow"
```

---

## Self-Review Notes

- **Spec coverage:** Section 1 (retire Meta) → Task 1. Section 2 (flyer into
  Sunday job) → Task 9. Section 3 (deal compositing) → Task 8. Section 4
  (template variety) → Task 7. Section 5 (caption authenticity) → Task 5.
  Section 6 (bookkeeping status) → Task 2. Section 7 (cadence guarantee) →
  Tasks 3 & 6. Section 8 (evergreen content) → Tasks 4 & 6. Section 9
  (optimal times) → Tasks 2 & 3. Section 10 (visual preview) → Task 10.
  Workflow/docs updates → Tasks 11 & 12.
- **Placeholder scan:** no TBD/TODO markers; `FEATURED_DRINKS`/
  `TRAIL_HIGHLIGHTS` are real starter content the owner is expected to edit
  to match the actual current menu/trails (documented as such in
  `config.py`'s own comment and in `SETUP.md`'s existing "edit config.py"
  convention), not unfinished placeholders.
- **Type/signature consistency:** `process_photos.process()`'s new
  `date_str`/`deal_photo_path` parameters are introduced once (Tasks 7-8) and
  used consistently by their only caller (`generate_captions.render_generated_images`,
  Task 9). `generate_captions()`/`_user_prompt()`'s `voice_examples` removal
  (Task 5) is threaded through every call site in the same task, and
  `build_extra_rows()`'s signature stays `(classified, existing_rows,
  run_date, avoid_examples_by_event=None)` unchanged in name across Tasks 5-6
  even though its internals are fully rewritten in Task 6.
