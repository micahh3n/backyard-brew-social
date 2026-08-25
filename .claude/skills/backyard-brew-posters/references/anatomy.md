# Poster anatomy: the MARKET recipe

> **This is one composition, not the house template.** It is the Sunday
> Market & Brews layout and the numbers below are what survived review *for
> that poster*. Every night gets its own structure — see "The reskin
> correction" in `likes-dislikes.md` for the rule and for what has already
> been built. Reuse the palette, the frame, the logo weight and the type
> scale here as reference values; do not reuse the stack.

Exact values. Use them rather than re-deriving — the numbers below are what
survived review.

## Canvas

| | Poster | Social |
|---|---|---|
| Size | 1620 × 2160 (18×24 at 90dpi) | 1080 × 1350 (4:5) |
| Outer padding | `92px 104px 84px` | `60px 64px 54px` |
| Gold frame inset | `40px`, `3px solid rgba(200,146,42,0.9)` | `26px`, `2px` |
| Root layout | `flex column`, `justify-content: space-between` | same |

The root is a fixed-size `position: relative` div. Everything stacks on it in
this order:

1. `<img>` — `position:absolute; inset:0; object-fit:cover`. Poster uses
   `object-position: 50% 50%`, social `50% 52%`.
2. Top scrim (see below)
3. Bottom scrim
4. Flat tint: `rgba(11,28,45,0.14)` — unifies the photo with the palette
5. Gold frame border
6. Content flex column (`position: relative`)

## Scrims

Type sits on the scrims; the photo shows through clean in the middle. Tune the
stops to the photo, but start here:

```css
/* top */
linear-gradient(180deg,
  rgba(7,19,32,0.95) 0%, rgba(7,19,32,0.90) 24%,
  rgba(7,19,32,0.42) 38%, rgba(7,19,32,0) 49%);

/* bottom */
linear-gradient(0deg,
  rgba(7,19,32,0.97) 0%, rgba(7,19,32,0.93) 19%,
  rgba(7,19,32,0.36) 32%, rgba(7,19,32,0) 42%);
```

Social runs a couple of points later on both (`25%/42%/53%` and
`20%/33%/43%`) because the shorter canvas needs a taller clear band
proportionally.

## Top block, in order

| Element | Poster | Social |
|---|---|---|
| Logo (`bb-logo.png`) | 232px square | 156px |
| Qualifier line (`BACKYARD`) | display font, 112px, `letter-spacing .06em`, cream | 76px |
| Event name (`MARKET & BREWS`) | display font, 150px, `#F5C842` | 102px |
| — line-height on the pair | `0.9` | `0.9` |
| Gold time bar | display font 84px navy on `#F5C842`, padding `17px 60px 13px` | 58px, `12px 40px 9px` |
| Positioning line | Barlow Bold 40px, `letter-spacing .15em`, uppercase, cream | 27px, `.14em` |

Headline text-shadow: `0 8px 30px rgba(4,12,21,0.7)` (cream line),
`0 10px 34px rgba(4,12,21,0.75)` (gold line). Small type over photo gets
`0 4px 16px rgba(4,12,21,0.85)`.

The time bar separator is an inline SVG rhombus, never a bullet character:

```html
<svg width="25" height="25" viewBox="0 0 18 18"><path d="M9 0 18 9 9 18 0 9Z" fill="#0B1C2D"></path></svg>
```

## Bottom block, in order

**Feature row** — 3-up CSS grid, `repeat(3, minmax(0,1fr))`, middle column
carries `border-left`/`border-right: 2px solid rgba(200,146,42,0.55)` as
dividers. Column padding `10px 16px 12px` (poster) / `7px 10px 8px` (social).
Each column: emoji then label.

- Emoji: `font-size: 84px` poster / `56px` social, `line-height: 1.1`, with
  `font-family: 'Apple Color Emoji','Segoe UI Emoji','Noto Color Emoji',sans-serif`
- Label: Barlow Bold 36px / 24px, `letter-spacing .14em`, uppercase, cream

**Brand-voice line** — Barlow Medium 40px / 27px, `rgba(245,239,216,0.86)`.

**Gold callout block** — full content width, `background:#F5C842`,
`border: 5px solid #0B1C2D` (4px social), `box-shadow: 0 20px 50px rgba(4,12,21,0.6)`,
padding `24px 40px 22px` / `17px 26px 15px`. Three stacked lines:

| Line | Poster | Social |
|---|---|---|
| Eyebrow | Barlow Bold 32px, `.2em`, `rgba(11,28,45,0.82)` | 22px, `.17em` |
| Headline | display font 114px, navy | 78px |
| CTA | Barlow Bold 40px, navy | 27px |

Gaps: outer column `gap: 30px` (poster) / `20px` (social); inside the gold
block `gap: 9px` / `6px`.

## Rules the numbers encode

- **One dominant element.** The event name is usually it. If a second block
  has to shout (a "NO VENDOR FEE" style callout), size it *below* the event
  name — around 114px against 150px — and let the solid gold ground do the
  work instead of the point size.
- **Minimum type** is 15px on the poster (12pt at 90dpi). Nothing goes below.
- **Layout with flex/grid and `gap`**, never margins between siblings — it
  survives direct manipulation in the canvas editor.
- **Copy is literal text in the markup**, never a template binding, so Micah
  can retype it in place in the editor.
- **Colors are inline styles**, so the properties panel can edit them.

## Brand palette (exact)

| Role | Hex |
|---|---|
| Ground, scrims, text on gold | `#0B1C2D` |
| Deeper ground (scrim base) | `#071523` |
| Frame, dividers, eyebrows | `#C8922A` |
| Loud blocks, event name | `#F5C842` |
| Text on navy | `#F5EFD8` |
