from datetime import date, datetime

import build_preview
import classify_photos
import config
import generate_captions as gc
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


def test_main_gives_vibe_spotlight_posts_the_repetition_guard(monkeypatch):
    """main() must feed build_extra_rows() a populated avoid_examples_by_event
    for ALL of the generic recurring bucket names used by vibe/spotlight
    posts -- the four config.EVERGREEN_LABELS ("Behind The Scenes",
    "Wisconsin Spotlight", "Course & Trail Feature", "Weather Vibes") plus
    "Community Spotlight" -- since these are the posts most at risk of
    copy-paste drift over unattended weeks (unlike a dated event, the same
    label is reused every run).

    Previously main() built extra_event_labels from a hardcoded two-item
    list ("Behind The Scenes", "Community Spotlight"), so the repetition
    guard never reached the caption prompt for "Wisconsin Spotlight",
    "Course & Trail Feature", or "Weather Vibes". This test drives main()
    itself (with its collaborators stubbed) and asserts the caption calls
    for both a "Behind The Scenes" row and a "Wisconsin Spotlight" row
    actually receive their respective old caption text.
    """
    run_date = date(2026, 5, 31)  # a Sunday

    existing_rows = [
        {**store.blank_row(), "date": "2026-05-20",
         "event": "Behind The Scenes", "status": config.STATUS_POSTED,
         "ig_caption": "Some old caption"},
        {**store.blank_row(), "date": "2026-05-21",
         "event": "Wisconsin Spotlight", "status": config.STATUS_POSTED,
         "ig_caption": "Some other old caption"},
    ]

    monkeypatch.setattr(gc, "today_local", lambda: run_date)
    monkeypatch.setattr(store, "load_posts", lambda: [dict(r) for r in existing_rows])
    monkeypatch.setattr(store, "load_recurring", lambda: [])
    monkeypatch.setattr(store, "write_posts", lambda rows: None)
    monkeypatch.setattr(store, "log", lambda message: None)
    monkeypatch.setattr(build_preview, "write_preview", lambda rows: "")
    monkeypatch.setattr(
        classify_photos, "classify_new_photos",
        lambda photos_dir, known_events, used: [
            {"filename": "vibe1.jpg", "match": None, "kind": "vibe", "confidence": "high"},
            {"filename": "vibe2.jpg", "match": None, "kind": "vibe", "confidence": "high"},
        ])

    captured = {}
    real_generate_captions_for = gc.generate_captions_for

    def spy_generate_captions_for(event, key_details, day_of_week, post_type,
                                   avoid_examples=None):
        if event in ("Behind The Scenes", "Wisconsin Spotlight"):
            captured[event] = avoid_examples
        return real_generate_captions_for(event, key_details, day_of_week, post_type,
                                          avoid_examples=avoid_examples)

    monkeypatch.setattr(gc, "generate_captions_for", spy_generate_captions_for)

    gc.main()

    assert captured.get("Behind The Scenes"), (
        "expected a non-empty avoid_examples to reach caption generation "
        "for the 'Behind The Scenes' vibe post")
    assert "Some old caption" in captured["Behind The Scenes"]

    assert captured.get("Wisconsin Spotlight"), (
        "expected a non-empty avoid_examples to reach caption generation "
        "for the 'Wisconsin Spotlight' vibe post -- this is the guard for "
        "one of the three evergreen labels previously left off the "
        "hardcoded extra_event_labels list")
    assert "Some other old caption" in captured["Wisconsin Spotlight"]


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


def test_photo_last_used_returns_most_recent_date_per_filename():
    rows = [
        {**store.blank_row(), "date": "2026-06-01", "photos": "a.jpg"},
        {**store.blank_row(), "date": "2026-06-08", "photos": "a.jpg, b.jpg"},
    ]
    last_used = gc._photo_last_used(rows)
    assert last_used["a.jpg"] == "2026-06-08"
    assert last_used["b.jpg"] == "2026-06-08"


def test_pick_pool_photo_prefers_never_used_photo(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "bingo_old.jpg").write_bytes(b"x")
    (tmp_path / "bingo_new.jpg").write_bytes(b"x")
    posts_history = [{**store.blank_row(), "date": "2026-06-01", "photos": "bingo_old.jpg"}]
    pick = gc._pick_pool_photo(["bingo"], exclude_filenames=set(), posts_history=posts_history)
    assert pick == "bingo_new.jpg"


