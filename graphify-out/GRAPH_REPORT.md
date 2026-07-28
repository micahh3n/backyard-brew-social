# Graph Report - backyard-brew-social  (2026-07-12)

## Corpus Check
- 52 files · ~21,557,755 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 87 nodes · 99 edges · 15 communities (9 shown, 6 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c10e10bd`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- CLAUDE.md
- classify_photos.py
- Backyard Brew — Weekly Social Content Workflow
- test_classify_photos.py
- generate_captions.py
- _pick_pool_photo
- render_generated_images
- _pool_candidates
- find_food_photo
- find_deal_photo
- slug_from_default
- test_find_photo_without_event_keeps_old_behavior
- test_find_food_photo_gates_occasional_keyword_to_one_day_per_week
- test_find_food_photo_excludes_already_chosen_main_photo

## God Nodes (most connected - your core abstractions)
1. `render_generated_images()` - 6 edges
2. `Backyard Brew — Weekly Social Content Workflow` - 5 edges
3. `_pool_candidates()` - 5 edges
4. `_pick_pool_photo()` - 5 edges
5. `How To Use This Every Week` - 4 edges
6. `list_photos()` - 4 edges
7. `find_photo()` - 4 edges
8. `find_food_photo()` - 4 edges
9. `find_deal_photo()` - 4 edges
10. `dow_name()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `render_generated_images()` --calls--> `dow_name()`  [EXTRACTED]
  scripts/generate_captions.py → scripts/generate_captions.py  _Bridges community 9 → community 7_
- `find_photo()` --calls--> `list_photos()`  [EXTRACTED]
  scripts/generate_captions.py → scripts/generate_captions.py  _Bridges community 10 → community 6_
- `_pool_candidates()` --calls--> `list_photos()`  [EXTRACTED]
  scripts/generate_captions.py → scripts/generate_captions.py  _Bridges community 10 → community 8_
- `find_food_photo()` --calls--> `_pick_pool_photo()`  [EXTRACTED]
  scripts/generate_captions.py → scripts/generate_captions.py  _Bridges community 9 → community 6_
- `render_generated_images()` --calls--> `find_deal_photo()`  [EXTRACTED]
  scripts/generate_captions.py → scripts/generate_captions.py  _Bridges community 10 → community 7_

## Import Cycles
- None detected.

## Communities (15 total, 6 thin omitted)

### Community 2 - "classify_photos.py"
Cohesion: 0.17
Nodes (10): manual_kind(), needs_classification(), pool_claimed(), classify_photos.py - Filename-convention helpers for photo handling.  No vision, vibe'/'spotlight' if the filename carries that override suffix, else None., True if this filename's stem contains a keyword from     config.EVENT_PHOTO_KEYW, False if the filename already carries an explicit override signal,     or isn't, EXIF DateTimeOriginal if present, else the file's mtime. None on error. (+2 more)

### Community 3 - "Backyard Brew — Weekly Social Content Workflow"
Cohesion: 0.18
Nodes (9): During the week, How To Use This Every Week, Sunday (or whenever): ask for it, The golden rules, Backyard Brew — Weekly Social Content Workflow, How it flows, Notes, Start here (+1 more)

### Community 5 - "generate_captions.py"
Cohesion: 0.25
Nodes (5): generate_captions.py - Reusable photo/schedule helpers for the Sunday social med, Auto-suggest text_overlay for info-dense pushes, none for vibe content., Return 'YYYY-MM-DD HH:MM' local. owner_time (HH:MM) overrides the default., scheduled_string(), suggest_enhance()

### Community 6 - "_pick_pool_photo"
Cohesion: 0.50
Nodes (4): find_photo(), _pick_pool_photo(), None if no eligible candidate. Otherwise the filename to use this     run: a nev, Pick the right photo filename for a post.      Preference order:       today pos

### Community 7 - "render_generated_images"
Cohesion: 0.50
Nodes (4): parse_date(), Render each row's flyer/photo to config.GENERATED_DIR and set     generated_imag, render_generated_images(), slug_from_event()

### Community 8 - "_pool_candidates"
Cohesion: 0.50
Nodes (4): _photo_last_used(), _pool_candidates(), filename -> most recent 'date' value (YYYY-MM-DD) it appeared in any     row's p, Every eligible photo in config.PHOTOS_DIR whose filename contains any     of `ke

### Community 9 - "find_food_photo"
Cohesion: 0.67
Nodes (3): dow_name(), find_food_photo(), Return a filename to attach as a second photo on this recurring     event's 'tod

### Community 10 - "find_deal_photo"
Cohesion: 0.67
Nodes (3): find_deal_photo(), list_photos(), The dated _deal photo for this date/event slug, if the owner dropped     one (e.

## Knowledge Gaps
- **9 isolated node(s):** `Sunday Social Media`, `graphify`, `During the week`, `Sunday (or whenever): ask for it`, `The golden rules` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_pick_pool_photo()` connect `_pick_pool_photo` to `_pool_candidates`, `find_food_photo`, `generate_captions.py`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `render_generated_images()` connect `render_generated_images` to `find_food_photo`, `find_deal_photo`, `generate_captions.py`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `_pool_candidates()` connect `_pool_candidates` to `find_deal_photo`, `generate_captions.py`, `_pick_pool_photo`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **What connects `Sunday Social Media`, `graphify`, `During the week` to the rest of the system?**
  _30 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_generate_captions.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._