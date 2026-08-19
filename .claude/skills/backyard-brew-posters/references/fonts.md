# Choosing the display font

Micah chose "pick the font per poster" over locking one. That means **you**
pick — from this shortlist, using the mapping below. Never ask him which
font; pick, build, and show him the finished poster.

## Fixed: everything that isn't the display font

**Barlow Condensed** — Medium (500) and Bold (700) — carries every small
line: positioning lines, feature labels, eyebrows, CTAs, contact strings.
It never changes, on any poster. It is also the fallback for a display face
when a string could be misread (see the hyphen note below).

**Pacifico never appears on a poster.** Not as a headline, not as an accent.

## The shortlist

All seven faces are bundled in `../assets/fonts/`. Embed as data URIs — never
a Google Fonts `<link>`, because PNG/PDF export drops linked webfonts and the
poster falls back to Arial.

| Face | Character | Reach for it when |
|---|---|---|
| **Lilita One** | Chunky, friendly, slightly condensed, rounded corners. The default. | Markets, family-friendly events, general calendar posts, anything where "warm and inviting" is the note. Starts every poster unless something below fits better. |
| **Alfa Slab One** | Heavy warm slab, appetite appeal. | Food-forward nights — Tacos + Poker, pizza pushes, bingo when the food is the hook. Already the brand's established food font. |
| **Titan One** | Rounder and more playful than Lilita, cartoon-adjacent. | Party nights — Moonlight Brews, holiday parties, anniversary, anything celebratory. Watch the width; long headlines run over. |
| **Anton** | Tall condensed grotesque, athletic, serious. | Competition nights — pool tournament, pickleball, disc golf league, brackets. **Never on a general event poster** — Micah finds it flat there. |
| **Shrikhand** | Quirky brush-slab with italic energy, very distinctive. | Music-forward nights — karaoke, live-music features. Long headlines get hard to read fast, so keep the string short. |
| **Barlow Condensed Bold** | — | Contact strings, and any headline where a hyphen or symbol must be unambiguous. |

## The one-shot check

Before committing, render a specimen strip of your top 2–3 candidates at the
**actual headline string and size** on the navy ground, look at it, and pick.
This takes one headless-Chrome call and it is the difference between one shot
and a revision round. `scripts/build.py specimen` does it.

What you are checking for:

- Does the full event name fit the content width at the target size?
- Does it still read at a glance, or does the character get in the way?
- Do hyphens, ampersands, and numerals look right? (Lilita One's hyphen sits
  high and long — `backyard-brew.com` reads like an en-dash. Any string with
  a hyphen goes in Barlow Condensed Bold instead.)

## Fallback stacks

Give every face a real fallback, in case a copy of this skill lands somewhere
the bundled fonts didn't follow:

```css
font-family: 'Lilita One', 'Arial Black', Impact, sans-serif;   /* any display face */
font-family: 'Barlow Condensed', 'Arial Narrow', Arial, sans-serif;
```

## Adding a face

Only if a genuinely new note is needed — the list is deliberately short so
posters stay recognizable as a family. Download the TTF from Google Fonts by
resolving the real URL first (the versioned paths change):

```bash
curl -sfL -A "Mozilla/5.0" "https://fonts.googleapis.com/css2?family=Font+Name&display=swap" | grep -o "https://fonts.gstatic.com/[^)]*"
```

Drop the TTF in `../assets/fonts/` and add a row to the table with the note it
covers and when to reach for it.
