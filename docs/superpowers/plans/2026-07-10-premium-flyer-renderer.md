# Premium Flyer Renderer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `process_photos.py`'s flat, PIL-drawn flyer templates (badge/minimal/poster) with a new HTML/CSS + Playwright renderer producing premium, photo-forward social graphics, per the design validated live in conversation and codified in the `premium-photo-forward-design` / `backyard-brew-brand` skills.

**Architecture:** A new module `scripts/flyer_render.py` owns everything: EXIF-correcting and cropping real photos, building one of two HTML/CSS layout archetypes (`full_bleed`, `editorial_split`) with the deal-photo inset as a normal-flow flexbox child (not a second absolute-positioned compositing pass — this is the structural fix for the real collision bug found earlier today), and rendering via Playwright. `process_photos.py`'s `process()` keeps its exact public signature and `mode` dispatch shape; only the `text_overlay`/`both` branches change internally to call the new module instead of PIL drawing functions, which get deleted as dead code.

**Tech Stack:** Python 3.11/3.12, Playwright (`sync_playwright`, chromium), Pillow (photo prep only, no more text drawing), pytest.

## Global Constraints

- Real photo is always the hero — never covered by more than ~40% opaque shape; text sits in gradient scrims or genuine negative space, never a solid box that competes with the photo.
- Deal-photo inset must be laid out via CSS flow (flexbox), not independently-positioned absolute coordinates, so it structurally cannot collide with a layout's own text.
- Photos must be EXIF-orientation-corrected before being referenced as a CSS `background-image` — Chrome does not read EXIF rotation.
- Colors/fonts come from `config.COLORS` / the brand's established Google Fonts (Anton, Barlow Condensed) — never hardcoded independently of `config.py`.
- `process_photos.process()`'s public signature (`input_path, out_path, platform_key, enhance_col, event, key_details, day_of_week, date_str, deal_photo_path`) does not change — callers (`generate_captions.py`) are unaffected.
- Never raise on a rendering failure that can be avoided — but note Playwright rendering is a harder dependency than PIL was; a Chromium/Playwright install failure is a real environment problem the Sunday job should surface loudly (via the job failing), not silently degrade into a broken image.

---

### Task 1: `scripts/flyer_render.py` — HTML/CSS layouts + Playwright rendering

**Files:**
- Create: `scripts/flyer_render.py`
- Test: `scripts/test_flyer_render.py`

**Interfaces:**
- Consumes: `config.COLORS` (dict of hex strings), `config.DIMENSIONS` (not directly — caller passes `size` explicitly).
- Produces: `flyer_render.choose_layout(event: str, date_str: str) -> str`, `flyer_render.prep_photo(src_path, out_path, size=(1080,1080), centering=(0.5,0.4)) -> str`, `flyer_render.render_flyer(photo_path, event, key_details, day_of_week, date_str, out_path, size=(1080,1080), deal_photo_path=None, layout=None) -> str`. Consumed by Task 2's `process_photos.py`.

- [ ] **Step 1: Install Playwright + Chromium in this dev environment (required before any test in this task can run)**

Run: `pip install playwright && playwright install chromium`
Expected: downloads complete without error (Chromium is ~150-300MB; this is a one-time local setup cost, same as what Task 3 adds to CI).

- [ ] **Step 2: Write the failing tests**

