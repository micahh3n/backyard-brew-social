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
