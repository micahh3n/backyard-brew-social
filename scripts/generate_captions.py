"""
generate_captions.py - The Sunday job.

For the upcoming week it builds, per event, a "today" post and a "tomorrow"
teaser post. For any one-off row in posts.csv with a promote_from date, it
expands the whole reminder campaign (countdown) at once. Every generated row
gets a photo, a scheduled time, both captions, and status = needs_review, then
is saved into posts.csv for the owner to review in one Sunday sitting.

This job NEVER posts anything. Run it with:  python scripts/generate_captions.py
"""

from __future__ import annotations

import os
from collections import defaultdict
from datetime import datetime, timedelta

import anthropic_client
import build_preview
import classify_photos
import config
import process_photos
import scheduling
import store
import weather
from anthropic_client import generate_captions

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
                # Not an exception, so the try/except below never sees this --
                # log explicitly. This exact bug happened for real: a
                # filename-case mismatch (recurring_events.csv referenced
                # lowercase, the real file started with a capital letter)
                # silently produced zero image for three events every week,
                # invisible because Windows' case-insensitive filesystem
                # hid it in local testing while GitHub Actions' Linux
                # runner (case-sensitive) enforced it for real.
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
    """Auto-suggest text_overlay for info-dense pushes, none for vibe content.

    The owner can always override in review. A _art file is handled by the
    filename itself, so this never overrides finished art.
    """
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


# ---------------------------------------------------------------------------
# Row builder
# ---------------------------------------------------------------------------
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
    row["fb_caption"] = caps["fb_caption"]
    row["ig_caption"] = caps["ig_caption"]
    row["_fallback"] = caps.get("_fallback", False)
    row["status"] = config.STATUS_NEEDS_REVIEW
    return row


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    run_date = today_local()
    recurring = load_recurring_by_day()
    posts = store.load_posts()

    # Index what already exists so re-runs don't duplicate.
    existing = {(r["date"], r["event"], r["post_type"]) for r in posts if r["post_type"]}
    skip_dates = {r["date"] for r in posts if r["status"] == config.STATUS_SKIP}
    generated = []
    campaign_dates = set()  # (date, event) fully handled by a campaign

    # --- 1. Campaign expansion (can extend beyond the 7-day window) ----------
    for src in posts:
        if src["status"] != config.STATUS_PENDING or not src["promote_from"]:
            continue
        try:
            event_date = parse_date(src["date"])
            promote_from = parse_date(src["promote_from"])
        except ValueError:
            store.log(f"campaign row has a bad date, skipping: {src.get('event')}")
            continue
        event = src["event"]
        details = src["key_details"]
        platforms = src["platforms"]
        photo_col = src["photos"]
        slug = slug_from_event(event)
        rhythm = config.CAMPAIGN_RHYTHMS[config.DEFAULT_CAMPAIGN_RHYTHM]

        # Reminder milestones (>=2 days out), plus teaser (day before) + today.
        milestones = [(d, f"reminder_{d}d") for d in rhythm]
        milestones += [(1, "teaser"), (0, "today")]
        for days_before, ptype in milestones:
            post_date = event_date - timedelta(days=days_before)
            if post_date < run_date or post_date < promote_from:
                continue  # milestone already passed or before promo window
            key = (src["date"], event, ptype)
            if key in existing:
                continue
            photo = find_photo(post_date.strftime(DATE_FMT), slug,
                               want_teaser=(ptype != "today"),
                               default_photo=photo_col)
            enhance = suggest_enhance(event, details, is_promo=True)
            generated.append(build_row(
                event_date, post_date, event, details, platforms,
                ptype, photo, enhance,
                days_until=(days_before if days_before >= 2 else None),
                avoid_examples=store.recent_captions_for_event(posts, event, limit=4)))
        src["status"] = config.STATUS_CAMPAIGN_SOURCE
        campaign_dates.add((src["date"], event))
        store.log(f"expanded campaign for '{event}' on {src['date']} "
                  f"({config.DEFAULT_CAMPAIGN_RHYTHM} rhythm)")

    # --- 2. Simple one-off overrides (pending, no promote_from) --------------
    # These become the "today" post for their date; a teaser is added too.
    oneoffs = {}
    for src in posts:
        if (src["status"] == config.STATUS_PENDING and not src["promote_from"]
                and src["event"] and src["date"]):
            oneoffs[src["date"]] = src

    # --- 3. Walk the upcoming 7 days for recurring + one-offs ----------------
    for i in range(1, 8):
        d = run_date + timedelta(days=i)
        dstr = d.strftime(DATE_FMT)
        if dstr in skip_dates:
            continue

        one = oneoffs.get(dstr)
        if one:
            event = one["event"]
            details = one["key_details"]
            platforms = one["platforms"]
            slug = slug_from_event(event)
            default_photo = one["photos"]
            owner_time = one["time"]
        else:
            rec = recurring.get(dow_name(d))
            if not rec:
                continue  # e.g. Sunday: no recurring event, no today post
            event = rec["event"]
            details = rec["key_details"]
            platforms = rec["platforms"]
            slug = slug_from_default(rec["default_photos"])
            default_photo = rec["default_photos"]
            owner_time = ""

        if (dstr, event) in campaign_dates:
            continue  # a campaign already produced this event's posts

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

        # teaser post (posts the evening before, about this event)
        teaser_post_date = d - timedelta(days=1)
        if teaser_post_date >= run_date and (dstr, event, "teaser") not in existing:
            photo = find_photo(dstr, slug, want_teaser=True, default_photo=default_photo,
                               event=event, posts_history=posts + generated)
            enhance = suggest_enhance(event, details, is_promo=bool(one))
            generated.append(build_row(d, teaser_post_date, event, details,
                                       platforms, "teaser", photo, enhance,
                                       avoid_examples=store.recent_captions_for_event(posts, event, limit=4)))

    # --- 5. Extra post types: carousel / vibe / spotlight --------------------
    used = store.used_photo_filenames(posts + generated)
    known_events = list(config.EVENT_ANGLES.keys())
    classified = classify_photos.classify_new_photos(config.PHOTOS_DIR, known_events, used)
    # Same repetition guard recurring/one-off/campaign posts already get, but
    # scoped to the generic bucket names vibe/spotlight posts reuse every week
    # (all four config.EVERGREEN_LABELS, plus "Community Spotlight") -- unlike
    # a dated event, these are the ones most likely to drift into
    # copy-paste-feeling repeats over unattended runs.
    extra_event_labels = list(config.EVERGREEN_LABELS) + ["Community Spotlight"]
    avoid_examples_by_event = {
        label: store.recent_captions_for_event(posts, label, limit=4)
        for label in extra_event_labels
    }
    extra_rows = build_extra_rows(classified, posts + generated, run_date,
                                  avoid_examples_by_event=avoid_examples_by_event)
    generated += extra_rows
    if extra_rows:
        store.log(f"generated {len(extra_rows)} extra post(s): "
                  f"{', '.join(r['post_type'] for r in extra_rows)}")

    # --- 6. Render flyer images, build the preview page, then save -----------
    all_rows = posts + generated
    render_generated_images(all_rows)
    week_rows = [r for r in all_rows if r["status"] == config.STATUS_NEEDS_REVIEW]
    build_preview.write_preview(week_rows)
    store.write_posts(all_rows)
    fell_back = sum(1 for r in generated if r.get("_fallback"))
    store.log(f"Sunday job done: generated {len(generated)} new post rows "
              f"(needs_review). Timing source: {config.TIMING_SOURCE}.")
    if fell_back:
        store.log(f"note: {fell_back} rows may need a manual caption pass.")
    usage = anthropic_client.usage_summary()
    if usage["calls"]:
        # Real evidence the system-prompt cache_control is doing something
        # (or isn't -- Anthropic silently no-ops caching below its minimum
        # cacheable prompt length, so this is the only way to know for sure).
        store.log(
            f"caption API usage: {usage['calls']} calls, "
            f"{usage['cache_read_input_tokens']} cache-read input tokens, "
            f"{usage['cache_creation_input_tokens']} cache-write input tokens, "
            f"{usage['input_tokens']} uncached input tokens, "
            f"{usage['output_tokens']} output tokens."
        )


