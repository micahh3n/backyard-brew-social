---
name: backyard-brew-posters
description: Build Backyard Brew event posters and social graphics — full-bleed real-photo posters in the bar's navy/gold identity, delivered as an editable Claude Design canvas plus finished PNGs. Trigger on any request to make a poster, flyer, event graphic, promo image, or social post image for Backyard Brew (market, bingo, karaoke, pool night, pickleball, poker, Moonlight Brews, parties, anything on the calendar). Also trigger when updating or restyling an existing Backyard Brew poster.
---

# Backyard Brew Posters

The house style for Backyard Brew event graphics, and the exact process that
produces one **without a round of revisions**. Micah's likes and dislikes are
recorded in `references/likes-dislikes.md` — read it before you draw anything.
It is the whole reason this skill exists.

**Read `backyard-brew-brand` first** for hours, event facts, voice, and the
Wisconsin-only rule. This skill owns the *visual* system only; that one owns
the truth about the business. If the two ever disagree about a fact, that one
wins.

## Non-negotiables

Break any of these and the poster comes back for rework:

1. **Full-bleed real photo.** Edge to edge, from the bar's own photo library.
   Never a shaped photo window (no arches, circles, rounded cutouts). Never
   stock, never AI-generated imagery.
2. **Navy dominant, gold loud, cream text.** `#0B1C2D` ground and scrims,
   `#C8922A` / `#F5C842` for the blocks that shout, `#F5EFD8` for type.
   No other palette, no gradients as decoration.
3. **No background patterns.** No sunbursts, rays, halftones, or textures
   behind the type. The photo is the texture.
4. **No logistics on the art.** No street address, no website, no social
   handle, no expiring "starts Aug 30" ribbon. Those go in the caption.
   Event name, day + time, one hook, one CTA. That's the whole poster.
5. **Every price renders with a real dollar sign** in anything a customer
   sees.
6. **Nothing invented.** No vendor counts, no commission claims, no
   promises the brand skill doesn't confirm.

## What you deliver, every time

- **Two artboards** on one Claude Design canvas: `Main.dc.html` at
  **1620×2160** (18×24 print at 90dpi) and `Social.dc.html` at **1080×1350**
  (4:5 feed). Same content, recomposed — not one scaled.
- **Two finished PNGs** at full size, rendered locally and sent to Micah.
- A caption **only if asked.** The poster deliberately leaves the date,
  address and handles off, so when he does ask, use `the-ghostwriter` +
  `backyard-brew-brand` and put them there.

## Process

1. **Read the event.** Get the facts from `backyard-brew-brand` —
   `references/backyard-market-brews.md` for the Sunday market, the weekly
   table for everything else. Confirm day and time before drawing.
2. **Pick the photo yourself.** Search `photos/` in the backyard-brew-social
   repo. Prefer the professional shots (people in frame, warm light) over
   phone snaps. Do not ask Micah to choose — pick, build, and show him.
3. **Crop it portrait.** `scripts/build.py crop` handles this. The poster is
   3:4; crop from the original so the subject sits in the clear middle band,
   not so the photo gets squashed to fit.
4. **Pick the display font** per `references/fonts.md`. Render the specimen
   strip yourself and choose — never ask Micah which font.
5. **Build both artboards** from `templates/`. `references/anatomy.md` has
   every measurement; follow it rather than re-deriving.
6. **Render and look at it.** `scripts/build.py render` writes both PNGs.
   **Actually read the PNG before publishing.** Half the fixes in this
   skill's history came from looking at the render, not the markup.
7. **Publish the canvas** via the `design` skill (it owns the seeding helper
   and the publish contract), then send both PNGs with `SendUserFile`.

## Pre-flight

Check every line before you hand it over:

- [ ] Photo is real, from the library, full-bleed, unshaped
- [ ] Colors are the exact brand hex values — no approximations
- [ ] Barlow Condensed for all small type; display font chosen per `fonts.md`
- [ ] Fonts embedded as data URIs, not linked (exports keep the real type)
- [ ] No address, website, handle, or expiring date on the art
- [ ] One dominant element; the eye lands somewhere on purpose
- [ ] Smallest type ≥ 15px on the poster (12pt at 90dpi)
- [ ] Still legible in grayscale
- [ ] No emoji scattered through the type — icon row only, if at all
- [ ] Both artboards say the same thing, composed for their own shape
- [ ] You looked at the rendered PNG

Any box fails, fix it before showing him.

## Files

| File | What's in it |
|---|---|
| `references/likes-dislikes.md` | **Read first.** Micah's standing preferences and the specific things he has rejected. |
| `references/anatomy.md` | Exact layout, type scale, scrim recipe, spacing for both sizes. |
| `references/fonts.md` | Display-font shortlist and how to pick one per event. |
| `templates/poster.dc.html` | 1620×2160 starting point. |
| `templates/social.dc.html` | 1080×1350 starting point. |
| `scripts/build.py` | Crop, embed fonts, build previews, render PNGs. |
| `assets/fonts/` | Every font this skill is allowed to use. |

## Keeping the copies in sync

The version in **`backyard-brew-social/.claude/skills/backyard-brew-posters/`
is canonical** — it is the one that syncs through GitHub. After editing it:

```bash
cp -r "C:/Users/micah/OneDrive/Desktop/backyard-brew-social/.claude/skills/backyard-brew-posters" "C:/Users/micah/.claude/skills/"
```
