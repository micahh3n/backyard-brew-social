# Graph Report - backyard-brew-social  (2026-07-28)

## Corpus Check
- 77 files · ~26,874,513 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 352 nodes · 350 edges · 31 communities (30 shown, 1 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7aabf89e`
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
- photos.md
- Do it in this order
- Making a Graphic
- Every Day
- Every Week
- Backyard Brew — Social Media & Online Presence
- Vendor_Communication_Templates_63fdc6dc.md
- Every Day

## God Nodes (most connected - your core abstractions)
1. `Backyard Brew Brand Identity` - 10 edges
2. `Making a Graphic` - 10 edges
3. `Writing the Gemini prompt` - 10 edges
4. `Making a Graphic` - 10 edges
5. `Backyard Brew: Start Here` - 9 edges
6. `Backyard Brew: Start Here` - 9 edges
7. `Every Week` - 9 edges
8. `Handoff Checklist` - 9 edges
9. `Every Week` - 9 edges
10. `Backyard Market & Brews (Thursday)` - 9 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (31 total, 1 thin omitted)

### Community 0 - "CLAUDE.md"
Cohesion: 0.22
Nodes (8): Backyard Brew, Data files, graphify, Nothing posts automatically, Read the brand skill first, Scripts, The printed sheets, The six commands

### Community 1 - "test_generate_captions.py"
Cohesion: 0.09
Nodes (6): One-off/special-event callers don't pass event/posts_history -- must     behave, pizza is served every day, so it must not attach on every event's     'today' po, A filename that contains BOTH an event keyword and a food keyword     (e.g. poke, test_find_food_photo_excludes_already_chosen_main_photo(), test_find_food_photo_gates_occasional_keyword_to_one_day_per_week(), test_find_photo_without_event_keeps_old_behavior()

### Community 2 - "classify_photos.py"
Cohesion: 0.14
Nodes (12): manual_kind(), needs_classification(), pool_claimed(), classify_photos.py - Filename-convention helpers for photo handling.  No vision, vibe'/'spotlight' if the filename carries that override suffix, else None., True if this filename's stem contains a keyword from     config.EVENT_PHOTO_KEYW, False if the filename already carries an explicit override signal,     or isn't, The photo's real capture time, or None. Never falls back to mtime.      Use this (+4 more)

### Community 3 - "Backyard Brew — Weekly Social Content Workflow"
Cohesion: 0.18
Nodes (10): Backup: when Gemini will not cooperate, Making a Graphic, Step 1. Pick your photo first, Step 2. Ask Claude for the prompt, Step 3. Run it through Gemini, Step 4. Remove the watermark, Step 5. Put the real logo on in Canva, Step 6. Name it and check it (+2 more)

### Community 4 - "test_classify_photos.py"
Cohesion: 0.20
Nodes (9): 1. Drop in this week's photos (5 min), 2. Write the week's posts (10 min), 3. Schedule everything in Meta Business Suite (30 min), 4. Google Business Profile (10 min), 5. Reviews (5 min), 6. Ask what to work on (5 min, optional), 7. Send it to Micah (1 min), Every Week (+1 more)

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
Cohesion: 0.09
Nodes (21): Backyard Brew: Start Here, Dropping in photos, First time on this Mac only, If something is not working, It already knows the bar, Opening it, Reading, printing, and editing these sheets, Sharing with Micah (+13 more)

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
Cohesion: 0.14
Nodes (13): Backyard Brew: Start Here, Dropping in photos, First time on this Mac only, If something is not working, It already knows the bar, Opening it, Reading, printing, and editing these sheets, Sharing with Micah (+5 more)

### Community 14 - "test_find_food_photo_excludes_already_chosen_main_photo"
Cohesion: 0.10
Nodes (20): 11:00am: the day's main post, 11am the day of: turn it into a decision, 2:30pm: highlight, recap, or filler that ties in, 2:30pm the day of: last call before doors, 7:00pm: teaser for tomorrow, 7pm the night before: make them want it, Before delivering: run the tally, Before writing anything (+12 more)

### Community 15 - "_selfcheck"
Cohesion: 0.24
Nodes (14): Path, _add_runs(), _docx_source_hash(), lint(), main(), md_to_docx(), md_to_html(), Convert one markdown sheet into a standalone printable HTML page. (+6 more)

### Community 16 - "Backyard Brew — Social Media & Online Presence"
Cohesion: 0.20
Nodes (9): 1. Access your dad needs (do this first, it blocks everything else), 2. Things only you can fill in, 3. Get it onto his Mac, 4. Do one real week together, 5. Print and leave these by the computer, 6. Tell him the three things that matter most, 7. First month, Handoff Checklist (+1 more)

### Community 17 - "growth-week.md"
Cohesion: 0.40
Nodes (4): Deliver, Do this, Rules, When asked for event ideas

### Community 18 - "reply.md"
Cohesion: 0.40
Nodes (4): Deliver, Do this, If he included what he actually wants to say, Remember

### Community 19 - "graphic.md"
Cohesion: 0.50
Nodes (3): Deliver, in this order, Do this, If Gemini keeps failing

### Community 20 - "Caption Voice Rules"
Cohesion: 0.40
Nodes (4): Caption Voice Rules, Facebook vs Instagram must be genuinely different posts, not repurposed copies, Give real information, not just hype, Money language: win big yes, gambling no

### Community 22 - "photos.md"
Cohesion: 0.20
Nodes (9): Check posts.csv before renaming anything, Decide the name, Find what needs naming, Finish, HEIC photos need a preview first, Judgment calls, Look at each one, Show the plan before touching anything (+1 more)

### Community 23 - "Do it in this order"
Cohesion: 0.22
Nodes (8): 1. See what is here, 2. Commit their work, if there is any, 3. Get their changes, 4. Send yours, 5. Confirm it actually landed, Do it in this order, Finish, When something goes wrong

### Community 24 - "Making a Graphic"
Cohesion: 0.18
Nodes (10): Backup: when Gemini will not cooperate, Making a Graphic, Step 1. Pick your photo first, Step 2. Ask Claude for the prompt, Step 3. Run it through Gemini, Step 4. Remove the watermark, Step 5. Put the real logo on in Canva, Step 6. Name it and check it (+2 more)

### Community 25 - "Every Day"
Cohesion: 0.20
Nodes (9): All day: stories, Every Day, First hour after each post: reply to comments, How to do it right, Morning: share the 11am post to Facebook groups, The daily checklist, The line you write above it matters most, Which groups for which post (+1 more)

### Community 26 - "Every Week"
Cohesion: 0.20
Nodes (9): 1. Drop in this week's photos (5 min), 2. Write the week's posts (10 min), 3. Schedule everything in Meta Business Suite (30 min), 4. Google Business Profile (10 min), 5. Reviews (5 min), 6. Ask what to work on (5 min, optional), 7. Send it to Micah (1 min), Every Week (+1 more)

### Community 27 - "Backyard Brew — Social Media & Online Presence"
Cohesion: 0.17
Nodes (4): Video files (iPhones drop these alongside camera-roll photos) are     never a st, Must not fall back to mtime: a fresh clone would date the whole     backlog as ', test_needs_classification_skips_video_files(), test_read_exif_time_returns_none_without_exif()

### Community 28 - "Vendor_Communication_Templates_63fdc6dc.md"
Cohesion: 0.40
Nodes (4): 1. The Rundown — send when someone asks for more info or to be in the market, 2. Polite Decline — similar vendor already booked for this event, 3. Vendor Spots Full — waitlist reply, 4. Confirmed Vendor Info Sheet — send a few days before the event

### Community 30 - "Every Day"
Cohesion: 0.20
Nodes (9): All day: stories, Every Day, First hour after each post: reply to comments, How to do it right, Morning: share the 11am post to Facebook groups, The daily checklist, The line you write above it matters most, Which groups for which post (+1 more)

## Knowledge Gaps
- **195 isolated node(s):** `Before writing anything`, `11:00am: the day's main post`, `2:30pm: highlight, recap, or filler that ties in`, `7:00pm: teaser for tomorrow`, `7pm the night before: make them want it` (+190 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `Before writing anything`, `11:00am: the day's main post`, `2:30pm: highlight, recap, or filler that ties in` to the rest of the system?**
  _224 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_generate_captions.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08695652173913043 - nodes in this community are weakly interconnected._
- **Should `classify_photos.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._
- **Should `generate_captions.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10317460317460317 - nodes in this community are weakly interconnected._
- **Should `_pick_pool_photo` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Should `render_generated_images` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._
- **Should `find_food_photo` be split into smaller, more focused modules?**
  _Cohesion score 0.08695652173913043 - nodes in this community are weakly interconnected._