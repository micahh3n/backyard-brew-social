from datetime import date, datetime, timedelta

import classify_photos
import config
import generate_captions as gc
import store


def test_slug_from_default_strips_art_and_teaser_suffixes():
    assert gc.slug_from_default("bingo_default.jpg") == "bingo"
    assert gc.slug_from_default("bingo_default_art.png") == "bingo"
    assert gc.slug_from_default("bingo_default_teaser.jpg") == "bingo"


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
    """One-off/special-event callers don't pass event/posts_history -- must
    behave exactly as before (no pool tier attempted)."""
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "party_bingo.jpg").write_bytes(b"x")
    photo = gc.find_photo("2026-07-13", "bingo", want_teaser=False,
                          default_photo="Bingo_default_art.jpg")
    assert photo == "Bingo_default_art.jpg"


def test_find_food_photo_attaches_mapped_food_photo(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "weds_taco.jpg").write_bytes(b"x")
    run_date = date(2026, 5, 31)  # Sunday
    event_date = date(2026, 6, 3)  # Wednesday
    pick = gc.find_food_photo("Tacos + Poker Club", event_date, run_date, posts_history=[])
    assert pick == "weds_taco.jpg"


def test_find_food_photo_returns_none_when_event_has_no_mapped_food(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    run_date = date(2026, 5, 31)
    pick = gc.find_food_photo("Karaoke Night", date(2026, 6, 5), run_date, posts_history=[])
    assert pick is None


def test_find_food_photo_gates_occasional_keyword_to_one_day_per_week(monkeypatch, tmp_path):
    """pizza is served every day, so it must not attach on every event's
    'today' post -- only on the one day per week the rotation lands on."""
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "fresh_pizza.jpg").write_bytes(b"x")
    run_date = date(2026, 5, 31)  # Sunday
    chosen_day = config.RECURRING_DAYS[run_date.isocalendar()[1] % len(config.RECURRING_DAYS)]
    other_day = next(d for d in config.RECURRING_DAYS if d != chosen_day)
    day_dates = {
        "Monday": date(2026, 6, 1), "Tuesday": date(2026, 6, 2),
        "Wednesday": date(2026, 6, 3), "Thursday": date(2026, 6, 4),
        "Friday": date(2026, 6, 5), "Saturday": date(2026, 6, 6),
    }
    event_by_day = {
        "Monday": "Bingo Night", "Tuesday": "Pickleball Open Play",
        "Wednesday": "Tacos + Poker Club", "Thursday": "Ladies Night + Line Dancing",
        "Friday": "Karaoke Night", "Saturday": "Pool Night",
    }
    chosen_pick = gc.find_food_photo(event_by_day[chosen_day], day_dates[chosen_day],
                                     run_date, posts_history=[])
    other_pick = gc.find_food_photo(event_by_day[other_day], day_dates[other_day],
                                    run_date, posts_history=[])
    assert chosen_pick == "fresh_pizza.jpg"
    assert other_pick is None


def test_find_food_photo_excludes_already_chosen_main_photo(monkeypatch, tmp_path):
    """A filename that contains BOTH an event keyword and a food keyword
    (e.g. poker_pizza.jpg matches "poker" for Tacos + Poker Club AND "pizza",
    which maps to every event) must never be picked as the food photo once
    it has already been chosen as the main photo -- otherwise the post ends
    up with the same filename listed twice in `photos`."""
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "poker_pizza.jpg").write_bytes(b"x")
    run_date = date(2026, 5, 31)  # Sunday

    # Find a date whose weekday matches this run's pizza-rotation day, so
    # "pizza" (an OCCASIONAL_FOOD_KEYWORDS entry) is actually eligible to
    # attach for "Tacos + Poker Club" today -- otherwise the day-gate alone
    # would already return None and the test wouldn't prove anything.
    chosen_day = config.RECURRING_DAYS[run_date.isocalendar()[1] % len(config.RECURRING_DAYS)]
    week_dates = [date(2026, 6, 1) + timedelta(days=i) for i in range(6)]  # Mon-Sat
    event_date = next(d for d in week_dates if gc.dow_name(d) == chosen_day)

    # Sanity check: without exclusion, the dual-keyword file is indeed a
    # valid (and only) food-photo candidate for this event/day.
    unfiltered = gc.find_food_photo("Tacos + Poker Club", event_date, run_date,
                                    posts_history=[])
    assert unfiltered == "poker_pizza.jpg"

    # With the main photo's filename excluded (as the owner/Claude would do
    # after picking the main photo), the same file must not be re-picked as
    # the food photo.
    pick = gc.find_food_photo("Tacos + Poker Club", event_date, run_date,
                              posts_history=[], exclude_filenames={"poker_pizza.jpg"})
    assert pick is None
