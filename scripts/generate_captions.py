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
from datetime import datetime, timedelta

import config
import store
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
    """bingo_default.jpg -> 'bingo' (the keyword the owner puts in filenames)."""
    stem = os.path.splitext(os.path.basename(default_photo or ""))[0]
    return stem.replace("_default", "").strip().lower() or "event"


def slug_from_event(event):
    return (event or "event").split()[0].lower()


def list_photos():
    if not os.path.isdir(config.PHOTOS_DIR):
        return []
    return [f for f in os.listdir(config.PHOTOS_DIR)
            if os.path.isfile(os.path.join(config.PHOTOS_DIR, f))
            and not f.lower().endswith((".txt", ".md"))]


def find_photo(post_date_str, slug, want_teaser, default_photo):
    """Pick the right photo filename for a post.

    Preference order:
      today post:   {date}_{slug}[_art]  ->  else default_photo
      teaser/remind {date}_{slug}_teaser[_art]  ->  {date}_{slug}[_art]  ->  default
    Returns a filename (not a full path). Never returns empty if a default exists.
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
    if want_teaser:
        return dated_teaser or dated_base or default_photo
    return dated_base or default_photo


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


def past_examples():
    """Placeholder hook for pulling real past captions as voice references.

    Left empty by default; wired for a future meta_client.recent_captions() pull.
    Returning [] simply means the prompt relies on the written voice rules.
    """
    return []


# ---------------------------------------------------------------------------
# Row builder
# ---------------------------------------------------------------------------
def build_row(event_date, post_date, event, key_details, platforms,
              post_type, photo, enhance, owner_time="", days_until=None):
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
                             days_until=days_until, past_examples=past_examples())
    row["fb_caption"] = caps["fb_caption"]
    row["ig_caption"] = caps["ig_caption"]
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
                days_until=(days_before if days_before >= 2 else None)))
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
            photo = find_photo(dstr, slug, want_teaser=False, default_photo=default_photo)
            enhance = suggest_enhance(event, details, is_promo=bool(one))
            row = build_row(d, d, event, details, platforms, "today",
                            photo, enhance, owner_time=owner_time)
            if one:
                # Repurpose the owner's original row into this today post
                # (no orphan pending row left behind).
                one.update(row)
            else:
                generated.append(row)

        # teaser post (posts the evening before, about this event)
        teaser_post_date = d - timedelta(days=1)
        if teaser_post_date >= run_date and (dstr, event, "teaser") not in existing:
            photo = find_photo(dstr, slug, want_teaser=True, default_photo=default_photo)
            enhance = suggest_enhance(event, details, is_promo=bool(one))
            generated.append(build_row(d, teaser_post_date, event, details,
                                       platforms, "teaser", photo, enhance))

    # --- 4. Save --------------------------------------------------------------
    all_rows = posts + generated
    store.write_posts(all_rows)
    fell_back = sum(1 for r in generated if not r["fb_caption"])
    store.log(f"Sunday job done: generated {len(generated)} new post rows "
              f"(needs_review). Timing source: {config.TIMING_SOURCE}.")
    if fell_back:
        store.log(f"note: {fell_back} rows may need a manual caption pass.")


def load_recurring_by_day():
    out = {}
    for row in store.load_recurring():
        out[row["day_of_week"].strip()] = row
    return out


if __name__ == "__main__":
    main()
