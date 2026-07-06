"""
post_to_meta.py - The hourly posting job.

Finds rows in posts.csv where status == approved and the scheduled time has
passed, then for each:
  1. renders the photo to the correct dimensions per platform (Instagram feed,
     Instagram story, Facebook),
  2. makes those images public (git commit + push so raw.githubusercontent can
     serve them), waits for the URL to go live,
  3. posts to Facebook and/or Instagram -- IG feed + auto Story repost + the
     hashtags as the first comment; both platforms get the auto location tag,
  4. marks the row `posted` on full success. On failure it logs the error and
     leaves the row `approved` so the next hourly run retries (never lost).

Run with:  python scripts/post_to_meta.py
Set DRY_RUN=1 to render + log without posting or pushing (useful for testing).
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import time
from datetime import datetime

import requests

import config
import meta_client
import process_photos
import store

DRY_RUN = os.environ.get("DRY_RUN") == "1"


def now_local():
    return datetime.now(config.TIMEZONE)


def parse_sched(s):
    """Parse 'YYYY-MM-DD HH:MM' as local time. Returns None if unparseable."""
    try:
        dt = datetime.strptime(s.strip(), "%Y-%m-%d %H:%M")
        return dt.replace(tzinfo=config.TIMEZONE)
    except (ValueError, AttributeError):
        return None


def wants(platforms, code):
    p = (platforms or "both").lower()
    return p == "both" or code in p


def source_photo_path(row):
    """First filename in the photos column -> absolute path, or None if missing."""
    first = (row["photos"] or "").split(",")[0].strip()
    if not first:
        return None
    path = os.path.join(config.PHOTOS_DIR, first)
    return path if os.path.exists(path) else None


def render_variant(src_path, row, platform_key, platform_short):
    """Render one platform image, save under photos/_generated, return (abs, rel)."""
    name = process_photos.output_name(platform_short, row["event"], row["date"])
    abs_path = os.path.join(config.GENERATED_DIR, name)
    process_photos.process(
        src_path, abs_path, platform_key, row["enhance"],
        event=row["event"], key_details=row["key_details"],
        day_of_week=datetime.strptime(row["date"], "%Y-%m-%d").strftime("%A"))
    rel = os.path.relpath(abs_path, config.REPO_ROOT).replace("\\", "/")
    return abs_path, rel


def push_images(rel_paths):
    """Commit + push generated images so their public URLs work. No-op on dry run."""
    if DRY_RUN or not rel_paths:
        return
    try:
        subprocess.run(["git", "add"] + rel_paths, cwd=config.REPO_ROOT, check=True)
        # Commit only if there's actually something staged.
        status = subprocess.run(["git", "status", "--porcelain"], cwd=config.REPO_ROOT,
                                capture_output=True, text=True).stdout.strip()
        if status:
            subprocess.run(["git", "commit", "-m", "Publish generated post images [skip ci]"],
                           cwd=config.REPO_ROOT, check=True)
            subprocess.run(["git", "push"], cwd=config.REPO_ROOT, check=True)
    except subprocess.CalledProcessError as exc:
        store.log(f"WARNING: could not push generated images: {exc}")


def wait_url_live(url, timeout=120):
    """Poll a URL until it returns 200 (raw CDN can lag a bit after a push)."""
    if DRY_RUN:
        return True
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if requests.head(url, timeout=15, allow_redirects=True).status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(6)
    return False


def hashtags_for(row):
    seed = int(hashlib.md5(f"{row['date']}{row['event']}".encode()).hexdigest(), 16)
    return config.pick_hashtags(seed)


def short_caption(caption, limit=180):
    text = " ".join(caption.split())
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "…"


def post_row(row):
    """Post one row. Returns the set of platform codes that succeeded."""
    src = source_photo_path(row)
    if not src:
        store.log(f"MISSING PHOTO for '{row['event']}' {row['scheduled_time']} "
                  f"-> '{row['photos']}' not in /photos/. Left approved for retry.")
        return set()

    succeeded = set()
    to_push, jobs = [], []

    # Render everything first so we can push all images in one commit.
    if wants(row["platforms"], "fb"):
        abs_p, rel_p = render_variant(src, row, "fb_feed", "fb")
        to_push.append(rel_p)
        jobs.append(("fb", rel_p))
    if wants(row["platforms"], "ig"):
        abs_f, rel_f = render_variant(src, row, "ig_feed", "ig-feed")
        abs_s, rel_s = render_variant(src, row, "ig_story", "ig-story")
        to_push += [rel_f, rel_s]
        jobs.append(("ig", (rel_f, rel_s)))

    push_images(to_push)

    for code, payload in jobs:
        try:
            if code == "fb":
                url = meta_client.public_image_url(payload)
                if not wait_url_live(url):
                    raise meta_client.MetaError(f"image URL not live yet: {url}")
                if DRY_RUN:
                    store.log(f"[DRY RUN] would post FB: {row['event']} -> {url}")
                else:
                    meta_client.post_facebook(url, row["fb_caption"])
                succeeded.add("fb")
            else:  # ig
                feed_rel, story_rel = payload
                feed_url = meta_client.public_image_url(feed_rel)
                story_url = meta_client.public_image_url(story_rel)
                if not wait_url_live(feed_url) or not wait_url_live(story_url):
                    raise meta_client.MetaError("IG image URL not live yet")
                if DRY_RUN:
                    store.log(f"[DRY RUN] would post IG feed+story+hashtags: {row['event']}")
                else:
                    meta_client.post_instagram(feed_url, row["ig_caption"], hashtags_for(row))
                    try:
                        meta_client.post_instagram_story(story_url)
                    except meta_client.MetaError as exc:
                        store.log(f"IG story repost failed (feed post is live): {exc}")
                succeeded.add("ig")
        except Exception as exc:
            store.log(f"POST FAILED [{code}] '{row['event']}' {row['scheduled_time']}: {exc}")

    return succeeded


def main():
    rows = store.load_posts()
    now = now_local()

    due = []
    for r in rows:
        if r["status"] != config.STATUS_APPROVED:
            continue
        sched = parse_sched(r["scheduled_time"])
        if sched is None:
            store.log(f"bad scheduled_time on '{r['event']}': '{r['scheduled_time']}' - skipping")
            continue
        if sched <= now:
            due.append(r)

    if not due:
        store.log("hourly job: nothing due.")
    for row in due:
        wanted = {c for c in ("fb", "ig") if wants(row["platforms"], c)}
        got = post_row(row)
        if got >= wanted:
            row["status"] = config.STATUS_POSTED
            store.log(f"POSTED '{row['event']}' ({row['post_type']}) to {', '.join(sorted(got)) or 'nothing'}")
        elif got:
            # Partial success: keep only the failed platform(s) for a clean retry.
            remaining = wanted - got
            row["platforms"] = "both" if remaining == {"fb", "ig"} else next(iter(remaining))
            store.log(f"PARTIAL '{row['event']}': posted {sorted(got)}, will retry {sorted(remaining)}")
        # else: total failure -> already logged, stays approved for retry.

    store.write_posts(rows)

    # 60-day token expiry reminder.
    days = meta_client.days_until_token_expires() if not DRY_RUN else None
    if days is not None and days <= config.TOKEN_WARN_DAYS:
        store.log(f"*** TOKEN EXPIRES IN {days} DAYS -- refresh META_PAGE_ACCESS_TOKEN soon ***")


if __name__ == "__main__":
    main()
