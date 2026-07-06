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


def source_photo_paths(row):
    """All filenames in the photos column that actually exist -> absolute paths."""
    names = [n.strip() for n in (row["photos"] or "").split(",") if n.strip()]
    paths = [os.path.join(config.PHOTOS_DIR, n) for n in names]
    return [p for p in paths if os.path.exists(p)]


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
    """Post one row (single photo or multi-photo carousel/album). Returns the
    set of platform codes that succeeded."""
    srcs = source_photo_paths(row)
    if not srcs:
        store.log(f"MISSING PHOTO for '{row['event']}' {row['scheduled_time']} "
                  f"-> '{row['photos']}' not in /photos/. Left approved for retry.")
        return set()

    intended_names = [n.strip() for n in (row["photos"] or "").split(",") if n.strip()]
    if len(intended_names) > 1 and len(srcs) < 2:
        store.log(f"MISSING PHOTO(S) for '{row['event']}' {row['scheduled_time']} "
                  f"-> carousel intended {len(intended_names)} photo(s) ('{row['photos']}') "
                  f"but only {len(srcs)} found in /photos/. Held back (not posted partially). "
                  f"Left approved for retry.")
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
