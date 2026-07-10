import base64
from datetime import datetime
from io import BytesIO
from unittest.mock import patch

from PIL import Image

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
    """Video files (iPhones drop these alongside camera-roll photos) can
    never be classified as a still image -- must be skipped before ever
    reaching _call_vision, not sent to the API and left to fail with a 400."""
    assert classify_photos.needs_classification("IMG_8847.MP4") is False
    assert classify_photos.needs_classification("IMG_8847.mov") is False
    assert classify_photos.needs_classification("clip.m4v") is False
    assert classify_photos.needs_classification("clip.avi") is False


def test_classify_new_photos_never_calls_classify_photo_for_video(tmp_path):
    (tmp_path / "IMG_8847.MP4").write_bytes(b"x")
    with patch("classify_photos.classify_photo") as mock_classify:
        result = classify_photos.classify_new_photos(
            str(tmp_path), ["Bingo Night"], used_filenames=set())
    mock_classify.assert_not_called()
    assert result == []


def test_prep_vision_bytes_always_reencodes_as_real_jpeg(tmp_path):
    """Regression test for the bug found in the real Sunday run: the old
    code guessed media_type from the file extension while sending raw file
    bytes unchanged, so a .heic file's actual (non-JPEG) bytes got declared
    to the API as image/jpeg and rejected. Re-encoding through PIL guarantees
    the bytes we send are always genuinely a JPEG, regardless of source
    filename/format."""
    src = tmp_path / "photo.png"  # PNG bytes, but exercises the same "trust
    Image.new("RGB", (20, 20), (10, 20, 30)).save(src, format="PNG")  # the extension" bug class

    b64 = classify_photos._prep_vision_bytes(str(src))
    decoded = base64.standard_b64decode(b64)
    reopened = Image.open(BytesIO(decoded))
    assert reopened.format == "JPEG"


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