def load_recurring_by_day():
    out = {}
    for row in store.load_recurring():
        out[row["day_of_week"].strip()] = row
    return out


# ---------------------------------------------------------------------------
# Extra post types (carousel / vibe / spotlight) -- hard-capped, anti-stacking.
# ---------------------------------------------------------------------------
def day_post_counts(rows):
    """How many posts already land on each date (YYYY-MM-DD), across rows."""
    counts = {}
    for r in rows:
        d = (r.get("scheduled_time") or "").split(" ")[0]
        if d:
            counts[d] = counts.get(d, 0) + 1
    return counts


def quietest_day(candidate_dates, counts):
    """The candidate date with the fewest posts already scheduled."""
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
                "capture_times": [i.get("capture_time") for i in items if i.get("capture_time")],
            })
    return groups


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
            # Pick by remaining fill need (not raw count): a day's target
            # already encodes its baseline shortfall + any bonus slot, so
            # concentrating on the neediest day first actually reaches
            # MIN_DAILY_POSTS instead of spreading thin across every day.
            # Ties (equal need) break toward the earliest date.
            target = max(eligible, key=lambda d: targets[d])
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


def generate_captions_for(event, key_details, day_of_week, post_type,
                          avoid_examples=None):
    """Thin wrapper so build_extra_rows doesn't need to import anthropic_client
    directly -- keeps the caption-generation entry point in one place."""
    from anthropic_client import generate_captions as _gen
    return _gen(event, key_details, day_of_week, post_type,
               avoid_examples=avoid_examples)


if __name__ == "__main__":
    main()
