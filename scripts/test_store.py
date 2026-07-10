import config
import store


def test_normalize_date_str_leaves_canonical_format_unchanged():
    assert store._normalize_date_str("2026-07-13") == "2026-07-13"


def test_normalize_date_str_fixes_excel_mangled_dates():
    """Regression test for a real bug: Excel silently rewrites a
    YYYY-MM-DD cell to M/D/YYYY the moment the owner opens+saves
    posts.csv, even if he only touched unrelated rows. This broke
    parse_date() (raised), build_preview's string-sort (mis-ordered
    since M/D/YYYY isn't zero-padded), and day_post_counts' cadence cap
    (mis-grouped) all at once."""
    assert store._normalize_date_str("7/13/2026") == "2026-07-13"
    assert store._normalize_date_str("07/13/2026") == "2026-07-13"


def test_normalize_date_str_passes_through_unknown_formats():
    assert store._normalize_date_str("not a date") == "not a date"
    assert store._normalize_date_str("") == ""


def test_normalize_scheduled_time_fixes_just_the_date_portion():
    assert store._normalize_scheduled_time("7/13/2026 11:00") == "2026-07-13 11:00"
    assert store._normalize_scheduled_time("2026-07-13 11:00") == "2026-07-13 11:00"
    assert store._normalize_scheduled_time("") == ""


def test_load_posts_normalizes_excel_mangled_dates(tmp_path, monkeypatch):
    csv_path = tmp_path / "posts.csv"
    csv_path.write_text(
        "date,time,photos,event,key_details,platforms,promote_from,post_type,"
        "enhance,fb_caption,ig_caption,scheduled_time,generated_image,status\n"
        "7/13/2026,,bingo.jpg,Bingo Night,,both,7/1/2026,today,none,,,"
        "7/13/2026 11:00,,needs_review\n",
        encoding="utf-8-sig",
    )
    monkeypatch.setattr(config, "POSTS_CSV", str(csv_path))
    rows = store.load_posts()
    assert len(rows) == 1
    assert rows[0]["date"] == "2026-07-13"
    assert rows[0]["scheduled_time"] == "2026-07-13 11:00"
    assert rows[0]["promote_from"] == "2026-07-01"


def _row(event="Bingo Night", date="2026-06-01", status="posted",
         ig_caption="Old caption", photos="2026-06-01_bingo.jpg"):
    row = store.blank_row()
    row.update(event=event, date=date, status=status,
               ig_caption=ig_caption, photos=photos)
    return row


def test_recent_captions_for_event_returns_most_recent_first():
    rows = [
        _row(date="2026-05-04", ig_caption="First"),
        _row(date="2026-06-01", ig_caption="Second"),
        _row(date="2026-06-08", ig_caption="Third", status="scheduled"),
        _row(date="2026-06-08", event="Pool Night", ig_caption="Unrelated"),
    ]
    result = store.recent_captions_for_event(rows, "Bingo Night", limit=2)
    assert result == ["Third", "Second"]


def test_recent_captions_for_event_ignores_pending_rows():
    rows = [_row(status="needs_review", ig_caption="Not yet approved")]
    assert store.recent_captions_for_event(rows, "Bingo Night") == []


def test_used_photo_filenames_splits_comma_lists():
    rows = [
        _row(photos="2026-06-01_bingo.jpg, 2026-06-01_bingo_teaser.jpg"),
        _row(photos=""),
    ]
    result = store.used_photo_filenames(rows)
    assert result == {"2026-06-01_bingo.jpg", "2026-06-01_bingo_teaser.jpg"}
