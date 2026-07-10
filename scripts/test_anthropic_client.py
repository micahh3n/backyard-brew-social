from unittest.mock import MagicMock

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


def test_user_prompt_includes_avoid_examples():
    text = ac._user_prompt("Bingo Night", "details", "Monday", "today", None, None,
                           avoid_examples=["Old hook line"])
    assert "Old hook line" in text
    assert "do not" in text.lower() or "avoid" in text.lower()


def test_user_prompt_has_no_voice_examples_parameter():
    import inspect
    params = inspect.signature(ac._user_prompt).parameters
    assert "voice_examples" not in params


def test_system_prompt_instructs_varying_the_opening_move():
    text = ac._system_prompt()
    assert "vary" in text.lower() and "opening" in text.lower()


def test_system_prompt_instructs_rotating_share_mechanism():
    text = ac._system_prompt()
    assert "tag-a-friend" in text.lower() or "tag a friend" in text.lower()


def test_generate_captions_caches_the_system_prompt(monkeypatch):
    """The system prompt is identical on every caption call within a run --
    it should be sent with cache_control so only the first call pays full
    input-token price for it, cutting repeated-run API cost."""
    fake_client = MagicMock()
    fake_response = MagicMock()
    fake_block = MagicMock()
    fake_block.type = "text"
    fake_block.text = '{"fb_caption": "fb text", "ig_caption": "ig text"}'
    fake_response.content = [fake_block]
    fake_response.stop_reason = "end_turn"
    fake_client.messages.create.return_value = fake_response

    fake_anthropic = MagicMock()
    fake_anthropic.Anthropic.return_value = fake_client

    monkeypatch.setattr(ac, "anthropic", fake_anthropic)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")

    result = ac.generate_captions("Bingo Night", "details", "Monday", "today")

    assert result["_fallback"] is False
    _, kwargs = fake_client.messages.create.call_args
    system = kwargs["system"]
    assert isinstance(system, list)
    assert system[0]["cache_control"] == {"type": "ephemeral"}
    assert "Backyard Brew" in system[0]["text"]
