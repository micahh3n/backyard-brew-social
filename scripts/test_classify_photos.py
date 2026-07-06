from datetime import datetime
from unittest.mock import patch

import classify_photos


def test_needs_classification_skips_known_suffixes():
    assert classify_photos.needs_classification("2026-06-01_bingo_teaser.jpg") is False
    assert classify_photos.needs_classification("2026-06-01_bingo_art.png") is False
    assert classify_photos.needs_classification("2026-06-01_vibe_sunset.jpg") is False
    assert classify_photos.needs_classification("2026-06-01_spotlight_regular.jpg") is False


def test_needs_classification_allows_plain_photos():
    assert classify_photos.needs_classification("IMG_4821.jpg") is True
    assert classify_photos.needs_classification("bonfire_night.png") is True


def test_classify_photo_parses_model_response():
    fake_response_text = '{"match": "Bingo Night", "kind": "event", "confidence": "high"}'
    with patch("classify_photos._call_vision", return_value=fake_response_text):
        result = classify_photos.classify_photo("fake/path.jpg", ["Bingo Night", "Pool Night"])
    assert result == {"match": "Bingo Night", "kind": "event", "confidence": "high"}


def test_classify_photo_falls_back_to_low_confidence_on_bad_response():
    with patch("classify_photos._call_vision", return_value="not json at all"):
        result = classify_photos.classify_photo("fake/path.jpg", ["Bingo Night"])
    assert result == {"match": None, "kind": None, "confidence": "low"}


def test_classify_new_photos_skips_used_and_suffixed_files(tmp_path):
    (tmp_path / "2026-06-01_bingo_teaser.jpg").write_bytes(b"x")
    (tmp_path / "already_used.jpg").write_bytes(b"x")
    (tmp_path / "fresh_one.jpg").write_bytes(b"x")
    with patch("classify_photos.classify_photo",
               return_value={"match": None, "kind": "vibe", "confidence": "high"}), \
         patch("classify_photos.read_capture_time", return_value=datetime(2026, 6, 1, 18, 0)):
        result = classify_photos.classify_new_photos(
            str(tmp_path), ["Bingo Night"], used_filenames={"already_used.jpg"})
    assert len(result) == 1
    assert result[0]["filename"] == "fresh_one.jpg"
    assert result[0]["kind"] == "vibe"