def test_pick_pool_photo_picks_oldest_last_used_when_all_used_photos(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "bingo_a.jpg").write_bytes(b"x")
    (tmp_path / "bingo_b.jpg").write_bytes(b"x")
    posts_history = [
        {**store.blank_row(), "date": "2026-06-01", "photos": "bingo_a.jpg"},
        {**store.blank_row(), "date": "2026-06-08", "photos": "bingo_b.jpg"},
    ]
    pick = gc._pick_pool_photo(["bingo"], exclude_filenames=set(), posts_history=posts_history)
    assert pick == "bingo_a.jpg"  # used longest ago wins


def test_pick_pool_photo_breaks_never_used_ties_toward_newest_capture_time(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "bingo_a.jpg").write_bytes(b"x")
    (tmp_path / "bingo_b.jpg").write_bytes(b"x")

    def fake_capture_time(path):
        return datetime(2026, 1, 1) if path.endswith("bingo_a.jpg") else datetime(2026, 6, 1)

    monkeypatch.setattr(classify_photos, "read_capture_time", fake_capture_time)
    pick = gc._pick_pool_photo(["bingo"], exclude_filenames=set(), posts_history=[])
    assert pick == "bingo_b.jpg"


def test_pick_pool_photo_excludes_the_events_own_default_photo(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "Bingo_default_art.jpg").write_bytes(b"x")
    pick = gc._pick_pool_photo(["bingo"], exclude_filenames={"Bingo_default_art.jpg"}, posts_history=[])
    assert pick is None


def test_pick_pool_photo_returns_none_when_no_candidates(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    pick = gc._pick_pool_photo(["bingo"], exclude_filenames=set(), posts_history=[])
    assert pick is None


def test_pick_pool_photo_excludes_video_files(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "bingo_clip.mp4").write_bytes(b"x")
    pick = gc._pick_pool_photo(["bingo"], exclude_filenames=set(), posts_history=[])
    assert pick is None


def test_find_photo_dated_match_still_wins_over_pool(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "2026-07-13_bingo.jpg").write_bytes(b"x")
    (tmp_path / "party_bingo.jpg").write_bytes(b"x")
    photo = gc.find_photo("2026-07-13", "bingo", want_teaser=False,
                          default_photo="Bingo_default_art.jpg",
                          event="Bingo Night", posts_history=[])
    assert photo == "2026-07-13_bingo.jpg"


def test_find_photo_falls_through_to_pool_when_no_dated_match(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "party_bingo.jpg").write_bytes(b"x")
    photo = gc.find_photo("2026-07-13", "bingo", want_teaser=False,
                          default_photo="Bingo_default_art.jpg",
                          event="Bingo Night", posts_history=[])
    assert photo == "party_bingo.jpg"


def test_find_photo_falls_back_to_default_when_pool_empty(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    photo = gc.find_photo("2026-07-13", "bingo", want_teaser=False,
                          default_photo="Bingo_default_art.jpg",
                          event="Bingo Night", posts_history=[])
    assert photo == "Bingo_default_art.jpg"


def test_find_photo_without_event_keeps_old_behavior(monkeypatch, tmp_path):
    """One-off/campaign callers don't pass event/posts_history -- must
    behave exactly as before (no pool tier attempted)."""
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "party_bingo.jpg").write_bytes(b"x")
    photo = gc.find_photo("2026-07-13", "bingo", want_teaser=False,
                          default_photo="Bingo_default_art.jpg")
    assert photo == "Bingo_default_art.jpg"


def test_main_uses_pool_photo_for_recurring_event_when_no_dated_photo(tmp_path, monkeypatch):
    run_date = date(2026, 5, 31)  # a Sunday; Monday 2026-06-01 is Bingo Night
    monkeypatch.setattr(gc, "today_local", lambda: run_date)
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "party_bingo.jpg").write_bytes(b"x")

    monkeypatch.setattr(store, "load_posts", lambda: [])
    monkeypatch.setattr(store, "load_recurring", lambda: [
        {"day_of_week": "Monday", "event": "Bingo Night",
         "key_details": "details", "default_photos": "Bingo_default_art.jpg",
         "platforms": "both"},
    ])
    written = []
    monkeypatch.setattr(store, "write_posts", lambda rows: written.extend(rows))
    monkeypatch.setattr(store, "log", lambda message: None)
    monkeypatch.setattr(build_preview, "write_preview", lambda rows: "")
    monkeypatch.setattr(classify_photos, "classify_new_photos", lambda *a, **k: [])
    monkeypatch.setattr(gc, "render_generated_images", lambda rows: None)

    gc.main()

    bingo_today = [r for r in written
                  if r["event"] == "Bingo Night" and r["post_type"] == "today"]
    assert len(bingo_today) == 1
    assert bingo_today[0]["photos"] == "party_bingo.jpg"
