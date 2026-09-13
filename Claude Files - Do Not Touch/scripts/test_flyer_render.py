import html as html_mod
import os

from PIL import Image

import config
import flyer_render as fr


def _dummy_photo(path, color=(120, 150, 90), size=(1600, 1200)):
    Image.new("RGB", size, color).save(path)


def test_choose_layout_is_deterministic_for_same_input():
    a = fr.choose_layout("Bingo Night", "2026-07-14")
    b = fr.choose_layout("Bingo Night", "2026-07-14")
    assert a == b


def test_choose_layout_varies_across_dates():
    layouts = {fr.choose_layout("Bingo Night", f"2026-07-{d:02d}") for d in range(1, 29)}
    assert len(layouts) > 1
    assert layouts <= set(fr.LAYOUTS)


def test_prep_photo_produces_exact_target_size(tmp_path):
    src = tmp_path / "wide.jpg"
    _dummy_photo(str(src), size=(2400, 800))  # very wide source, needs real cropping
    out = tmp_path / "prepped.jpg"
    fr.prep_photo(str(src), str(out), size=(1080, 1080))
    result = Image.open(out)
    assert result.size == (1080, 1080)


def test_full_bleed_html_contains_event_day_and_detail():
    out = fr._full_bleed_html("file:///photo.jpg", "Bingo Night", "10 rounds, free to play",
                              "Monday")
    assert "BINGO NIGHT" in out
    assert "MONDAY" in out
    assert "10 rounds" in out


def test_full_bleed_html_escapes_special_characters():
    out = fr._full_bleed_html("file:///photo.jpg", "Rock & Roll Night", "Free w/ <beer>",
                              "Friday")
    assert "&amp;" in out
    assert "<beer>" not in out
    assert html_mod.escape("Free w/ <beer>") in out


def test_full_bleed_html_omits_deal_row_when_no_deal_photo():
    out = fr._full_bleed_html("file:///photo.jpg", "Bingo Night", "details", "Monday",
                              deal_photo_uri=None)
    assert "deal-row" not in out


def test_full_bleed_html_includes_deal_row_when_deal_photo_given():
    out = fr._full_bleed_html("file:///photo.jpg", "Bingo Night", "$2 off Spotted Cow", "Monday",
                              deal_photo_uri="file:///deal.jpg")
    assert "deal-row" in out
    assert "file:///deal.jpg" in out
    assert "Spotted Cow" in out


def test_editorial_split_html_contains_event_day_and_detail():
    out = fr._editorial_split_html("file:///photo.jpg", "Pool Night", "beat the bartender",
                                   "Saturday")
    assert "POOL NIGHT" in out
    assert "SATURDAY" in out
    assert "beat the bartender" in out


def test_editorial_split_html_omits_deal_row_when_no_deal_photo():
    out = fr._editorial_split_html("file:///photo.jpg", "Pool Night", "details", "Saturday",
                                   deal_photo_uri=None)
    assert "deal-row" not in out


def test_render_flyer_full_bleed_produces_correct_size(tmp_path):
    src = tmp_path / "photo.jpg"
    _dummy_photo(str(src))
    out = tmp_path / "out.png"
    fr.render_flyer(str(src), "Bingo Night", "10 rounds", "Monday", "2026-07-13",
                    str(out), size=(1080, 1080), layout="full_bleed")
    result = Image.open(out)
    assert result.size == (1080, 1080)


def test_render_flyer_editorial_split_produces_correct_size(tmp_path):
    src = tmp_path / "photo.jpg"
    _dummy_photo(str(src))
    out = tmp_path / "out.png"
    fr.render_flyer(str(src), "Pool Night", "beat the bartender", "Saturday", "2026-07-11",
                    str(out), size=(1080, 1080), layout="editorial_split")
    result = Image.open(out)
    assert result.size == (1080, 1080)


def test_render_flyer_with_deal_photo_still_renders_correct_size_both_layouts(tmp_path):
    """Regression for the real collision bug found in the old PIL system: a
    deal photo composited alongside a layout's own text must never break
    rendering or produce a wrong-sized image, on either layout."""
    src = tmp_path / "photo.jpg"
    _dummy_photo(str(src))
    deal = tmp_path / "deal.jpg"
    _dummy_photo(str(deal), color=(200, 50, 50))
    for layout in fr.LAYOUTS:
        out = tmp_path / f"out-{layout}.png"
        fr.render_flyer(str(src), "Pickleball Open Play", "$2 off Spotted Cow", "Tuesday",
                        "2026-07-14", str(out), size=(1080, 1080),
                        deal_photo_path=str(deal), layout=layout)
        result = Image.open(out)
        assert result.size == (1080, 1080), f"{layout} produced wrong size with a deal photo"
