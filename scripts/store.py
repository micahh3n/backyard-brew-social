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
    with open(config.RECURRING_CSV, newline="", encoding="utf-8") as f:
        return [dict(row) for row in csv.DictReader(f)]


def load_posts():
    """Return posts.csv as a list of dicts, every column present (blank if empty)."""
    rows = []
    if not os.path.exists(config.POSTS_CSV):
        return rows
    with open(config.POSTS_CSV, newline="", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            row = {col: (raw.get(col) or "").strip() for col in config.POSTS_COLUMNS}
            rows.append(row)
    return rows


def write_posts(rows):
    """Overwrite posts.csv with these rows, in the canonical column order."""
    with open(config.POSTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=config.POSTS_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in config.POSTS_COLUMNS})


def blank_row():
    return {col: "" for col in config.POSTS_COLUMNS}


def log(message: str):
    """Append a timestamped line to status.log (owner-visible) and stdout."""
    stamp = datetime.now(config.TIMEZONE).strftime("%Y-%m-%d %H:%M")
    line = f"[{stamp}] {message}"
    print(line)
    with open(config.STATUS_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")
