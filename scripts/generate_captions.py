"""
generate_captions.py - Reusable photo/schedule helpers for the Sunday social
media pass.

There's no automated entry point anymore -- the owner asks Claude Code
directly ("run sunday social media") to write the week's captions in
Backyard Brew's voice and propose a schedule. These functions are the
deterministic parts worth keeping as code rather than redoing by eye each
week: picking the right photo for a post (exact dated match, then the
undated event/food photo pool, then the static default) and the default
posting-time slots.
"""

from __future__ import annotations

import os
from datetime import datetime

import classify_photos
import config
import process_photos
import store

DATE_FMT = "%Y-%m-%d"


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def today_local():
    return datetime.now(config.TIMEZONE).date()


def parse_date(s):
    return datetime.strptime(s.strip(), DATE_FMT).date()


def dow_name(d):
    return d.strftime("%A")


def slug_from_default(default_photo):
    """bingo_default_art.png -> 'bingo' (the keyword the owner puts in filenames).

    Strips both "_default" and any "_art"/"_teaser" suffix so a default that's
    premade art still matches future dated photos dropped for the same event.
    """
    stem = os.path.splitext(os.path.basename(default_photo or ""))[0]
    for token in ("_default", "_art", "_teaser"):
        stem = stem.replace(token, "")
    return stem.strip().lower() or "event"


def slug_from_event(event):
    return (event or "event").split()[0].lower()


def list_photos():
    if not os.path.isdir(config.PHOTOS_DIR):
        return []
    return [f for f in os.listdir(config.PHOTOS_DIR)
            if os.path.isfile(os.path.join(config.PHOTOS_DIR, f))
            and not f.lower().endswith((".txt", ".md"))]


def find_photo(post_date_str, slug, want_teaser, default_photo, event=None, posts_history=None):
    """Pick the right photo filename for a post.

    Preference order:
      today post:   {date}_{slug}[_art]  ->  pool photo (event keyword, LRU)  ->  default_photo
      teaser/remind {date}_{slug}_teaser[_art]  ->  {date}_{slug}[_art]  ->  pool  ->  default
    Returns a filename (not a full path). Never returns empty if a default exists.

    `event`/`posts_history` are optional -- pass posts_history=posts.csv rows
    (plus anything already picked this session) and event="Bingo Night" etc.
    to enable the undated-pool tier; omit both for a plain dated-or-default
    lookup (one-off/special events).
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


def find_food_photo(event, event_date, run_date, posts_history, exclude_filenames=None):
    """Return a filename to attach as a second photo on this recurring
    event's 'today' post, or None. Independent LRU rotation from the event
    photo pool -- never blocks or delays the main post.

    'Occasional' keywords (config.OCCASIONAL_FOOD_KEYWORDS, e.g. pizza --
    served every day at the bar) only attach on one deterministically
    rotating day per week (based on the run's ISO week number), so they
    don't show up on every single post just because they're always
    technically available.

    `exclude_filenames` should include the main photo filename already
    chosen for this row (via find_photo) -- a single filename can contain
    both an event keyword and a food keyword (e.g. "poker_pizza.jpg"), so
    without this the food LRU could re-pick the exact same file the main
    photo already used, duplicating it in the post's `photos` list.
    """
    exclude_filenames = exclude_filenames or set()
    for keyword, events in config.FOOD_PHOTO_KEYWORDS.items():
        if event not in events:
            continue
        if keyword in config.OCCASIONAL_FOOD_KEYWORDS:
            chosen_day = config.RECURRING_DAYS[run_date.isocalendar()[1] % len(config.RECURRING_DAYS)]
            if dow_name(event_date) != chosen_day:
                continue
        pick = _pick_pool_photo([keyword], exclude_filenames=exclude_filenames,
                                posts_history=posts_history)
        if pick:
            return pick
    return None


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


def render_generated_images(rows):
    """Render each row's flyer/photo to config.GENERATED_DIR and set
    generated_image to its repo-relative path. Never raises -- a render
    failure just leaves generated_image blank so the row still shows up for
    review with its original photo referenced in the photos column."""
    for row in rows:
        try:
            if row.get("generated_image") or not row.get("photos"):
                continue
            first_photo = row["photos"].split(",")[0].strip()
            src = os.path.join(config.PHOTOS_DIR, first_photo)
            if not os.path.isfile(src):
                store.log(f"no image for '{row['event']}' {row['date']}: "
                          f"'{first_photo}' not found in {config.PHOTOS_DIR} "
                          "(check filename spelling/case)")
                continue
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


def suggest_enhance(event, key_details, is_promo):
    """Auto-suggest text_overlay for info-dense pushes, none for vibe content."""
    text = f"{event} {key_details}".lower()
    hard_detail = any(k in text for k in
                      ("$", "buy-in", "tournament", "winner", "special",
                       "this week", "deadline", "prize"))
    return "text_overlay" if (is_promo or hard_detail) else "none"


def scheduled_string(post_date, dow_for_time, post_type, owner_time):
    """Return 'YYYY-MM-DD HH:MM' local. owner_time (HH:MM) overrides the default."""
    if owner_time:
        hhmm = owner_time.strip()
    else:
        key = "teaser" if post_type != "today" else "today"
        hhmm = config.DEFAULT_TIMES.get(
            (dow_for_time, key),
            config.DEFAULT_TIME_FALLBACK.get(key, "12:00"))
    return f"{post_date.strftime(DATE_FMT)} {hhmm}"


def load_recurring_by_day():
    out = {}
    for row in store.load_recurring():
        out[row["day_of_week"].strip()] = row
    return out
