# Graphics Workflow

How to produce a promotional graphic for Backyard Brew that looks designed
rather than generated. This is the Claude-facing half. The human half, the
click-by-click steps at the computer, is `playbook/2-MAKE-A-GRAPHIC.md`.

The process was developed by the owner's son and produced the graphics the
business is known for. Follow it rather than improvising a new one.

---

## The pipeline

1. **Claude writes a Gemini Image prompt** (this file).
2. Human pastes the prompt into Gemini Image along with a real photo of the
   bar or the event, plus the logo file.
3. Human takes the result to ChatGPT to remove Gemini's bottom-right
   watermark.
4. Human opens it in Canva and lays the real logo over the reserved circle.
5. Human downloads and names it.
6. **Human proofreads before it goes anywhere.** Spelling, AI distortion,
   whether it sounds like Backyard Brew.
7. **Claude writes the Facebook and Instagram captions** (see
   `caption-voice-rules.md`).

Steps 1 and 7 are the ones to get right here.

---

## Writing the Gemini prompt

Do not hand over a one-line prompt. Every prompt covers all nine blocks
below, in this order. Write it as a single block of prose the human can copy
in one go, not a numbered list they have to reassemble.

### 1. Format
Always **4:5 vertical**. State it explicitly in the prompt. This is the
non-negotiable aspect ratio for both Facebook and Instagram feed posts.

**Say what orientation the source photo is, and how to reconcile it.** Most
candids in `photos/` are horizontal, so this applies to nearly every prompt.
When the attached photo is landscape, tell the generator to **extend the frame
vertically — more sky above, more ground or paving below — and to keep the
subject intact and unstretched.** Left unsaid, a "4:5 vertical" instruction
over a wide subject invites the generator to crop the subject down to a
fragment or to invent filler. Do not let it stretch to fit either.

### 2. Base the image on the real photo
The attached photo is the source of truth for the space, not a mood
reference. Say so: use the actual bar, the actual course, the actual people
in the photo. Do not let the generator invent a different venue.

Name what is actually in the frame. If the photo shows the tap wall, say tap
wall. If it shows the first tee at golden hour, say that. Vague prompts
produce generic bars.

### 3. Style
Retro outdoor badge, vintage national park poster meets craft brewery. Bold,
warm, slightly rugged. Explicitly not sleek, not tech, not cute, not trendy.

### 4. Exact colors
Give the hex values, never color names alone:
- Deep Navy `#0B1C2D` dominant
- Gold/Amber `#C8922A` accent, borders, highlights
- Warm Yellow `#F5C842` sparingly, for energy
- Cream `#F5EFD8` text on dark
- Disc Blue `#4A90C4` supporting details only

### 5. Typography
Bold condensed display for the headline in the spirit of Anton. Condensed
sans for details in the spirit of Barlow Condensed. For food-forward events
(Bingo, Tacos + Poker) a heavy slab in the spirit of Alfa Slab One works for
the headline. Script styling never carries a headline.

### 6. Text, spelled out exactly and kept short
This is where AI graphics fail. Every rendered word is a chance for a
misspelling or mangled letterform.

- Put the **fewest possible words** in the image. Event name, day, time. That
  is usually all.
- Write each string in the prompt **in quotes, spelled exactly** as it must
  appear.
- Push everything else into the caption, where it cannot be misrendered.
- Never ask for a paragraph, a list of details, or small print in the image.

### 7. Reserve a circle for the logo
Do not ask Gemini to draw the Backyard Brew logo. It will approximate it and
the approximation is always wrong.

Instead, ask for **a clean empty circular badge area** in the composition,
sized and placed as a logo lockup, in navy or gold, with nothing inside it.
The human drops the real logo onto that circle in Canva. Say in the prompt
that the circle must be left completely empty.

### 8. Anti-slop negatives
State these as things to avoid:
- No AI gloss, no plastic skin, no waxy over-smoothed faces
- No warped hands, no extra fingers, no distorted limbs
- No fake or garbled text anywhere outside the exact quoted strings
- No stock-photo staging, no generic crowd of models
- No invented logos, no invented beer brands, no readable labels that are not
  real Wisconsin products
- No dreamy haze, no lens flare pile-up, no HDR halo

### 9. Realism anchors
Ask for real photographic texture: natural light, real grain, imperfect
surfaces, actual wear on the wood and the grass. The target is a poster
designed over a real photograph, not an illustration of a bar.

---

## Rules that override the template

- **Wisconsin only.** No non-Wisconsin brand may appear or be implied. If a
  can or tap handle would be legible, specify that it is a Wisconsin product
  or that labels are not readable.
- **Never mention breakfast.** Discontinued 2026-07-26.
- **Facts before flourish.** Times, prices, and details come from
  `recurring_events.csv` and the parent skill. Never guess a time to make a
  layout work.
- **Match the event's angle.** Each recurring event has one, listed in the
  parent skill. A Bingo graphic leads with the prize. A Pickleball graphic
  leads with the challenge.

---

## The backup path, when Gemini will not cooperate

The repo already renders brand-exact flyers locally with no AI involved:
`scripts/flyer_render.py` builds HTML/CSS templates and renders them through
Playwright, using the real fonts in `assets/fonts/` and the real logo in
`assets/logo/`.

Use it when:
- Gemini keeps misspelling the text
- The output has visible distortion that will not go away
- The graphic is text-heavy, where a browser's layout engine beats a model
- Nobody has Gemini access that day

Text rendered this way is always correctly spelled and always the exact brand
color, because a browser drew it. Setup is `pip install -r requirements.txt`
followed by `playwright install chromium`.

---

## After the image is done

Write the captions. Facebook and Instagram take genuinely different angles on
the same facts, per `caption-voice-rules.md`. Do not write one and shorten it.

Remind the human to proofread the image before posting: spelling, distortion,
and whether it actually sounds like Backyard Brew. The son caught problems at
this step every week, and it is the reason the graphics looked right.
