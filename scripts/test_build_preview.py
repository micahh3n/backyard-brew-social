import build_preview
import config
import store


def _row(**overrides):
    row = {**store.blank_row(), **overrides}
    return row


def test_build_preview_includes_event_and_captions():
    rows = [_row(event="Bingo Night", fb_caption="FB text here", ig_caption="IG text here",
                scheduled_time="2026-07-13 11:00", generated_image="photos/_generated/x.png")]
    html_out = build_preview.build_preview(rows)
    assert "Bingo Night" in html_out
    assert "FB text here" in html_out
    assert "IG text here" in html_out
    assert "photos/_generated/x.png" in html_out


def test_build_preview_escapes_html_in_captions():
    rows = [_row(event="Bingo Night", fb_caption="<script>alert(1)</script>", ig_caption="ok")]
    html_out = build_preview.build_preview(rows)
    assert "<script>" not in html_out
    assert "&lt;script&gt;" in html_out


def test_build_preview_orders_by_scheduled_time():
    rows = [
        _row(event="Second", scheduled_time="2026-07-14 11:00"),
        _row(event="First", scheduled_time="2026-07-13 11:00"),
    ]
    html_out = build_preview.build_preview(rows)
    assert html_out.index("First") < html_out.index("Second")


def test_write_preview_creates_the_file(tmp_path, monkeypatch):
    monkeypatch.setattr(build_preview, "PREVIEW_DIR", str(tmp_path / "preview"))
    monkeypatch.setattr(build_preview, "PREVIEW_FILE", str(tmp_path / "preview" / "this-week.html"))
    rows = [_row(event="Bingo Night", fb_caption="x", ig_caption="y",
                scheduled_time="2026-07-13 11:00")]
    path = build_preview.write_preview(rows)
    assert path == str(tmp_path / "preview" / "this-week.html")
    assert (tmp_path / "preview" / "this-week.html").exists()