Create `scripts/test_flyer_render.py`:
```python
import html as html_mod
import os

from PIL import Image

import config
import flyer_render as fr


def _dummy_photo(path, color=(120, 150, 90), size=(1600, 1200)):
    Image.new("RGB", size, color).save(path)


def test_choose_layout_is_deterministic_for_same_input():
    a = fr.choose_layout("Bingo Night", "2026-07-14")
    b = fr.choose_layout("Bingo Night", "2026-07-14")
    assert a == b


def test_choose_layout_varies_across_dates():
    layouts = {fr.choose_layout("Bingo Night", f"2026-07-{d:02d}") for d in range(1, 29)}
    assert len(layouts) > 1
    assert layouts <= set(fr.LAYOUTS)


def test_prep_photo_produces_exact_target_size(tmp_path):
    src = tmp_path / "wide.jpg"
    _dummy_photo(str(src), size=(2400, 800))  # very wide source, needs real cropping
    out = tmp_path / "prepped.jpg"
    fr.prep_photo(str(src), str(out), size=(1080, 1080))
    result = Image.open(out)
    assert result.size == (1080, 1080)


def test_full_bleed_html_contains_event_day_and_detail():
    out = fr._full_bleed_html("file:///photo.jpg", "Bingo Night", "10 rounds, free to play",
                              "Monday")
    assert "BINGO NIGHT" in out
    assert "MONDAY" in out
    assert "10 rounds" in out


def test_full_bleed_html_escapes_special_characters():
    out = fr._full_bleed_html("file:///photo.jpg", "Rock & Roll Night", "Free w/ <beer>",
                              "Friday")
    assert "&amp;" in out
    assert "<beer>" not in out
    assert html_mod.escape("Free w/ <beer>") in out


def test_full_bleed_html_omits_deal_row_when_no_deal_photo():
    out = fr._full_bleed_html("file:///photo.jpg", "Bingo Night", "details", "Monday",
                              deal_photo_uri=None)
    assert "deal-row" not in out


def test_full_bleed_html_includes_deal_row_when_deal_photo_given():
    out = fr._full_bleed_html("file:///photo.jpg", "Bingo Night", "$2 off Spotted Cow", "Monday",
                              deal_photo_uri="file:///deal.jpg")
    assert "deal-row" in out
    assert "file:///deal.jpg" in out
    assert "Spotted Cow" in out


def test_editorial_split_html_contains_event_day_and_detail():
    out = fr._editorial_split_html("file:///photo.jpg", "Pool Night", "beat the bartender",
                                   "Saturday")
    assert "POOL NIGHT" in out
    assert "SATURDAY" in out
    assert "beat the bartender" in out


def test_editorial_split_html_omits_deal_row_when_no_deal_photo():
    out = fr._editorial_split_html("file:///photo.jpg", "Pool Night", "details", "Saturday",
                                   deal_photo_uri=None)
    assert "deal-row" not in out


def test_render_flyer_full_bleed_produces_correct_size(tmp_path):
    src = tmp_path / "photo.jpg"
    _dummy_photo(str(src))
    out = tmp_path / "out.png"
    fr.render_flyer(str(src), "Bingo Night", "10 rounds", "Monday", "2026-07-13",
                    str(out), size=(1080, 1080), layout="full_bleed")
    result = Image.open(out)
    assert result.size == (1080, 1080)


def test_render_flyer_editorial_split_produces_correct_size(tmp_path):
    src = tmp_path / "photo.jpg"
    _dummy_photo(str(src))
    out = tmp_path / "out.png"
    fr.render_flyer(str(src), "Pool Night", "beat the bartender", "Saturday", "2026-07-11",
                    str(out), size=(1080, 1080), layout="editorial_split")
    result = Image.open(out)
    assert result.size == (1080, 1080)


def test_render_flyer_with_deal_photo_still_renders_correct_size_both_layouts(tmp_path):
    """Regression for the real collision bug found in the old PIL system: a
    deal photo composited alongside a layout's own text must never break
    rendering or produce a wrong-sized image, on either layout."""
    src = tmp_path / "photo.jpg"
    _dummy_photo(str(src))
    deal = tmp_path / "deal.jpg"
    _dummy_photo(str(deal), color=(200, 50, 50))
    for layout in fr.LAYOUTS:
        out = tmp_path / f"out-{layout}.png"
        fr.render_flyer(str(src), "Pickleball Open Play", "$2 off Spotted Cow", "Tuesday",
                        "2026-07-14", str(out), size=(1080, 1080),
                        deal_photo_path=str(deal), layout=layout)
        result = Image.open(out)
        assert result.size == (1080, 1080), f"{layout} produced wrong size with a deal photo"
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd scripts && python -m pytest test_flyer_render.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'flyer_render'`

- [ ] **Step 4: Write `scripts/flyer_render.py`**

