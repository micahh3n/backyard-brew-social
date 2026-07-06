"""
anthropic_client.py - Generates on-brand Facebook + Instagram captions.

Uses the Anthropic API with Backyard Brew's exact voice rules. If the API call
fails for any reason, falls back to a simple templated caption so the owner
always has something to review (a day never goes dark on an API hiccup).
"""

from __future__ import annotations

import json
import os
import re

import config

try:
    import anthropic
except ImportError:  # library not installed yet (e.g. local dry run)
    anthropic = None


# ---------------------------------------------------------------------------
# The system prompt: Backyard Brew's brand voice, verbatim from the spec.
# ---------------------------------------------------------------------------
def _system_prompt() -> str:
    b = config.BUSINESS
    return f"""You write social captions for {b['name']}, {b['region']}'s most unique bar \
(bar + disc golf + hiking trails on 35 acres in {b['city']}, WI). Tagline: "{b['tagline']}".

VOICE (follow exactly):
- Energetic, community-first, outdoorsy, Wisconsin-proud, fun without being try-hard. \
Feels like a friend texting you about a cool spot -- never corporate.
- HOOK FIRST LINE, ALWAYS. The opening line must stop the scroll -- lead with the most \
surprising, specific, or urgency-driving detail. "Bingo's back" not "Hey everyone, don't forget".
- Wisconsin identity is the superpower -- SAY IT. Every beer, wine, seltzer is 100% \
Wisconsin-made, zero outside brands. That's rare and worth naming.
- WISCONSIN-ONLY IS NON-NEGOTIABLE. Never name-drop or reference any non-Wisconsin brand, \
chain, or product. Packers/Brewers/Green Bay references are welcome where natural.
- Promote the uniqueness: bar + disc golf + hiking, unlike anywhere else.
- Events need FOMO, not generic "join us" energy -- something you'd regret missing.
- Weave memberships in naturally and often (not a hard sell, just the obvious move): {config.MEMBERSHIPS}
- ONE clear foot-traffic CTA per post (a specific reason to come in), plus a rotated \
engagement bait (comment-bait "tag your ___", share-bait "send this to ___", or save-bait for \
info-dense posts). Specific CTAs only -- never a vague "come visit".
- No filler. Every word earns its place. Fragmented sentences over full paragraphs.
- On-brand emojis only, used naturally never spammed: {' '.join(config.EMOJIS)}
- Never post anything implying hours outside the real open hours.

FACEBOOK vs INSTAGRAM must be genuinely DIFFERENT posts, not repurposed copies:
- Facebook: conversational, event-focused, 80-150 words, full event details. NO hashtags.
- Instagram: punchy, ~100-150 characters above the fold, clean and short. NO hashtags in the \
caption (they are posted separately as the first comment).

Return ONLY valid JSON: {{"fb_caption": "...", "ig_caption": "..."}} -- no other text."""


def _framing(post_type: str, days_until: int | None) -> str:
    """Return the timing/format-specific instruction for this post."""
    if post_type == "today":
        return ("This is a TODAY post -- urgent, same-day framing. It's happening TONIGHT, "
                "come now. Same-day energy.")
    if post_type == "teaser":
        return ("This is a TOMORROW TEASER post -- anticipation/planning framing. Tomorrow's "
                "the night, tell your people, get ready. Must feel genuinely different from the "
                "same event's today post, not a copy with the day swapped.")
    if post_type == "vibe":
        return ("This is a BEHIND-THE-SCENES / VIBE post. NO CTA, no membership mention, no "
                "urgency framing -- suspend the usual foot-traffic-CTA rule entirely for this "
                "one. Just a short, warm, personality-driven line about this specific candid "
                "moment. Its whole job is likability, not conversion.")
    if post_type == "spotlight":
        return ("This is a COMMUNITY SPOTLIGHT post. Credit the person or moment specifically "
                "and warmly -- a genuine shoutout, not a generic mention. If concrete facts were "
                "given, use them exactly. If not, write a plausible generic shoutout from what "
                "the photo shows -- never invent a specific name.")
    if post_type == "carousel":
        return ("This is a CAROUSEL recap post, published the day AFTER the event, covering "
                "several photos from that night. Frame it as looking back at how it went -- "
                "'here's how last night went down' energy -- not urgency to attend, since it "
                "already happened.")
    # Campaign reminder
    if days_until is not None and days_until >= 10:
        urgency = "It's a couple weeks out -- 'mark your calendar / save the date' energy, build anticipation."
    elif days_until is not None and days_until >= 4:
        urgency = "It's about a week out -- 'start making plans, clear your schedule' energy."
    else:
        urgency = "It's just days away -- rising urgency, 'this is almost here, lock it in' energy."
    return (f"This is a REMINDER post {days_until} days before the event. {urgency} "
            "It must read differently from the other reminders in this campaign -- new hook, "
            "new angle, never a repeat.")


