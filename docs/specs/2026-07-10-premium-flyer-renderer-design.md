# Design: Premium HTML/CSS Flyer Renderer (replaces the PIL flyer templates)

Date: 2026-07-10
Status: Approved (validated live via rendered mockups in conversation before this doc was written)

## Goal / success criteria

Replace the flat, amateurish PIL-drawn flyer templates (`_build_flyer`, `_build_flyer_minimal`,
`_build_flyer_poster` in `process_photos.py`) with HTML/CSS rendered through a headless browser,
per the technique validated live in this session (two real candidate renders shown to the owner
using an actual dropped-in photo; owner approved, with an explicit requirement that spacing must
never let elements overlap). This directly serves the owner's stated goal: posts that make
customers "stop scrolling," look like a professionally designed poster, and never look like
"Google Docs" or "one second in Canva."

This design follows the `premium-photo-forward-design` and `backyard-brew-brand` skills
(`.claude/skills/` in the user's home project) — those skills are the durable design reference;
this doc is the integration spec for wiring the technique into the real Sunday automation.

## Current state

- `process_photos.py`'s `process()` dispatches on `mode` (from `resolve_mode()`): `premade_art`
  (untouched passthrough), `none` (light PIL polish), `logo` (PIL watermark), `text_overlay`/
  `both` (PIL-drawn flyer: badge/minimal/poster, chosen by `choose_template()`, optionally with
  `_add_deal_callout()`'s real-photo badge composited on top).
- The `text_overlay`/`both` PIL rendering path is what's being replaced. `premade_art`, `none`,
  and `logo` modes are untouched — they don't need HTML sophistication (passthrough, light
  polish, and a watermark are already correctly simple).
- `ensure_fonts()`/`FONT_FILES` download local TTF files so PIL's `ImageFont.truetype` can draw
  text — this whole mechanism becomes unnecessary once text is drawn by a real browser's font
  engine via `@import`.
- `generate_captions.py`'s `render_generated_images()` calls `process_photos.process(...)` with
  `platform_key="ig_feed"` (1080×1080) as the only real call site in production.
- The Sunday job runs on GitHub Actions `ubuntu-latest`, which has **no browser installed by
  default** — this is a new operational requirement this design must account for.

## Approach

### Rendering engine: Playwright, not a hardcoded Chrome path

The live mockups in this session were rendered by shelling out to a hardcoded
`chrome.exe` path — fine for local Windows exploration, but not portable to the Linux CI runner
that actually executes the Sunday job. **Use Playwright** (`pip install playwright`, then
`playwright install --with-deps chromium` in CI) instead of a raw subprocess call to a
platform-specific browser path:
- Cross-platform (same code path on the owner's Windows machine and GitHub Actions' Linux
  runner).
- pip-installable, well-supported, actively maintained.
- Provides a clean Python API (`sync_playwright().chromium.launch()` → `page.set_viewport_size()`
  → `page.goto(file_url)` → `page.screenshot()`) instead of parsing subprocess output.

This adds Chromium's download (~150-300MB) to the Sunday job's setup step, adding roughly a
minute to a job that runs once a week — an acceptable tradeoff for real design quality.

### New module: `scripts/flyer_render.py`

Owns everything the old PIL flyer-building code did, rebuilt on the new technique:

- **Photo prep:** `prep_photo(src_path, out_path, size, centering)` — EXIF-orientation-correct
  (`ImageOps.exif_transpose`) and crop-to-cover via PIL, exactly as documented in
  `premium-photo-forward-design/scripts/render.py`. Required before any photo is referenced from
  HTML — CSS `background-image` does not read EXIF rotation, so skipping this renders sideways
  photos (a real bug hit during live testing this session).
- **Two layout archetypes** (replacing badge/minimal/poster's three-way rotation with two
  higher-quality options — see "Why two, not three" below):
  1. **`full_bleed`** — the primary/default. Photo fills the entire canvas; a bottom gradient
     scrim (not a solid box) holds an eyebrow label, bold headline, accent rule, and detail line;
     fine film grain; subtle CSS `filter` color grade; small wordmark bottom-right. This is
     "Option A" from the live mockup session, which the owner explicitly preferred.
  2. **`editorial_split`** — secondary variety option. Dedicated navy type panel (left ~38%) +
     photo (right ~62-66%) with its own edge fade. This is "Option B" from the live session.
  Chosen deterministically per (event, date) the same way `choose_template()` worked before —
  same event+date always picks the same layout on re-runs, different dates vary.
- **Deal-photo inset is a first-class part of each layout's own HTML, not a bolted-on second
  compositing pass.** This is the direct fix for the real collision bug found in production
  during this session (a deal badge's opaque box only partially covered a template's own footer
  text, leaving a garbled fragment visible). Each layout template defines its own reserved
  deal-inset slot *inside* the region it already controls (e.g. `full_bleed` places it inside the
  bottom scrim, stacked above or beside the text rather than guessing at a fixed offset that
  might collide with whatever else is in that corner) — so there is no second absolute-positioned
  element for two features to independently miscalculate around. When no deal photo is provided,
  that slot in the HTML is simply omitted.
- **HTML generation** as Python functions returning template strings (one function per layout
  archetype), substituting real event copy and the brand's exact colors/fonts from the
  `backyard-brew-brand` skill (already mirrored in `config.py` — pull from there, not
  re-hardcoded, so the two stay in sync).
- **Render:** call into Playwright directly (not shelling out to the skill's `render.py`, which
  is a local dev-convenience script using a hardcoded Chrome path — production needs the
  Playwright path for CI portability). Write the generated HTML to a temp file, screenshot at
  the exact target size, clean up the temp file.

### Why two layout archetypes, not three

The old system rotated three PIL templates for variety. Of the two new candidates validated live,
both are considerably higher quality than any of the three old ones — better to ship two
genuinely excellent layouts than stretch to a third built quickly to hit a round number. A third
archetype can be added later following the same skill/pattern once there's real signal on what
additional variety would help (this is explicitly a future option, not a gap).

### Integration point: `process_photos.py` stays the entry point

`process()`'s `mode` dispatch is unchanged in shape — `premade_art`/`none`/`logo` still go
through existing PIL code (still correct for those cases). Only the `text_overlay`/`both`
branches change to call into `flyer_render.py` instead of the old `_build_flyer*` functions.
`generate_captions.py`'s `render_generated_images()` and its call signature to
`process_photos.process(...)` do not change at all — this is purely an internal swap of *how*
`text_overlay`/`both` gets rendered, invisible to every other part of the pipeline.

### Dead code removal

Once `text_overlay`/`both` route through `flyer_render.py`, the following become unused and
should be deleted from `process_photos.py`: `_build_flyer`, `_build_flyer_minimal`,
`_build_flyer_poster`, `_autosize_headline`, `_add_deal_callout`, `choose_template`,
`FLYER_TEMPLATES`, `ensure_fonts`, `FONT_FILES`, `_headline_font`. Keep `_fit_cover`,
`_fit_contain`, `_auto_polish`, `_add_logo`, `resolve_mode`, `output_name`, `_hex` — still used
by the surviving `premade_art`/`none`/`logo` modes (confirm each at implementation time rather
than assuming; don't delete something still referenced).

## Testing strategy

Playwright/Chromium must be installed in the dev/test environment for these tests to run (same
as CI) — this is a new local setup requirement, not just a CI one. Tests should:
- Verify `prep_photo()` corrects orientation and produces the exact target size (fast, no
  browser needed — pure PIL).
- Verify the HTML-generating functions produce valid, complete markup containing the expected
  event/detail/day text, and that omitting `deal_photo_path` omits the deal-inset markup
  entirely (string-level assertions, no browser needed — fast, the bulk of the test coverage).
- A smaller number of real end-to-end tests that actually render through Playwright and assert
  on the output image's pixel dimensions (these are slower and require the browser install, but
  are the only way to catch a real rendering-pipeline break — keep them minimal and targeted,
  not the primary coverage mechanism).
- A **collision regression test** mirroring the exact bug fixed today: render `full_bleed` with
  a deal photo present and assert the output image dimensions are correct and the render
  succeeds without exception — full pixel-level layout assertions aren't practical for a
  screenshot, but a working render with a deal photo present, produced by the same code path
  used for the header-only case, is the meaningful regression signal here since the fix is
  structural (one shared layout, not two independently-positioned elements).

## Operational changes

- `requirements.txt` gains `playwright`.
- `.github/workflows/sunday-generate.yml` gains a `playwright install --with-deps chromium` step
  after `pip install -r requirements.txt`.
- No change to the owner's weekly workflow (`HOW-TO-USE-WEEKLY.md`) — this is purely an internal
  rendering-quality upgrade; the owner still just drops photos, reviews the preview page, and
  manually schedules. Worth a one-line mention in the doc that flyer visuals got a redesign, nice
  to have but not required for correctness.

## Explicitly out of scope

- A third layout archetype (noted above as a future option).
- Changing `editorial_split`'s photo-to-panel ratio or adding more layout variety knobs.
- Any change to the `ig_story`/`fb_feed`/`fb_cover` dimension entries in `config.DIMENSIONS` —
  production only ever renders `ig_feed` (1080×1080) today; the new layouts are built
  proportionally (percentage-based CSS) so they would reasonably adapt, but that adaptation
  isn't being verified since nothing calls those dimensions yet.
- Updating the live backyard-brew.com website's incorrect Sunday hours — noted as a separate,
  unrelated follow-up.
