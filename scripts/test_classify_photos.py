import base64
from datetime import datetime
from io import BytesIO
from unittest.mock import MagicMock, patch

from PIL import Image

import classify_photos
import config


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


def test_classify_new_photos_never_calls_classify_photo_for_video(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CLASSIFICATION_CACHE", str(tmp_path / "cache.json"))
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


def test_prep_vision_bytes_downscales_large_images(tmp_path):
    """Full-res iPhone photos (often 3000px+) should be shrunk before being
    sent for classification -- classification only needs a coarse read, and
    downscaling caps the image-token cost per photo."""
    src = tmp_path / "big.jpg"
    Image.new("RGB", (3000, 2000), (5, 5, 5)).save(src, format="JPEG")

    b64 = classify_photos._prep_vision_bytes(str(src))
    decoded = base64.standard_b64decode(b64)
    reopened = Image.open(BytesIO(decoded))
    assert max(reopened.size) <= classify_photos.CLASSIFY_MAX_DIMENSION


def test_call_vision_uses_classification_model_not_caption_model(tmp_path, monkeypatch):
    """Classification should use config.CLASSIFICATION_MODEL (Haiku), a
    cheaper/faster model than the Sonnet model captions use -- classification
    is a much simpler task and runs far more often."""
    src = tmp_path / "photo.jpg"
    Image.new("RGB", (20, 20), (1, 2, 3)).save(src, format="JPEG")

    fake_client = MagicMock()
    fake_response = MagicMock()
    fake_block = MagicMock()
    fake_block.type = "text"
    fake_block.text = '{"match": null, "kind": "vibe", "confidence": "low"}'
    fake_response.content = [fake_block]
    fake_client.messages.create.return_value = fake_response

    fake_anthropic = MagicMock()
    fake_anthropic.Anthropic.return_value = fake_client

    monkeypatch.setattr(classify_photos, "anthropic", fake_anthropic)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")

    classify_photos._call_vision(str(src), ["Bingo Night"])

    _, kwargs = fake_client.messages.create.call_args
    assert kwargs["model"] == config.CLASSIFICATION_MODEL
    assert kwargs["model"] != config.ANTHROPIC_MODEL


def test_classify_photo_parses_model_response():
    fake_response_text = '{"match": "Bingo Night", "kind": "event", "confidence": "high"}'
    with patch("classify_photos._call_vision", return_value=fake_response_text):
        result = classify_photos.classify_photo("fake/path.jpg", ["Bingo Night", "Pool Night"])
    assert result == {"match": "Bingo Night", "kind": "event", "confidence": "high"}


def test_classify_photo_falls_back_to_low_confidence_on_bad_response():
    with patch("classify_photos._call_vision", return_value="not json at all"):
        result = classify_photos.classify_photo("fake/path.jpg", ["Bingo Night"])
    assert result == {"match": None, "kind": None, "confidence": "low"}


def test_manual_kind_reads_vibe_and_spotlight_suffixes():
    assert classify_photos.manual_kind("2026-07-16_sunset_vibe.jpg") == "vibe"
    assert classify_photos.manual_kind("regular_vibe.png") == "vibe"
    assert classify_photos.manual_kind("winner_spotlight.jpg") == "spotlight"
    assert classify_photos.manual_kind("IMG_4821.jpg") is None


def test_classify_new_photos_honors_vibe_suffix_without_calling_the_api(tmp_path, monkeypatch):
    """A _vibe/_spotlight-suffixed filename is the owner directly telling us
    its kind -- it must become a post without ever touching the vision API
    (previously this suffix was excluded from classification and then went
    nowhere, silently dropping the photo)."""
    monkeypatch.setattr(config, "CLASSIFICATION_CACHE", str(tmp_path / "cache.json"))
    photo_dir = tmp_path / "photos"
    photo_dir.mkdir()
    (photo_dir / "sunset_vibe.jpg").write_bytes(b"x")

    with patch("classify_photos.classify_photo") as mock_classify, \
         patch("classify_photos.read_capture_time", return_value=None):
        result = classify_photos.classify_new_photos(
            str(photo_dir), ["Bingo Night"], used_filenames=set())

    mock_classify.assert_not_called()
    assert len(result) == 1
    assert result[0]["filename"] == "sunset_vibe.jpg"
    assert result[0]["kind"] == "vibe"
    assert result[0]["confidence"] == "high"


def test_classify_new_photos_only_calls_the_api_once_per_filename_ever(tmp_path, monkeypatch):
    """A photo that never becomes a post (e.g. low confidence) must not be
    re-sent to the vision API on a later run -- the owner drops photos in
    continuously, so this cost would otherwise compound every week."""
    monkeypatch.setattr(config, "CLASSIFICATION_CACHE", str(tmp_path / "cache.json"))
    photo_dir = tmp_path / "photos"
    photo_dir.mkdir()
    (photo_dir / "blurry.jpg").write_bytes(b"x")

    with patch("classify_photos.classify_photo",
               return_value={"match": None, "kind": None, "confidence": "low"}) as mock_classify:
        classify_photos.classify_new_photos(str(photo_dir), ["Bingo Night"], used_filenames=set())
        classify_photos.classify_new_photos(str(photo_dir), ["Bingo Night"], used_filenames=set())

    assert mock_classify.call_count == 1, (
        "second run should have reused the cached result instead of calling "
        "the vision API again for the same filename")


def test_classify_new_photos_caches_and_still_returns_high_confidence_matches(tmp_path, monkeypatch):
    """A high-confidence match that isn't placed into a post this week (e.g.
    daily quota already full) must still come back from cache on a later
    run -- caching must not silently drop good candidates."""
    monkeypatch.setattr(config, "CLASSIFICATION_CACHE", str(tmp_path / "cache.json"))
    photo_dir = tmp_path / "photos"
    photo_dir.mkdir()
    (photo_dir / "vibe.jpg").write_bytes(b"x")

    with patch("classify_photos.classify_photo",
               return_value={"match": None, "kind": "vibe", "confidence": "high"}) as mock_classify, \
         patch("classify_photos.read_capture_time", return_value=None):
        first = classify_photos.classify_new_photos(str(photo_dir), ["Bingo Night"], used_filenames=set())
        second = classify_photos.classify_new_photos(str(photo_dir), ["Bingo Night"], used_filenames=set())

    assert mock_classify.call_count == 1
    assert len(first) == 1 and len(second) == 1
    assert first[0]["filename"] == second[0]["filename"] == "vibe.jpg"


def test_classify_new_photos_skips_used_and_suffixed_files(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CLASSIFICATION_CACHE", str(tmp_path / "cache.json"))
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
