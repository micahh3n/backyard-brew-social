import anthropic_client as ac


def test_framing_vibe_suppresses_cta():
    text = ac._framing("vibe", None)
    assert "no CTA" in text or "NO CTA" in text.upper()


def test_framing_spotlight_mentions_crediting():
    text = ac._framing("spotlight", None)
    assert "credit" in text.lower()


def test_framing_carousel_mentions_recap():
    text = ac._framing("carousel", None)
    assert "recap" in text.lower() or "looking back" in text.lower()


def test_fallback_captions_handles_vibe():
    result = ac.fallback_captions("Behind The Scenes", "", post_type="vibe")
    assert result["fb_caption"] and result["ig_caption"]


def test_fallback_captions_handles_spotlight():
    result = ac.fallback_captions("Community Spotlight", "", post_type="spotlight")
    assert result["fb_caption"] and result["ig_caption"]


def test_fallback_captions_handles_carousel():
    result = ac.fallback_captions("Bingo Night", "10 rounds", post_type="carousel")
    assert result["fb_caption"] and result["ig_caption"]