```python
"""
flyer_render.py - Premium HTML/CSS flyer rendering via Playwright.

Replaces the old PIL-drawn badge/minimal/poster templates in process_photos.py.
See the premium-photo-forward-design skill (~/.claude/skills/premium-photo-forward-design)
for the full design rationale. Two layout archetypes ("full_bleed", "editorial_split")
are chosen deterministically per (event, date). Each layout lays its content out with
CSS flexbox (not fixed absolute-pixel offsets), and the optional deal-photo inset is a
normal-flow child of that same flex column -- so it can never silently collide with the
headline/detail text the way the old PIL system's independently-positioned deal badge
once did. The browser's layout engine handles the spacing, not hand-computed coordinates.
"""

from __future__ import annotations

import hashlib
import html
import os
import tempfile
from pathlib import Path

from PIL import Image, ImageOps
from playwright.sync_api import sync_playwright

import config

LAYOUTS = ["full_bleed", "editorial_split"]


def choose_layout(event: str, date_str: str) -> str:
    """Deterministic layout rotation: the same (event, date) always picks the
    same layout on re-runs, but different dates/events vary."""
    seed = int(hashlib.md5(f"{event}{date_str}".encode()).hexdigest(), 16)
    return LAYOUTS[seed % len(LAYOUTS)]


def prep_photo(src_path: str, out_path: str, size=(1080, 1080), centering=(0.5, 0.4)) -> str:
    """Orientation-correct (EXIF) and crop-to-cover a real photo before
    referencing it from the HTML template -- CSS background-image ignores
    EXIF rotation, so skipping this renders sideways photos."""
    img = ImageOps.exif_transpose(Image.open(src_path))
    img = ImageOps.fit(img, size, method=Image.LANCZOS, centering=centering)
    img.convert("RGB").save(out_path, quality=92)
    return out_path


def _file_uri(path: str) -> str:
    return Path(path).resolve().as_uri()


def _deal_row_html(deal_photo_uri, key_details) -> str:
    if not deal_photo_uri:
        return ""
    detail = html.escape(key_details.split(",")[0].strip()) if key_details else ""
    caption_detail = f"<b>{detail}</b>" if detail else ""
    return f"""
  <div class="deal-row">
    <img class="deal-thumb" src="{deal_photo_uri}">
    <div class="deal-caption">Today's Deal{caption_detail}</div>
  </div>"""


def _full_bleed_html(photo_uri, event, key_details, day_of_week, deal_photo_uri=None) -> str:
    c = config.COLORS
    event_esc = html.escape(event.upper())
    day_esc = html.escape(day_of_week.upper())
    detail_esc = html.escape(key_details.split(",")[0].strip()) if key_details else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Barlow+Condensed:wght@500;600;700&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{width:1080px;height:1080px;}}
.canvas{{width:1080px;height:1080px;position:relative;overflow:hidden;background:{c['navy']};font-family:'Barlow Condensed',sans-serif;}}
.photo{{position:absolute;inset:0;background-image:url('{photo_uri}');background-size:cover;background-position:center;filter:contrast(1.08) saturate(1.12) brightness(0.98);}}
.grade{{position:absolute;inset:0;background:linear-gradient(160deg, rgba(11,28,45,0.28) 0%, rgba(11,28,45,0) 40%, rgba(200,146,42,0.10) 100%);mix-blend-mode:overlay;}}
.grain{{position:absolute;inset:0;opacity:0.06;mix-blend-mode:overlay;pointer-events:none;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");}}
.scrim{{position:absolute;left:0;right:0;bottom:0;height:60%;
  background:linear-gradient(to top, rgba(6,15,24,0.97) 0%, rgba(6,15,24,0.88) 30%, rgba(6,15,24,0.4) 68%, rgba(6,15,24,0) 100%);}}
.eyebrow{{position:absolute;top:56px;left:56px;display:flex;align-items:center;gap:12px;}}
.eyebrow .dot{{width:7px;height:7px;border-radius:50%;background:{c['yellow']};}}
.eyebrow span{{color:{c['yellow']};font-weight:700;font-size:22px;letter-spacing:6px;text-transform:uppercase;text-shadow:0 2px 8px rgba(0,0,0,0.5);}}
.content{{position:absolute;left:56px;right:56px;bottom:64px;display:flex;flex-direction:column;}}
.deal-row{{display:flex;align-items:center;gap:14px;margin-bottom:20px;}}
.deal-thumb{{width:84px;height:84px;border-radius:10px;object-fit:cover;border:3px solid {c['gold']};flex-shrink:0;}}
.deal-caption{{color:{c['gold']};font-weight:700;font-size:15px;letter-spacing:2px;text-transform:uppercase;line-height:1.5;}}
.deal-caption b{{color:{c['cream']};display:block;font-size:19px;letter-spacing:0.5px;text-transform:none;font-weight:700;}}
.headline{{font-family:'Anton';color:{c['cream']};font-size:108px;line-height:0.88;letter-spacing:1px;text-transform:uppercase;
  text-shadow:0 4px 24px rgba(0,0,0,0.55);}}
.rule{{width:64px;height:4px;background:{c['gold']};margin-top:24px;margin-bottom:18px;}}
.detail{{color:{c['gold']};font-weight:600;font-size:28px;letter-spacing:1px;line-height:1.4;}}
.footer{{position:absolute;bottom:56px;right:56px;text-align:right;}}
.footer .mark{{color:{c['cream']};font-weight:700;font-size:18px;letter-spacing:5px;text-transform:uppercase;opacity:0.9;}}
.footer .tag{{color:rgba(245,239,216,0.55);font-weight:500;font-size:13px;letter-spacing:3px;text-transform:uppercase;margin-top:4px;}}
</style></head>
<body>
<div class="canvas">
  <div class="photo"></div>
  <div class="grade"></div>
  <div class="scrim"></div>
  <div class="grain"></div>
  <div class="eyebrow"><div class="dot"></div><span>{day_esc}</span></div>
  <div class="content">{_deal_row_html(deal_photo_uri, key_details)}
    <div class="headline">{event_esc}</div>
    <div class="rule"></div>
    <div class="detail">{detail_esc}</div>
  </div>
  <div class="footer">
    <div class="mark">Backyard Brew</div>
    <div class="tag">Craft Brews &amp; Things To Do</div>
  </div>
</div>
</body></html>"""


def _editorial_split_html(photo_uri, event, key_details, day_of_week, deal_photo_uri=None) -> str:
    c = config.COLORS
    event_esc = html.escape(event.upper())
    day_esc = html.escape(day_of_week.upper())
    detail_esc = html.escape(key_details.split(",")[0].strip()) if key_details else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Barlow+Condensed:wght@500;600;700&display=swap');
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{width:1080px;height:1080px;}}
.canvas{{width:1080px;height:1080px;position:relative;overflow:hidden;background:{c['navy']};font-family:'Barlow Condensed',sans-serif;}}
.photo{{position:absolute;top:0;bottom:0;right:0;width:66%;background-image:url('{photo_uri}');background-size:cover;background-position:65% center;filter:contrast(1.06) saturate(1.1);}}
.photo-fade{{position:absolute;top:0;bottom:0;right:0;width:66%;background:linear-gradient(90deg, rgba(11,28,45,0.9) 0%, rgba(11,28,45,0) 12%);}}
.grain{{position:absolute;inset:0;opacity:0.05;mix-blend-mode:overlay;pointer-events:none;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");}}
.panel{{position:absolute;top:0;bottom:0;left:0;width:38%;padding:64px 0 56px 56px;display:flex;flex-direction:column;justify-content:flex-end;}}
.deal-row{{display:flex;align-items:center;gap:12px;margin-bottom:24px;}}
.deal-thumb{{width:72px;height:72px;border-radius:10px;object-fit:cover;border:3px solid {c['gold']};flex-shrink:0;}}
.deal-caption{{color:{c['gold']};font-weight:700;font-size:13px;letter-spacing:2px;text-transform:uppercase;line-height:1.5;}}
.deal-caption b{{color:{c['cream']};display:block;font-size:17px;letter-spacing:0.5px;text-transform:none;font-weight:700;}}
.eyebrow{{display:flex;align-items:center;gap:12px;margin-bottom:24px;}}
.eyebrow .bar{{width:36px;height:3px;background:{c['gold']};}}
.eyebrow span{{color:{c['gold']};font-weight:700;font-size:19px;letter-spacing:5px;text-transform:uppercase;}}
.headline{{font-family:'Anton';color:{c['cream']};font-size:86px;line-height:0.9;letter-spacing:1px;text-transform:uppercase;}}
.detail{{margin-top:26px;color:{c['cream']};font-weight:500;font-size:23px;line-height:1.5;opacity:0.92;max-width:290px;}}
.footer{{position:absolute;bottom:56px;left:56px;}}
.footer .mark{{color:rgba(245,239,216,0.55);font-weight:600;font-size:13px;letter-spacing:4px;text-transform:uppercase;}}
</style></head>
<body>
<div class="canvas">
  <div class="photo"></div>
  <div class="photo-fade"></div>
  <div class="grain"></div>
  <div class="panel">{_deal_row_html(deal_photo_uri, key_details)}
    <div class="eyebrow"><div class="bar"></div><span>{day_esc}</span></div>
    <div class="headline">{event_esc}</div>
    <div class="detail">{detail_esc}</div>
  </div>
  <div class="footer"><div class="mark">Backyard Brew</div></div>
</div>
</body></html>"""


_LAYOUT_BUILDERS = {"full_bleed": _full_bleed_html, "editorial_split": _editorial_split_html}


def render_flyer(photo_path, event, key_details, day_of_week, date_str, out_path,
                 size=(1080, 1080), deal_photo_path=None, layout=None) -> str:
    """Render one flyer: prep the photo(s), pick a layout (or use the given
    override -- mainly for tests), build the HTML, screenshot it via
    Playwright, save to out_path. Returns out_path."""
    with tempfile.TemporaryDirectory() as tmp:
        prepped_photo = os.path.join(tmp, "photo.jpg")
        prep_photo(photo_path, prepped_photo, size=size)
        photo_uri = _file_uri(prepped_photo)

        deal_photo_uri = None
        if deal_photo_path:
            prepped_deal = os.path.join(tmp, "deal.jpg")
            prep_photo(deal_photo_path, prepped_deal, size=(400, 400))
            deal_photo_uri = _file_uri(prepped_deal)

        chosen_layout = layout or choose_layout(event, date_str or day_of_week)
        html_str = _LAYOUT_BUILDERS[chosen_layout](
            photo_uri, event, key_details, day_of_week, deal_photo_uri)
        html_path = os.path.join(tmp, "flyer.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_str)

        out_dir = os.path.dirname(out_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": size[0], "height": size[1]})
            page.goto(_file_uri(html_path))
            page.screenshot(path=out_path)
            browser.close()

    return out_path
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_flyer_render.py -v`
Expected: PASS (13 tests). The 3 `render_flyer` tests are slower (real browser launches) — that's expected and matches the plan's testing strategy (small number of real end-to-end tests, not the primary coverage mechanism).

