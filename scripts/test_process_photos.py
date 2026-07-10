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


def test_choose_template_respects_a_narrowed_candidate_pool():
    deal_safe = ["badge", "poster"]
    for d in range(1, 29):
        result = pp.choose_template("Bingo Night", f"2026-07-{d:02d}", deal_safe)
        assert result in deal_safe


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


def test_add_deal_callout_returns_same_size_image(tmp_path):
    base = _dummy_photo(size=(1080, 1080))
    deal_photo = tmp_path / "deal.jpg"
    _dummy_photo(color=(200, 50, 50)).save(deal_photo)
    result = pp._add_deal_callout(base, str(deal_photo), "$2 off Spotted Cow")
    assert result.size == base.size


def test_add_deal_callout_changes_pixels_near_the_badge(tmp_path):
    base = _dummy_photo(size=(1080, 1080), color=(0, 0, 0))
    deal_photo = tmp_path / "deal.jpg"
    _dummy_photo(color=(255, 255, 255)).save(deal_photo)
    result = pp._add_deal_callout(base, str(deal_photo), "$2 off Spotted Cow")
    # Bottom-left region should no longer be pure black once the badge lands there.
    sample = result.convert("RGB").getpixel((60, 1010))
    assert sample != (0, 0, 0)


def test_add_deal_callout_degrades_gracefully_on_missing_photo():
    base = _dummy_photo(size=(1080, 1080))
    result = pp._add_deal_callout(base, "/nonexistent/path.jpg", "$2 off Spotted Cow")
    assert result is base


def test_process_never_picks_minimal_template_when_deal_photo_present(tmp_path, monkeypatch):
    """The minimal template's caption bar sits bottom-left -- the same corner
    the deal callout badge occupies -- so process() must never route to it
    when compositing a deal photo (regression: they used to collide)."""
    calls = []
    monkeypatch.setattr(pp, "_build_flyer_minimal",
                        lambda *a, **k: calls.append("minimal") or pp._build_flyer(*a, **k))
    src = tmp_path / "photo.jpg"
    _dummy_photo().save(src)
    deal_photo = tmp_path / "deal.jpg"
    _dummy_photo(color=(255, 255, 255)).save(deal_photo)
    for d in range(1, 29):
        out = tmp_path / f"out-{d}.png"
        pp.process(str(src), str(out), "ig_feed", "text_overlay",
                  event="Bingo Night", key_details="10 rounds",
                  day_of_week="Monday", date_str=f"2026-07-{d:02d}",
                  deal_photo_path=str(deal_photo))
    assert calls == [], "minimal template must never be chosen alongside a deal photo"


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