def _user_prompt(event, key_details, day_of_week, post_type, days_until,
                 angle, past_examples):
    parts = [
        f"EVENT: {event}",
        f"DAY: {day_of_week}",
        f"KEY DETAILS (work these facts in accurately): {key_details}",
        f"REAL OPEN HOURS that day: {config.HOURS.get(day_of_week, 'see website')}",
    ]
    if angle:
        parts.append(f"CONTENT ANGLE for this event: {angle}")
    parts.append(_framing(post_type, days_until))
    if past_examples:
        joined = "\n---\n".join(past_examples[:4])
        parts.append("REFERENCE -- some of the bar's real past captions for voice matching "
                     f"(match the vibe, do not copy):\n{joined}")
    parts.append('Write the two captions now. Return ONLY the JSON object.')
    return "\n\n".join(parts)


def _extract_json(text: str) -> dict:
    """Pull the JSON object out of the model's reply, tolerating stray text."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("no JSON object in model response")
    return json.loads(match.group(0))


def fallback_captions(event, key_details, post_type="today", days_until=None) -> dict:
    """Simple templated captions used when the API is unavailable.

    Framing-aware so an outage still produces a sensible-sounding post. Not
    fancy -- just enough for the owner to review and rewrite by hand.
    """
    details = key_details.strip().rstrip(".") if key_details else ""
    first = details.split(",")[0].strip() if details else event
    if post_type == "today":
        when_fb, when_ig = "Tonight at", f"{event} tonight \U0001F37A"
    elif post_type == "teaser":
        when_fb, when_ig = "Tomorrow at", f"Tomorrow: {event} \U0001F37A"
    elif post_type == "vibe":
        fb = f"Just another day at {config.BUSINESS['name']} \U0001F332\U0001F37A."
        ig = "Living the backyard life \U0001F332"
        return {"fb_caption": fb, "ig_caption": ig, "_fallback": True}
    elif post_type == "spotlight":
        fb = f"Shoutout to our regulars at {config.BUSINESS['name']} -- you make this place \U0001F37A."
        ig = "Community shoutout \U0001F3AF"
        return {"fb_caption": fb, "ig_caption": ig, "_fallback": True}
    elif post_type == "carousel":
        fb = (f"Last night at {config.BUSINESS['name']} -- {event}! {details or 'Great crowd, great time.'} "
              "Wisconsin-made drinks, disc golf & hiking out back. Come see for yourself next time!")
        ig = f"Last night: {event} \U0001F37A recap"
        return {"fb_caption": fb, "ig_caption": ig, "_fallback": True}
    else:  # reminder
        lead = (f"{days_until} days out" if days_until else "Coming up")
        when_fb, when_ig = f"{lead} at", f"Mark your calendar: {event} \U0001F37A"
    fb = (f"{when_fb} {config.BUSINESS['name']} -- {event}! {details}. "
          f"All Wisconsin-made drinks, disc golf & hiking out back. See you there!")
    ig = f"{when_ig} {first}. Come hang."
    return {"fb_caption": fb, "ig_caption": ig, "_fallback": True}


def generate_captions(event, key_details, day_of_week, post_type,
                      days_until=None, past_examples=None):
    """Generate {fb_caption, ig_caption} for one post.

    Falls back to a templated caption on any error. Never raises -- the Sunday
    job must keep going even if one caption fails.
    """
    angle = config.EVENT_ANGLES.get(event)
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if anthropic is None or not api_key:
        return fallback_captions(event, key_details, post_type, days_until)

    try:
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=1024,
            system=_system_prompt(),
            messages=[{
                "role": "user",
                "content": _user_prompt(event, key_details, day_of_week,
                                        post_type, days_until, angle,
                                        past_examples or []),
            }],
        )
        text = "".join(block.text for block in resp.content
                       if getattr(block, "type", None) == "text")
        data = _extract_json(text)
        fb = str(data.get("fb_caption", "")).strip()
        ig = str(data.get("ig_caption", "")).strip()
        if not fb or not ig:
            raise ValueError("model returned an empty caption")
        # Safety net: strip any hashtags the model may have slipped in.
        ig = re.sub(r"#\w+", "", ig).strip()
        fb = re.sub(r"#\w+", "", fb).strip()
        return {"fb_caption": fb, "ig_caption": ig, "_fallback": False}
    except Exception as exc:  # any API/parse failure -> safe fallback
        print(f"[anthropic_client] caption generation failed, using fallback: {exc}")
        return fallback_captions(event, key_details, post_type, days_until)