- [ ] **Step 6: Commit**

```bash
git add scripts/flyer_render.py scripts/test_flyer_render.py
git commit -m "Add flyer_render.py: HTML/CSS + Playwright premium flyer rendering"
```

---

### Task 2: Wire into `process_photos.py`, remove the dead PIL flyer code

**Files:**
- Modify: `scripts/process_photos.py`
- Modify: `scripts/test_process_photos.py`

**Interfaces:**
- Consumes: `flyer_render.render_flyer(...)` (Task 1).
- Produces: `process_photos.process(...)` — same public signature as before, internals changed for `text_overlay`/`both` modes.

- [ ] **Step 1: Update the tests first (this task is an integration swap, not new-feature TDD — update tests to match the new implementation, then verify the old code fails them, then implement)**

Replace `scripts/test_process_photos.py` in full:
```python
from PIL import Image

import config
import process_photos as pp


def _dummy_photo(color=(120, 150, 90), size=(1600, 1200)):
    return Image.new("RGB", size, color)


def test_process_premade_art_mode_untouched_passthrough(tmp_path):
    src = tmp_path / "2026-07-14_bingo_art.png"
    _dummy_photo().save(src)
    out = tmp_path / "out.png"
    pp.process(str(src), str(out), "ig_feed", "premade_art")
    result = Image.open(out)
    assert result.size == config.DIMENSIONS["ig_feed"]


def test_process_none_mode_applies_light_polish(tmp_path):
    src = tmp_path / "photo.jpg"
    _dummy_photo().save(src)
    out = tmp_path / "out.png"
    pp.process(str(src), str(out), "ig_feed", "none")
    result = Image.open(out)
    assert result.size == config.DIMENSIONS["ig_feed"]


def test_process_logo_mode_adds_watermark_without_error(tmp_path):
    src = tmp_path / "photo.jpg"
    _dummy_photo().save(src)
    out = tmp_path / "out.png"
    pp.process(str(src), str(out), "ig_feed", "logo")
    result = Image.open(out)
    assert result.size == config.DIMENSIONS["ig_feed"]


def test_process_text_overlay_mode_renders_via_flyer_render(tmp_path):
    src = tmp_path / "2026-07-14_bingo.jpg"
    _dummy_photo().save(src)
    out = tmp_path / "out.png"
    result_path = pp.process(str(src), str(out), "ig_feed", "text_overlay",
                             event="Bingo Night", key_details="10 rounds",
                             day_of_week="Monday", date_str="2026-07-14")
    assert result_path == str(out)
    result = Image.open(out)
    assert result.size == config.DIMENSIONS["ig_feed"]


def test_process_both_mode_renders_flyer_then_adds_logo(tmp_path):
    src = tmp_path / "2026-07-14_bingo.jpg"
    _dummy_photo().save(src)
    out = tmp_path / "out.png"
    pp.process(str(src), str(out), "ig_feed", "both",
              event="Bingo Night", key_details="10 rounds",
              day_of_week="Monday", date_str="2026-07-14")
    result = Image.open(out)
    assert result.size == config.DIMENSIONS["ig_feed"]


def test_process_composites_deal_photo_when_provided(tmp_path):
    src = tmp_path / "2026-07-14_pickleball.jpg"
    _dummy_photo().save(src)
    deal_photo = tmp_path / "2026-07-14_pickleball_deal.jpg"
    _dummy_photo(color=(255, 255, 255)).save(deal_photo)
    out = tmp_path / "out.png"
    pp.process(str(src), str(out), "ig_feed", "text_overlay",
              event="Pickleball Open Play", key_details="$2 off Spotted Cow",
              day_of_week="Tuesday", date_str="2026-07-14",
              deal_photo_path=str(deal_photo))
    result = Image.open(out).convert("RGB")
    assert result.size == config.DIMENSIONS["ig_feed"]


def test_resolve_mode_art_suffix_always_wins():
    assert pp.resolve_mode("2026-07-14_bingo_art.png", "text_overlay") == "premade_art"


def test_output_name_format():
    name = pp.output_name("post", "Bingo Night", "2026-07-14")
    assert name == "backyard-brew-post-bingo-night-2026-07-14.png"
```

