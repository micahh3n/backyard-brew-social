import io
import os
from unittest.mock import patch

from PIL import Image

import config
import post_to_meta as ptm
import store


def _write_fake_jpeg(path):
    """A real, minimal, PIL-openable JPEG (a hand-rolled byte header isn't
    parseable by Pillow's JPEG decoder, so we generate one)."""
    buf = io.BytesIO()
    Image.new("RGB", (50, 50), color="red").save(buf, format="JPEG")
    path.write_bytes(buf.getvalue())


def _row(photos, platforms="both", post_type="today"):
    row = store.blank_row()
    row.update(photos=photos, platforms=platforms, post_type=post_type,
               event="Bingo Night", date="2026-06-01", key_details="",
               fb_caption="FB caption", ig_caption="IG caption",
               scheduled_time="2026-06-01 12:00", status=config.STATUS_APPROVED)
    return row


def test_source_photo_paths_returns_all_existing_files(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    (tmp_path / "a.jpg").write_bytes(b"x")
    (tmp_path / "b.jpg").write_bytes(b"x")
    row = _row("a.jpg, b.jpg, missing.jpg")
    result = ptm.source_photo_paths(row)
    assert len(result) == 2
    assert all(os.path.basename(p) in ("a.jpg", "b.jpg") for p in result)


def test_source_photo_paths_empty_when_none_exist(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    row = _row("missing.jpg")
    assert ptm.source_photo_paths(row) == []


def test_post_row_uses_carousel_path_for_multi_photo_ig(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    monkeypatch.setattr(config, "GENERATED_DIR", str(tmp_path / "_generated"))
    monkeypatch.setattr(ptm, "DRY_RUN", True)
    for name in ("a.jpg", "b.jpg", "c.jpg"):
        _write_fake_jpeg(tmp_path / name)
    row = _row("a.jpg, b.jpg, c.jpg", platforms="ig")
    with patch("post_to_meta.wait_url_live", return_value=True), \
         patch("post_to_meta.push_images"):
        succeeded = ptm.post_row(row)
    assert succeeded == {"ig"}


def test_post_row_holds_back_degraded_multi_photo_row(tmp_path, monkeypatch):
    """A row that intended a 3-photo carousel but has only 1 file actually on
    disk must be held back entirely for retry -- NOT silently posted as a
    single photo."""
    monkeypatch.setattr(config, "PHOTOS_DIR", str(tmp_path))
    monkeypatch.setattr(config, "GENERATED_DIR", str(tmp_path / "_generated"))
    monkeypatch.setattr(ptm, "DRY_RUN", True)
    _write_fake_jpeg(tmp_path / "a.jpg")
    row = _row("a.jpg, b.jpg, c.jpg", platforms="ig")
    with patch("post_to_meta.store.log") as mock_log, \
         patch("post_to_meta.wait_url_live", return_value=True), \
         patch("post_to_meta.push_images"), \
         patch("post_to_meta.render_variant") as mock_render:
        mock_render.return_value = (str(tmp_path / "fake.jpg"), "fake.jpg")
        succeeded = ptm.post_row(row)
    assert succeeded == set()
    assert mock_log.called
    # render_variant must never even be called -- the row is held back before
    # any rendering/upload work happens.
    mock_render.assert_not_called()
