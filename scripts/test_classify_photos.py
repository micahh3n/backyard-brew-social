import classify_photos


def test_needs_classification_skips_known_suffixes():
    assert classify_photos.needs_classification("2026-06-01_bingo_teaser.jpg") is False
    assert classify_photos.needs_classification("2026-06-01_bingo_art.png") is False
    assert classify_photos.needs_classification("2026-06-01_vibe_sunset.jpg") is False
    assert classify_photos.needs_classification("2026-06-01_spotlight_regular.jpg") is False


def test_needs_classification_allows_plain_photos():
    assert classify_photos.needs_classification("IMG_4821.jpg") is True
    assert classify_photos.needs_classification("bonfire_night.png") is True


def test_needs_classification_skips_video_files():
    """Video files (iPhones drop these alongside camera-roll photos) are
    never a still image, so they never need a manual look either."""
    assert classify_photos.needs_classification("IMG_8847.MP4") is False
    assert classify_photos.needs_classification("IMG_8847.mov") is False
    assert classify_photos.needs_classification("clip.m4v") is False
    assert classify_photos.needs_classification("clip.avi") is False


def test_manual_kind_reads_vibe_and_spotlight_suffixes():
    assert classify_photos.manual_kind("2026-07-16_sunset_vibe.jpg") == "vibe"
    assert classify_photos.manual_kind("regular_vibe.png") == "vibe"
    assert classify_photos.manual_kind("winner_spotlight.jpg") == "spotlight"
    assert classify_photos.manual_kind("IMG_4821.jpg") is None


def test_pool_claimed_matches_event_keyword():
    assert classify_photos.pool_claimed("party_bingo.jpg") is True
    assert classify_photos.pool_claimed("randomname.jpg") is False


def test_pool_claimed_matches_food_keyword():
    assert classify_photos.pool_claimed("wednesday_taco_special.jpg") is True
    assert classify_photos.pool_claimed("fresh_pizza_pie.jpg") is True


def test_pool_claimed_recognizes_an_events_own_default_art_filename():
    # Already excluded from a manual look by the existing "_art" check in
    # needs_classification() -- pool_claimed() should also recognize it as
    # claimed, never mistakenly report False.
    assert classify_photos.pool_claimed("Bingo_default_art.jpg") is True


def test_read_capture_time_falls_back_to_mtime(tmp_path):
    src = tmp_path / "photo.jpg"
    src.write_bytes(b"not a real image")
    # No EXIF (not even a real image) -- still returns the file's mtime, not None.
    assert classify_photos.read_capture_time(str(src)) is not None


def test_read_exif_time_returns_none_without_exif(tmp_path):
    """Must not fall back to mtime: a fresh clone would date the whole
    backlog as 'today' and stamp wrong dates onto every filename."""
    src = tmp_path / "no_exif.jpg"
    src.write_bytes(b"not a real image")
    assert classify_photos.read_exif_time(str(src)) is None
    # the mtime-fallback variant still answers, which is why they differ
    assert classify_photos.read_capture_time(str(src)) is not None
