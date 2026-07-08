from datetime import date

import classify_photos
import config
import generate_captions as gc
import meta_client
import store


def _scheduled_row(dt_str):
    row = store.blank_row()
    row["scheduled_time"] = dt_str
    return row


def test_slug_from_default_strips_art_and_teaser_suffixes():
    assert gc.slug_from_default("bingo_default.jpg") == "bingo"
    assert gc.slug_from_default("bingo_default_art.png") == "bingo"
    assert gc.slug_from_default("bingo_default_teaser.jpg") == "bingo"


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


def test_main_gives_vibe_spotlight_posts_the_repetition_guard(monkeypatch):
    """main() must feed build_extra_rows() a populated avoid_examples_by_event
    for the generic recurring bucket names ("Behind The Scenes",
    "Community Spotlight") used by vibe/spotlight posts -- these are the
    posts most at risk of copy-paste drift over unattended weeks, since
    (unlike a dated event) the same label is reused every run.

    Currently main() calls build_extra_rows(...) with only voice_examples,
    never avoid_examples_by_event, so the repetition guard never reaches
    the caption prompt for these post types. This test drives main() itself
    (with its collaborators stubbed) and asserts the caption call for the
    new "Behind The Scenes" row actually receives the old caption text.
    """
    run_date = date(2026, 5, 31)  # a Sunday

    existing_row = {**store.blank_row(), "date": "2026-05-20",
                    "event": "Behind The Scenes", "status": config.STATUS_POSTED,
                    "ig_caption": "Some old caption"}

    monkeypatch.setattr(gc, "today_local", lambda: run_date)
    monkeypatch.setattr(store, "load_posts", lambda: [dict(existing_row)])
    monkeypatch.setattr(store, "load_recurring", lambda: [])
    monkeypatch.setattr(store, "write_posts", lambda rows: None)
    monkeypatch.setattr(meta_client, "recent_page_posts", lambda limit=6: [])
    monkeypatch.setattr(
        classify_photos, "classify_new_photos",
        lambda photos_dir, known_events, used: [
            {"filename": "vibe1.jpg", "match": None, "kind": "vibe", "confidence": "high"},
        ])

    captured = {}
    real_generate_captions_for = gc.generate_captions_for

    def spy_generate_captions_for(event, key_details, day_of_week, post_type,
                                   voice_examples=None, avoid_examples=None):
        if event == "Behind The Scenes":
            captured["avoid_examples"] = avoid_examples
        return real_generate_captions_for(event, key_details, day_of_week, post_type,
                                          voice_examples=voice_examples,
                                          avoid_examples=avoid_examples)

    monkeypatch.setattr(gc, "generate_captions_for", spy_generate_captions_for)

    gc.main()

    assert captured.get("avoid_examples"), (
        "expected a non-empty avoid_examples to reach caption generation "
        "for the 'Behind The Scenes' vibe post")
    assert "Some old caption" in captured["avoid_examples"]


def test_vibe_spotlight_lands_on_genuinely_quietest_day_not_tomorrow():
    """Vibe/spotlight posts must go on the quietest day of the week, not
    default to 'tomorrow' just because it happens to have room.

    run_date is a Sunday, so week_dates[0] ("tomorrow") is 2026-06-01 (Monday).
    We pre-load Monday with 1 existing post (still has room: < 2) but leave
    Tuesday (2026-06-02) completely empty -- the genuinely quietest day.
    A single vibe candidate (no event match) must land on Tuesday, not Monday.
    """
    run_date = date(2026, 5, 31)  # a Sunday
    classified = [
        {"filename": "vibe1.jpg", "match": None, "kind": "vibe", "confidence": "high"},
    ]
    existing_rows = [_scheduled_row("2026-06-01 12:00")]  # Monday has 1 post already
    rows = gc.build_extra_rows(classified, existing_rows, run_date)
    assert len(rows) == 1
    assert rows[0]["scheduled_time"].split(" ")[0] == "2026-06-02"
