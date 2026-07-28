# Graph Report - backyard-brew-social  (2026-07-28)

## Corpus Check
- 68 files · ~26,861,637 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 245 nodes · 249 edges · 22 communities (19 shown, 3 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ecc222ff`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- CLAUDE.md
- test_generate_captions.py
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
- _selfcheck
- Backyard Brew — Social Media & Online Presence
- growth-week.md
- reply.md
- graphic.md
- Caption Voice Rules
- setup.sh

## God Nodes (most connected - your core abstractions)
1. `Backyard Brew Brand Identity` - 10 edges
2. `Writing the Gemini prompt` - 10 edges
3. `Making a Graphic` - 10 edges
4. `Backyard Market & Brews (Thursday)` - 9 edges
5. `Growth Playbook` - 9 edges
6. `Backyard Brew: Start Here` - 9 edges
7. `Replying to Reviews, Comments, and Messages` - 8 edges
8. `Backyard Brew` - 8 edges
9. `Every Week` - 8 edges
10. `Operations Reality` - 7 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (22 total, 3 thin omitted)

### Community 0 - "CLAUDE.md"
Cohesion: 0.22
Nodes (8): Backyard Brew, Data files, graphify, Nothing posts automatically, Read the brand skill first, Scripts, The four commands, The printed sheets

### Community 1 - "test_generate_captions.py"
Cohesion: 0.09
Nodes (6): One-off/special-event callers don't pass event/posts_history -- must     behave, pizza is served every day, so it must not attach on every event's     'today' po, A filename that contains BOTH an event keyword and a food keyword     (e.g. poke, test_find_food_photo_excludes_already_chosen_main_photo(), test_find_food_photo_gates_occasional_keyword_to_one_day_per_week(), test_find_photo_without_event_keeps_old_behavior()

### Community 2 - "classify_photos.py"
Cohesion: 0.17
Nodes (10): manual_kind(), needs_classification(), pool_claimed(), classify_photos.py - Filename-convention helpers for photo handling.  No vision, vibe'/'spotlight' if the filename carries that override suffix, else None., True if this filename's stem contains a keyword from     config.EVENT_PHOTO_KEYW, False if the filename already carries an explicit override signal,     or isn't, EXIF DateTimeOriginal if present, else the file's mtime. None on error. (+2 more)

### Community 3 - "Backyard Brew — Weekly Social Content Workflow"
Cohesion: 0.09
Nodes (18): Backup: when Gemini will not cooperate, Making a Graphic, Step 1. Pick your photo first, Step 2. Ask Claude for the prompt, Step 3. Run it through Gemini, Step 4. Remove the watermark, Step 5. Put the real logo on in Canva, Step 6. Name it and check it (+10 more)

### Community 5 - "generate_captions.py"
Cohesion: 0.10
Nodes (25): dow_name(), find_deal_photo(), find_food_photo(), find_photo(), list_photos(), parse_date(), _photo_last_used(), _pick_pool_photo() (+17 more)

### Community 6 - "_pick_pool_photo"
Cohesion: 0.12
Nodes (15): 1. Format, 2. Base the image on the real photo, 3. Style, 4. Exact colors, 5. Typography, 6. Text, spelled out exactly and kept short, 7. Reserve a circle for the logo, 8. Anti-slop negatives (+7 more)

### Community 7 - "render_generated_images"
Cohesion: 0.14
Nodes (13): Comments and DMs, Delivering a draft, Never, in a public reply, Never respond in the first hour, Replying to Reviews, Comments, and Messages, Responding to a false review (Type B), Step 1: Triage before writing, The one reframe that governs everything (+5 more)

### Community 8 - "_pool_candidates"
Cohesion: 0.15
Nodes (12): 1. Google Business Profile, 2. Reviews, 3. Tuesday and Wednesday, 4. Facebook groups, 5. Website and AI search, 6. Event concepts for the two dead windows, Before recommending any of these, Growth Playbook (+4 more)

### Community 9 - "find_food_photo"
Cohesion: 0.17
Nodes (12): Backyard Brew: Start Here, Dropping in photos, First time on this Mac only, If something is not working, It already knows the bar, Opening it, Printing these, The four commands (+4 more)

### Community 10 - "find_deal_photo"
Cohesion: 0.18
Nodes (10): Constraints to respect in any recommendation, Customers and complaints, Goals, How to handle staffing in recommendations, Operations Reality, Staff (as of 2026-07-27, actively changing), The Tuesday/Wednesday diagnosis, The two real gaps (+2 more)

### Community 11 - "slug_from_default"
Cohesion: 0.18
Nodes (10): Backyard Brew Brand Identity, Colors (extracted from the logo — use these exact hex values), Facts (verified — use these exact values), Fonts already established in this brand's content pipeline, Pre-flight for any Backyard Brew deliverable, Recurring weekly events (the heartbeat of the content calendar), Start here: which file answers your question, Voice (+2 more)

### Community 12 - "test_find_photo_without_event_keeps_old_behavior"
Cohesion: 0.20
Nodes (9): Backyard Market & Brews (Thursday), Contact, Messaging & tone guidelines, Musician standards, Photo situation (open gap as of 2026-07-26), Schedule, Vendor standards (screening criteria), What happens (+1 more)

### Community 13 - "test_find_food_photo_gates_occasional_keyword_to_one_day_per_week"
Cohesion: 0.20
Nodes (9): All day: stories, Every Day, First hour after each post: reply to comments, How to do it right, Morning: share the 11am post to Facebook groups, The daily checklist, The line you write above it matters most, Which groups for which post (+1 more)

### Community 14 - "test_find_food_photo_excludes_already_chosen_main_photo"
Cohesion: 0.22
Nodes (8): 11:00am: the day's main post, 2:30pm: highlight, recap, or filler, 7:00pm: teaser for tomorrow, Before delivering: run the tally, Before writing anything, Deliver, Picking photos, The schedule: 3 posts a day, every day, all seven days

### Community 15 - "_selfcheck"
Cohesion: 0.43
Nodes (7): lint(), main(), md_to_html(), Warn about a list glued to the line above it.      Markdown silently swallows th, Smallest thing that fails if the conversion breaks., Convert one markdown sheet into a standalone printable HTML page., _selfcheck()

### Community 16 - "Backyard Brew — Social Media & Online Presence"
Cohesion: 0.25
Nodes (8): Backyard Brew — Social Media & Online Presence, Naming photos, Optional setup, The four commands, The rules, Then read this, Using it (no terminal needed), What's in here

### Community 17 - "growth-week.md"
Cohesion: 0.40
Nodes (4): Deliver, Do this, Rules, When asked for event ideas

### Community 18 - "reply.md"
Cohesion: 0.40
Nodes (4): Deliver, Do this, If he included what he actually wants to say, Remember

### Community 19 - "graphic.md"
Cohesion: 0.50
Nodes (3): Deliver, in this order, Do this, If Gemini keeps failing

## Knowledge Gaps
- **121 isolated node(s):** `Do this`, `Deliver, in this order`, `If Gemini keeps failing`, `Do this`, `Deliver` (+116 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Backyard Brew: Start Here` connect `find_food_photo` to `Backyard Brew — Weekly Social Content Workflow`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **What connects `Do this`, `Deliver, in this order`, `If Gemini keeps failing` to the rest of the system?**
  _145 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_generate_captions.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08695652173913043 - nodes in this community are weakly interconnected._
- **Should `Backyard Brew — Weekly Social Content Workflow` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._
- **Should `generate_captions.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10317460317460317 - nodes in this community are weakly interconnected._
- **Should `_pick_pool_photo` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Should `render_generated_images` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._