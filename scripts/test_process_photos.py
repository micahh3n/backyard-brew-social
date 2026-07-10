from PIL import Image

import config
import process_photos as pp


def _dummy_photo(color=(120, 150, 90), size=(1600, 1200)):
    return Image.new("RGB", size, color)


def test_process_premade_art_mode_untouched_passthrough(tmp_path):
    src = tmp_path / "2026-07-14_bingo_art.png"
    _dummy_photo().save(src)
    out = tmp_path / "out.png"
    pp.process(str(src), str(out), "ig_feed", "premade_art")
    result = Image.open(out)
    assert result.size == config.DIMENSIONS["ig_feed"]


def test_process_none_mode_applies_light_polish(tmp_path):
    src = tmp_path / "photo.jpg"
    _dummy_photo().save(src)
    out = tmp_path / "out.png"
    pp.process(str(src), str(out), "ig_feed", "none")
    result = Image.open(out)
    assert result.size == config.DIMENSIONS["ig_feed"]


def test_process_logo_mode_adds_watermark_without_error(tmp_path):
    src = tmp_path / "photo.jpg"
    _dummy_photo().save(src)
    out = tmp_path / "out.png"
    pp.process(str(src), str(out), "ig_feed", "logo")
    result = Image.open(out)
    assert result.size == config.DIMENSIONS["ig_feed"]


def test_process_text_overlay_mode_renders_via_flyer_render(tmp_path):
    src = tmp_path / "2026-07-14_bingo.jpg"
    _dummy_photo().save(src)
    out = tmp_path / "out.png"
    result_path = pp.process(str(src), str(out), "ig_feed", "text_overlay",
                             event="Bingo Night", key_details="10 rounds",
                             day_of_week="Monday", date_str="2026-07-14")
    assert result_path == str(out)
    result = Image.open(out)
    assert result.size == config.DIMENSIONS["ig_feed"]


def test_process_both_mode_renders_flyer_then_adds_logo(tmp_path):
    src = tmp_path / "2026-07-14_bingo.jpg"
    _dummy_photo().save(src)
    out = tmp_path / "out.png"
    pp.process(str(src), str(out), "ig_feed", "both",
              event="Bingo Night", key_details="10 rounds",
              day_of_week="Monday", date_str="2026-07-14")
    result = Image.open(out)
    assert result.size == config.DIMENSIONS["ig_feed"]


def test_process_composites_deal_photo_when_provided(tmp_path):
    src = tmp_path / "2026-07-14_pickleball.jpg"
    _dummy_photo().save(src)
    deal_photo = tmp_path / "2026-07-14_pickleball_deal.jpg"
    _dummy_photo(color=(255, 255, 255)).save(deal_photo)
    out = tmp_path / "out.png"
    pp.process(str(src), str(out), "ig_feed", "text_overlay",
              event="Pickleball Open Play", key_details="$2 off Spotted Cow",
              day_of_week="Tuesday", date_str="2026-07-14",
              deal_photo_path=str(deal_photo))
    result = Image.open(out).convert("RGB")
    assert result.size == config.DIMENSIONS["ig_feed"]


def test_resolve_mode_art_suffix_always_wins():
    assert pp.resolve_mode("2026-07-14_bingo_art.png", "text_overlay") == "premade_art"


def test_output_name_format():
    name = pp.output_name("post", "Bingo Night", "2026-07-14")
    assert name == "backyard-brew-post-bingo-night-2026-07-14.png"
