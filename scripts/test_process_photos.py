from PIL import Image

import config
import process_photos as pp


def _dummy_photo(color=(120, 150, 90), size=(800, 600)):
    return Image.new("RGB", size, color)


def test_choose_template_is_deterministic_for_same_input():
    a = pp.choose_template("Bingo Night", "2026-07-14")
    b = pp.choose_template("Bingo Night", "2026-07-14")
    assert a == b


def test_choose_template_varies_across_dates():
    templates = {pp.choose_template("Bingo Night", f"2026-07-{d:02d}") for d in range(1, 29)}
    assert len(templates) > 1
    assert templates <= set(pp.FLYER_TEMPLATES)


def test_build_flyer_minimal_returns_correct_size():
    result = pp._build_flyer_minimal(_dummy_photo(), "Bingo Night", "10 rounds, free to play",
                                     "Monday", (1080, 1080))
    assert result.size == (1080, 1080)


def test_build_flyer_poster_returns_correct_size():
    result = pp._build_flyer_poster(_dummy_photo(), "Pool Night", "beat the bartender",
                                    "Saturday", (1080, 1080))
    assert result.size == (1080, 1080)


def test_process_text_overlay_mode_picks_a_valid_template(tmp_path):
    src = tmp_path / "2026-07-14_bingo.jpg"
    _dummy_photo().save(src)
    out = tmp_path / "out.png"
    result_path = pp.process(str(src), str(out), "ig_feed", "text_overlay",
                             event="Bingo Night", key_details="10 rounds",
                             day_of_week="Monday", date_str="2026-07-14")
    assert result_path == str(out)
    result = Image.open(out)
    assert result.size == config.DIMENSIONS["ig_feed"]