- [ ] **Step 2: Run to verify these tests fail against the current implementation**

Run: `cd scripts && python -m pytest test_process_photos.py -v`
Expected: FAIL — the old `process()` doesn't produce comparable output for `text_overlay`/`both` via the new module (it isn't calling `flyer_render` yet), and several old-test-only symbols (`choose_template`, `_build_flyer_minimal`, etc.) referenced by the *previous* version of this test file are gone from this new version, so this is really confirming the new tests exercise real, not-yet-built behavior. (The two tests that don't touch flyer rendering — `premade_art`, `resolve_mode`, `output_name` — should already pass; that's fine and expected, this isn't a strict RED-for-every-test gate since this task is an integration swap.)

- [ ] **Step 3: Rewrite `scripts/process_photos.py`**

Replace the entire file:
```python
"""
process_photos.py - Crop/resize/enhance photos and build flyers.

Modes (from the `enhance` column or the filename suffix):
  none / blank  -> light polish only: crop to platform aspect + auto brightness/contrast
  text_overlay  -> premium HTML/CSS flyer over the photo (see flyer_render.py)
  logo          -> photo + logo watermark in a corner
  both          -> flyer + logo
  premade_art   -> finished graphic: NO editing, only resize to fit platform dims
                   (any filename ending in _art is auto-treated as premade_art)

text_overlay/both delegate to flyer_render.py (HTML/CSS rendered via Playwright) for real
design quality -- see the premium-photo-forward-design skill for why. Everything else here
stays plain PIL, which is already correctly simple for those modes.
"""

from __future__ import annotations

import os

from PIL import Image, ImageEnhance, ImageOps

import config
import flyer_render


def resolve_mode(filename: str, enhance_col: str) -> str:
    """Decide the processing mode. A _art suffix always wins (premade_art)."""
    stem = os.path.splitext(os.path.basename(filename))[0].lower()
    if stem.endswith("_art") or stem.endswith("_teaser_art") or "_art" in stem.split("_")[-1:]:
        return "premade_art"
    # Robust check: any token equal to "art".
    if "art" in stem.split("_"):
        return "premade_art"
    mode = (enhance_col or "").strip().lower()
    if mode in {"none", ""}:
        return "none"
    if mode in {"text_overlay", "logo", "both", "premade_art"}:
        return mode
    return "none"


def _fit_cover(img: Image.Image, size) -> Image.Image:
    """Crop-to-cover: fill the target box exactly, cropping overflow (center)."""
    return ImageOps.fit(img, size, method=Image.LANCZOS, centering=(0.5, 0.5))


def _fit_contain(img: Image.Image, size) -> Image.Image:
    """Contain: scale to fit inside the box, pad with brand navy (no cropping)."""
    canvas = Image.new("RGB", size, config.COLORS["navy"])
    scaled = img.copy()
    scaled.thumbnail(size, Image.LANCZOS)
    x = (size[0] - scaled.width) // 2
    y = (size[1] - scaled.height) // 2
    canvas.paste(scaled, (x, y))
    return canvas


def _auto_polish(img: Image.Image) -> Image.Image:
    """Gentle, universal cleanup: mild autocontrast + tiny brightness/color lift."""
    img = ImageOps.exif_transpose(img)  # respect phone orientation
    img = ImageOps.autocontrast(img, cutoff=1)
    img = ImageEnhance.Brightness(img).enhance(1.03)
    img = ImageEnhance.Color(img).enhance(1.05)
    return img


def _load_logo():
    for name in ("logo.png", "logo_light.png"):
        p = os.path.join(config.LOGO_DIR, name)
        if os.path.exists(p):
            try:
                return Image.open(p).convert("RGBA")
            except Exception:
                pass
    return None


def _add_logo(img: Image.Image) -> Image.Image:
    logo = _load_logo()
    if logo is None:
        print("[process_photos] no logo found in assets/logo/, skipping watermark")
        return img
    target_w = int(img.width * 0.18)
    ratio = target_w / logo.width
    logo = logo.resize((target_w, int(logo.height * ratio)), Image.LANCZOS)
    margin = int(img.width * 0.04)
    pos = (img.width - logo.width - margin, img.height - logo.height - margin)
    base = img.convert("RGBA")
    base.alpha_composite(logo, pos)
    return base.convert("RGB")


def process(input_path, out_path, platform_key, enhance_col,
            event="", key_details="", day_of_week="", date_str="",
            deal_photo_path=None):
    """Process one image for one platform and save it to out_path.

    text_overlay/both delegate entirely to flyer_render.render_flyer(), which
    saves directly to out_path; "both" then reopens that file to stamp the
    logo on top. Every other mode stays plain PIL.

    Returns out_path on success. Never raises on cosmetic issues -- worst case it
    still writes a correctly-sized image so a post is never blocked.
    """
    size = config.DIMENSIONS[platform_key]
    mode = resolve_mode(input_path, enhance_col)
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    if mode in ("text_overlay", "both"):
        flyer_render.render_flyer(input_path, event, key_details, day_of_week, date_str,
                                  out_path, size=size, deal_photo_path=deal_photo_path)
        if mode == "both":
            logoed = _add_logo(Image.open(out_path).convert("RGB"))
            logoed.save(out_path, quality=92)
        return out_path

    img = Image.open(input_path)
    if mode == "premade_art":
        # Post exactly as supplied -- only fit to platform dims, no other edits.
        result = _fit_contain(img.convert("RGB"), size)
    elif mode == "none":
        result = _fit_cover(_auto_polish(img), size)
    elif mode == "logo":
        result = _add_logo(_fit_cover(_auto_polish(img), size))
    else:
        result = _fit_cover(_auto_polish(img), size)

    result.save(out_path, quality=92)
    return out_path


def output_name(platform_short, event, date_str, ext=".png"):
    """backyard-brew-[platform]-[type]-[YYYY-MM-DD].ext"""
    slug = "".join(ch if ch.isalnum() else "-" for ch in event.lower()).strip("-")
    slug = "-".join(filter(None, slug.split("-")))
    return f"backyard-brew-{platform_short}-{slug}-{date_str}{ext}"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd scripts && python -m pytest test_process_photos.py -v`
Expected: PASS (8 tests)

- [ ] **Step 5: Grep the repo for any remaining reference to the deleted symbols**

Run: `cd scripts && grep -rn "_build_flyer\|_add_deal_callout\|choose_template\|FLYER_TEMPLATES\|ensure_fonts\|FONT_FILES\|_headline_font\|_autosize_headline\|SLAB_EVENTS" .`
Expected: no output. If anything else in the repo (not just `process_photos.py`/`test_process_photos.py`) still references one of these, that's a real gap this task must also fix.

- [ ] **Step 6: Run the full suite**

Run: `cd scripts && python -m pytest -v`
Expected: PASS (all tests, including Task 1's `test_flyer_render.py`)

- [ ] **Step 7: Commit**

```bash
git add scripts/process_photos.py scripts/test_process_photos.py
git commit -m "Wire flyer_render.py into process_photos.py, remove dead PIL flyer-drawing code"
```

---

### Task 3: CI/dependency updates — Playwright in requirements.txt and the Sunday workflow

**Files:**
- Modify: `requirements.txt`
- Modify: `.github/workflows/sunday-generate.yml`

**Interfaces:** none (dependency/CI config only).

- [ ] **Step 1: Add Playwright to `requirements.txt`**

Replace:
```
anthropic>=0.40.0
requests>=2.31.0
Pillow>=10.2.0
tzdata>=2024.1        # timezone database (required on Windows; harmless on Linux)
```

With:
```
anthropic>=0.40.0
requests>=2.31.0
Pillow>=10.2.0
playwright>=1.40.0    # renders the premium HTML/CSS flyer templates (see flyer_render.py)
tzdata>=2024.1        # timezone database (required on Windows; harmless on Linux)
```

- [ ] **Step 2: Add a Chromium install step to `.github/workflows/sunday-generate.yml`**

Replace:
```yaml
      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Generate the week's captions
```

With:
```yaml
      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Install Playwright's browser
        run: playwright install --with-deps chromium

      - name: Generate the week's captions
```

- [ ] **Step 3: Validate the YAML by reading the full file back and confirming indentation is consistent with the surrounding steps**

Run: `cat .github/workflows/sunday-generate.yml` and visually confirm the new step matches the 6-space step indentation and `- name:` / `run:` structure of every other step in the file. If `python -c "import yaml"` succeeds in this environment, also run `python -c "import yaml; yaml.safe_load(open('.github/workflows/sunday-generate.yml')); print('VALID')"` for a second confirmation.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt .github/workflows/sunday-generate.yml
git commit -m "Add Playwright + Chromium install for the new HTML/CSS flyer renderer"
```

---

## Self-Review Notes

- **Spec coverage:** Playwright rendering engine → Task 1 & 3. Two layout archetypes with
  flexbox-based deal-photo collision safety → Task 1. `process_photos.py` integration point
  unchanged, dead PIL code removed → Task 2. CI Chromium install → Task 3. EXIF correction →
  Task 1's `prep_photo`. Out-of-scope items (third layout, other aspect ratios, website hours
  fix) are explicitly not tasked, matching the spec.
- **Placeholder scan:** no TBD/TODO. The two layout HTML templates are complete, real CSS (not
  simplified stand-ins) — they're the exact design validated live in conversation.
- **Type/signature consistency:** `process_photos.process()`'s signature is unchanged end-to-end
  (Task 2 keeps every parameter name/order identical to what `generate_captions.py`'s
  `render_generated_images()` already calls it with — confirmed by reading that call site before
  writing this plan). `flyer_render.render_flyer()`'s signature is introduced once in Task 1 and
  consumed identically in Task 2.
