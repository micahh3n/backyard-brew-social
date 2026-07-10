# Design: 4:5 Format, Single Layout, and Photo-Cutout Decorations for Flyers

Date: 2026-07-10
Status: Approved (validated live via a rendered mockup in conversation before this doc was written)

## Goal / success criteria

Follow-up to `2026-07-10-premium-flyer-renderer-design.md`. After seeing the first batch of
real renders (Bingo, Pickleball, Thursday, Karaoke) from that redesign, the owner gave three
pieces of feedback:

1. He prefers the `full_bleed` layout (photo-first, gradient scrim) over `editorial_split`
   (solid navy side panel) — called the navy panel out by name as the one he doesn't want.
2. The new flyers, while premium, lost the "heart"/personality the old amateurish flyers had.
   Asked directly which specific element carried that personality (logo badge, hand-lettered
   font, busier color palette, or the illustrated decorative extras), he confirmed: the
   **decoration/illustrated character**, not the other three.
3. Asked whether 1:1 square is actually the best format for social — it isn't; since posting is
   now manual (owner pastes into FB/IG's own composer, per the manual-posting redesign), there's
   no technical reason to stay locked to square. 4:5 portrait (1080×1350) claims more feed real
   estate on Instagram/Facebook than 1:1.

This design makes three changes: switch the default canvas to 4:5 portrait, retire
`editorial_split` so `full_bleed` is the only layout, and add an optional per-flyer decorative
photo accent that restores personality without returning to the old clip-art look.

## Current state

- `scripts/flyer_render.py` has two layout archetypes (`full_bleed`, `editorial_split`), chosen
  deterministically per `(event, date)` by `choose_layout()`, both hardcoded to a 1080×1080
  canvas regardless of the `size` argument passed to `render_flyer()` (documented limitation,
  see the function's docstring).
- The footer/detail-text collision bug in `editorial_split` was already found and fixed this
  session (commit `38b1951`) — moot once `editorial_split` is retired, but noted so the retirement
  doesn't get mistaken for reverting that fix.
- `config.DIMENSIONS["flyer"]` and `config.DIMENSIONS["ig_feed"]` are both `(1080, 1080)`;
  `generate_captions.py` calls `process_photos.process(..., platform_key="ig_feed")` as the only
  real call site in production.
- `recurring_events.csv` already has the corrected Thursday/Friday event names (`Ladies Night +
  Line Dancing`, `Karaoke Night`) — that data is current. However `config.EVENT_ANGLES` (used only
  for picking a caption angle, a separate lookup from the flyer path) still has the old combined
  names (`Disc Golf League + Ladies Night`, `Line Dancing + Karaoke Night`) and needs updating to
  match, since the decoration keyword-matching added here reads the same `event` string.
- **Separately discovered, not part of this design:** `recurring_events.csv`'s Thursday row
  points to `default_photos=line dancing_default_artpg` (missing a `.` and not matching any
  actual file in `photos/` — the real file is `Backyard Thursdays_default_art.jpg`). This is a
  broken reference the owner should fix in the CSV; flagging it here since it was found during
  this work, but the fix itself is out of scope for this spec.
- No background-removal capability is available in this environment: the connected Higgsfield
  MCP is at 0 credits (image generation and background removal both run on that balance), and the
  two free local alternatives (`rembg`, OpenCV) fail to install because this Python is Windows
  ARM64 with no C/C++ build toolchain. A live prototype (Wednesday Tacos + Poker Club flyer, real
  photo the owner sent, circular CSS clip-path) was built and approved as the way to get
  decoration into flyers without true alpha-channel cutout.

## Approach

### Canvas: 1080×1080 to 1080×1350

`config.DIMENSIONS["flyer"]` changes to `(1080, 1350)`. `flyer_render.py`'s `full_bleed` HTML/CSS
template's `.canvas`/`body` fixed pixel values change from `1080px` square to `1080px × 1350px`,
and the bottom-scrim/content-block proportions are re-tuned for the taller canvas (validated
values from the live prototype: scrim height ~52% instead of ~60%, content `bottom` offset ~76px,
headline `font-size` ~96px — close to current but re-checked against the taller frame rather than
assumed identical). `ig_feed` stays `(1080, 1080)` unchanged — nothing currently calls it through
the flyer path, but it's a different, real Instagram surface (square feed post) that shouldn't be
silently repurposed.

### Layout: retire `editorial_split`

Delete `_editorial_split_html()`, the `LAYOUTS` list, and `choose_layout()`'s rotation logic —
`render_flyer()` calls `_full_bleed_html()` directly. The `layout` override parameter on
`render_flyer()` (currently used by tests to force a specific layout) becomes moot with only one
layout and should be removed rather than kept as dead flexibility — if a second layout is wanted
later, it should be designed against real need at that time (same reasoning the original spec
used for "why two, not three").

### Decoration system

**What it is:** an optional circular photo accent — not a true alpha-channel cutout (blocked, see
above) but a CSS `border-radius:50%` + `overflow:hidden` clip around a normal cropped photo,
finished with a gold ring border, drop shadow, and a slight rotation, positioned top-right in the
photo area (clear of the bottom scrim/text). Validated live: a close crop of a real taco photo
the owner sent reads as a clean "featured dish" seal, not a janky cutout, because the object's own
plate/background (checkered paper) fills the circle naturally. This works well for
already-plated/contained subjects (food in a basket, a paddle held up close); it will read worse
for a busy, uncontained subject (e.g., a paddle mid-swing with a crowd behind it) — true cutout
removal would matter more there, and stays blocked until credits or a local toolchain are
available.

**Asset convention:** `assets/decorations/<name>.png` (or `.jpg` — no alpha channel is required by
this technique). One file per object. This is a new directory; nothing reads from `assets/` today
except `assets/logo/`.

**Event-to-decoration mapping:** a small dict in `flyer_render.py`, keyed by a lowercase keyword
match against the `event` string, e.g.:

```python
DECORATION_KEYWORDS = {
    "bingo": "bingo.png",
    "pickleball": "pickleball.png",
    "poker": "taco.png",       # "Tacos + Poker Club"
    "taco": "taco.png",
    "line dancing": "boots.png",
    "ladies night": "boots.png",  # same night as line dancing per recurring_events.csv
    "karaoke": "mic.png",
    "league": "disc.png",
}
DECORATION_DEFAULT = "beer_pint.png"
```

First keyword match (case-insensitive substring) wins; no match falls back to
`DECORATION_DEFAULT`. If the resolved asset file doesn't exist on disk, the decoration is skipped
silently (same pattern already used for a missing/absent `deal_photo_path` — a flyer must never
fail to render because decoration art is missing).

**Not mandatory:** `render_flyer()` gains an optional `decoration_path=None` parameter (mirroring
`deal_photo_path`'s existing optional pattern). Callers may pass `None` explicitly to skip
decoration even when a keyword would otherwise match, for weeks the owner wants a plainer flyer.
`process_photos.py`'s call site resolves the path from the keyword map by default.

**Sourcing the actual asset images (separate follow-up, not blocked on this spec):** a mix of
owner-submitted real photos (like the taco photo used in the validated prototype) and
Higgsfield-generated photoreal placeholders once credits are available. Both land at the same
`assets/decorations/<name>.png` path — the code has no way to distinguish "real" from
"placeholder" and doesn't need to. The initial ship of this feature can go out with a partial or
even empty `assets/decorations/` folder; every flyer simply renders without a decoration until
files are dropped in, per the "skip silently if missing" rule above.

## Testing strategy

- `full_bleed`'s HTML-generation tests get their expected canvas dimensions updated from
  1080×1080 to 1080×1350.
- All `editorial_split`-specific tests (HTML generation, the footer-collision regression test
  fixed today) are deleted along with the code they test.
- New tests for the decoration system, no browser required (string-level, fast):
  - Keyword matching resolves the right filename for a representative sample of event strings
    (including a no-match case falling back to the default).
  - A missing decoration asset file produces HTML with no decoration markup, not an exception.
  - `decoration_path=None` passed explicitly produces no decoration markup even when the event
    string would otherwise match a keyword.
- One end-to-end Playwright test (mirroring the existing minimal smoke-test pattern) rendering
  with a real decoration image present, asserting the render succeeds and output dimensions are
  1080×1350.

## Operational changes

None beyond what the previous flyer-renderer spec already put in place (Playwright/Chromium is
already installed in CI and documented locally). No change to `HOW-TO-USE-WEEKLY.md` is required
by this spec — decoration is invisible plumbing from the owner's side until asset files exist.

## Explicitly out of scope

- True alpha-channel background removal (blocked on Higgsfield credits / no local compiler
  toolchain on this ARM64 Windows Python). Revisit if either unblocks.
- Producing the actual decoration image files (`bingo.png`, `taco.png`, etc.) — separate,
  photo-sourcing work, mixing owner-submitted photos and later Higgsfield generations.
- Fixing `config.EVENT_ANGLES`'s stale Thursday/Friday combined-event-name keys — noted above as
  needed, but it's a caption-angle lookup fix, not a flyer/decoration change; do it as its own
  small follow-up.
- Fixing `recurring_events.csv`'s broken Thursday `default_photos` filename reference — flagged
  for the owner, not fixed here.
- Changing `ig_story`/`fb_feed`/`fb_cover` dimensions or adding a format-selection knob — 4:5
  becomes the one flyer default; nothing today calls the other `DIMENSIONS` entries through this
  path.
