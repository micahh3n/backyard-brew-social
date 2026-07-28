---
description: Write a Gemini Image prompt for a promo graphic, then the captions to go with it
argument-hint: [what the graphic is for, e.g. "bingo night this monday"]
---

Produce a promotional graphic prompt for Backyard Brew: $ARGUMENTS

## Do this

1. Read the `backyard-brew-brand` skill and
   `references/graphics-workflow.md`. The nine-block prompt structure is
   there. Follow it.
2. Get the facts right from `recurring_events.csv` or `posts.csv`. Never
   invent a time or a price to make a layout work.
3. Ask which photo he is using, if it is not clear. The prompt has to describe
   what is actually in that photo, otherwise Gemini invents a different venue.

## Deliver, in this order

**1. The prompt.** One copy-paste block of prose, not a numbered list. It must
cover all nine blocks from `graphics-workflow.md`:

- 4:5 vertical
- Build on the attached real photo, described specifically
- Retro outdoor badge, vintage national park meets craft brewery
- The exact hex colors
- The typography direction
- The exact text strings in quotes, as few words as possible
- An empty circular badge area reserved for the logo, left completely blank
- The anti-slop negatives
- The realism anchors

**2. What to attach.** Which photo file, plus the logo from `assets/logo/`.

**3. The captions.** Facebook and Instagram, following
`references/caption-voice-rules.md`. Genuinely different angles, not one
shortened. Hashtags listed separately for the first comment.

**4. The proofread reminder.** One line: check spelling in the image, check
for AI distortion, check it sounds like Backyard Brew.

## If Gemini keeps failing

After two or three bad attempts, stop and offer the local renderer instead.
`scripts/flyer_render.py` builds the flyer in HTML and CSS and renders it
through Playwright with the real fonts and the real logo. Text comes out
correctly spelled and exactly on-brand because a browser drew it rather than a
model. Best choice for anything text-heavy.
