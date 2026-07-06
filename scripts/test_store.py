import store


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
        _row(date="2026-06-08", ig_caption="Third", status="approved"),
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
