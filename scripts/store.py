"""
store.py - Read/write helpers for the two CSV files.

Keeps every row as a plain dict keyed by the columns in config.POSTS_COLUMNS so
the rest of the code never worries about column order or missing fields.
"""

from __future__ import annotations

import csv
import os
from datetime import datetime

import config


def load_recurring():
    """Return the recurring schedule as a list of dicts (one per event night)."""
    if not os.path.exists(config.RECURRING_CSV):
        return []
    with open(config.RECURRING_CSV, newline="", encoding="utf-8-sig") as f:
        return [dict(row) for row in csv.DictReader(f)]


def load_posts():
    """Return posts.csv as a list of dicts, every column present (blank if empty)."""
    rows = []
    if not os.path.exists(config.POSTS_CSV):
        return rows
    with open(config.POSTS_CSV, newline="", encoding="utf-8-sig") as f:
        for raw in csv.DictReader(f):
            row = {col: (raw.get(col) or "").strip() for col in config.POSTS_COLUMNS}
            rows.append(row)
    return rows


def write_posts(rows):
    """Overwrite posts.csv with these rows, in the canonical column order."""
    with open(config.POSTS_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=config.POSTS_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in config.POSTS_COLUMNS})


def blank_row():
    return {col: "" for col in config.POSTS_COLUMNS}


def recent_captions_for_event(rows, event, limit=4):
    """Most-recent-first ig_captions already posted/approved for this event.

    Used as the repetition guard so the caption prompt can be told what it
    already said recently and told not to repeat it.
    """
    matches = [r for r in rows
               if r["event"] == event and r["status"] in (config.STATUS_SCHEDULED, config.STATUS_POSTED)
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


def log(message: str):
    """Append a timestamped line to status.log (owner-visible) and stdout."""
    stamp = datetime.now(config.TIMEZONE).strftime("%Y-%m-%d %H:%M")
    line = f"[{stamp}] {message}"
    print(line)
    with open(config.STATUS_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")
