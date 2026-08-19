# Graph Report - backyard-brew-social  (2026-08-12)

## Corpus Check
- 105 files · ~37,408,579 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 756 nodes · 796 edges · 72 communities (71 shown, 1 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 11 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2e29c5fe`
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
- core.py
- Vendor_Communication_Templates_63fdc6dc.md
- Every Day
- fetch-and-enrich.py
- Pattern Recognition Reference
- generator_template.js
- SKILL.md
- Path B — Websites
- Auto Google Font
- Memory Management Reference
- Skill Creation Checklist
- Font Pairing Principles
- Power Design
- Typographic Rhythm System
- Core Loop: Observe → Decide → Act → Verify
- Extract a brand — the Firecrawl recipe
- Section 4: Typography
- Design Principles for Codified Slide Generation
- Section 5: Color & Contrast
- Section 6: Spatial Systems
- Section 3: Gestalt Principles
- Section 1: Cognitive Load & Attention
- Section 4: Color, Contrast & Theming
- build-pairings.py
- generate-og-images.py
- Section 11: Information Density & Charts
- Section 2: Visual Hierarchy
- Section 10: Image, Visual & Iconography Treatment
- Section 8: Slide-Specific Rules
- Section 7: Conversion & Landing-Page Structure
- Section 1: Responsive & Fluid Layout
- Section 2: Visual Hierarchy & Scanning on Screen
- Section 6: Interaction, State & Feedback
- Section 9: Accessibility
- Section 7: Alignment & Rhythm
- Design Principles for Codified Website Generation
- Section 5: Spatial Systems & Grid
- Section 3: Typography on Screen
- Section 9: Navigation & Information Architecture
- Section 8: Forms
- Section 11: Accessibility (WCAG 2.2, operational)
- Section 10: Performance (Core Web Vitals as a Design Constraint)
- Section 12: Semantic HTML, SEO & Social

## God Nodes (most connected - your core abstractions)
1. `Design Principles for Codified Slide Generation` - 17 edges
2. `Design Principles for Codified Website Generation` - 17 edges
3. `main()` - 14 edges
4. `Backyard Brew Brand Identity` - 10 edges
5. `Writing the Gemini prompt` - 10 edges
6. `Auto Google Font` - 10 edges
7. `Power Design` - 10 edges
8. `Making a Graphic` - 10 edges
9. `Making a Graphic` - 10 edges
10. `Backyard Market & Brews (Sunday)` - 9 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `compute_sizes()`  [INFERRED]
  .claude/skills/google-fonts/scripts/generate-css.py → .claude/skills/google-fonts/scripts/core.py
- `generate_html_page()` --calls--> `compute_sizes()`  [INFERRED]
  .claude/skills/google-fonts/scripts/generate-showcase.py → .claude/skills/google-fonts/scripts/core.py
- `main()` --calls--> `get_fallback()`  [INFERRED]
  .claude/skills/google-fonts/scripts/generate-css.py → .claude/skills/google-fonts/scripts/core.py
- `generate_html_page()` --calls--> `get_fallback()`  [INFERRED]
  .claude/skills/google-fonts/scripts/generate-showcase.py → .claude/skills/google-fonts/scripts/core.py
- `generate_index()` --calls--> `encode_font()`  [INFERRED]
  .claude/skills/google-fonts/scripts/generate-showcase.py → .claude/skills/google-fonts/scripts/core.py

## Import Cycles
- None detected.

## Communities (72 total, 1 thin omitted)

### Community 0 - "CLAUDE.md"
Cohesion: 0.20
Nodes (9): Backyard Brew, Data files, graphify, Nothing posts automatically, Other skills worth reaching for, Read the brand skill first, Scripts, The printed sheets (+1 more)

### Community 1 - "test_generate_captions.py"
Cohesion: 0.06
Nodes (18): manual_kind(), needs_classification(), pool_claimed(), classify_photos.py - Filename-convention helpers for photo handling.  No vision, vibe'/'spotlight' if the filename carries that override suffix, else None., True if this filename's stem contains a keyword from     config.EVENT_PHOTO_KEYW, False if the filename already carries an explicit override signal,     or isn't, The photo's real capture time, or None. Never falls back to mtime.      Use this (+10 more)

### Community 2 - "classify_photos.py"
Cohesion: 0.17
Nodes (4): Video files (iPhones drop these alongside camera-roll photos) are     never a st, Must not fall back to mtime: a fresh clone would date the whole     backlog as ', test_needs_classification_skips_video_files(), test_read_exif_time_returns_none_without_exif()

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
Cohesion: 0.14
Nodes (13): 1. Google Business Profile, 2. Reviews, 3. Tuesday and Wednesday, 4. Facebook groups, 5. Website and AI search, 6. Event concepts for the two dead windows, Baseline, from a real audit (2026-08-04 — re-check periodically, don't assume it's still current forever), Before recommending any of these (+5 more)

### Community 9 - "find_food_photo"
Cohesion: 0.09
Nodes (21): Backyard Brew: Start Here, Dropping in photos, First time on this Mac only, If something is not working, It already knows the bar, Opening it, Reading, printing, and editing these sheets, Sharing with Micah (+13 more)

### Community 10 - "find_deal_photo"
Cohesion: 0.18
Nodes (10): Constraints to respect in any recommendation, Customers and complaints, Goals, How to handle staffing in recommendations, Operations Reality, Staff (as of 2026-07-27, actively changing), The real gaps, The Tuesday/Wednesday diagnosis (+2 more)

### Community 11 - "slug_from_default"
Cohesion: 0.18
Nodes (10): Backyard Brew Brand Identity, Colors (extracted from the logo — use these exact hex values), Facts (verified — use these exact values), Fonts already established in this brand's content pipeline, Pre-flight for any Backyard Brew deliverable, Recurring weekly events (the heartbeat of the content calendar), Start here: which file answers your question, Voice (+2 more)

### Community 12 - "test_find_photo_without_event_keeps_old_behavior"
Cohesion: 0.20
Nodes (9): Backyard Market & Brews (Sunday), Contact, Messaging & tone guidelines, Musician standards, Photo situation (open gap as of 2026-07-26), Schedule, Vendor standards (screening criteria), What happens (+1 more)

### Community 13 - "test_find_food_photo_gates_occasional_keyword_to_one_day_per_week"
Cohesion: 0.14
Nodes (13): Backyard Brew: Start Here, Dropping in photos, First time on this Mac only, If something is not working, It already knows the bar, Opening it, Reading, printing, and editing these sheets, Sharing with Micah (+5 more)

### Community 14 - "test_find_food_photo_excludes_already_chosen_main_photo"
Cohesion: 0.08
Nodes (24): 11:00am: the day's main post, 11am the day of: turn it into a decision, 2:30pm: highlight, recap, or filler that ties in, 2:30pm the day of: last call before doors, 7:00pm: teaser for tomorrow, 7pm the night before: make them want it, Before delivering: run the tally, Before writing anything (+16 more)

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
Cohesion: 0.25
Nodes (7): Caption Voice Rules, Facebook vs Instagram must be genuinely different posts, not repurposed copies, Give real information, not just hype, Money language: win big yes, gambling no, Rotate the tone, not just the opener (added 2026-08-09), Structure and warmth (Micah's call, 2026-08-09), When Micah asks for a revision (added 2026-08-09)

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

### Community 27 - "core.py"
Cohesion: 0.12
Nodes (26): BM25, compute_sizes(), encode_font(), fmt_rem(), generate_css(), generate_embed(), generate_tailwind(), get_fallback() (+18 more)

### Community 28 - "Vendor_Communication_Templates_63fdc6dc.md"
Cohesion: 0.40
Nodes (4): 1. The Rundown — send when someone asks for more info or to be in the market, 2. Polite Decline — similar vendor already booked for this event, 3. Vendor Spots Full — waitlist reply, 4. Confirmed Vendor Info Sheet — send a few days before the event

### Community 30 - "Every Day"
Cohesion: 0.20
Nodes (9): All day: stories, Every Day, First hour after each post: reply to comments, How to do it right, Morning: share the 11am post to Facebook groups, The daily checklist, The line you write above it matters most, Which groups for which post (+1 more)

### Community 31 - "fetch-and-enrich.py"
Cohesion: 0.11
Nodes (26): compute_body_suitable(), compute_contrast(), compute_quality_tier(), compute_width(), fetch_url(), generate_css_import(), get_best_for(), get_expressive() (+18 more)

### Community 32 - "Pattern Recognition Reference"
Cohesion: 0.10
Nodes (20): Anti-Patterns to Avoid, Code Patterns, Detection Signals, During Work, End of Session, Knowledge Patterns, Medium Signals (Note and Watch), Over-Remembering (+12 more)

### Community 33 - "generator_template.js"
Cohesion: 0.11
Nodes (5): Entity, initializeSeed(), params, regenerate(), setup()

### Community 34 - "SKILL.md"
Cohesion: 0.11
Nodes (18): ALGORITHMIC PHILOSOPHY CREATION, CRAFTSMANSHIP REQUIREMENTS, CRITICAL: WHAT'S FIXED VS VARIABLE, DEDUCING THE CONCEPTUAL SEED, ESSENTIAL PRINCIPLES, HOW TO GENERATE AN ALGORITHMIC PHILOSOPHY, INTERACTIVE ARTIFACT CREATION, OUTPUT FORMAT (+10 more)

### Community 35 - "Path B — Websites"
Cohesion: 0.11
Nodes (18): After emitting (both paths), Common refinement patterns, Files in this skill, Output contract, Output contract, Path A — Slides, Path B — Websites, Power Design — brand-native design generator (+10 more)

### Community 36 - "Auto Google Font"
Cohesion: 0.13
Nodes (14): Auto Google Font, Data Files, Font Pair (Contrast), Full System Output, Modes, Output Includes, Pairing Contrast Types, Quality Rules (+6 more)

### Community 37 - "Memory Management Reference"
Cohesion: 0.13
Nodes (14): Always Save, Audit (run periodically), How Memory Loading Works, Memory Architecture, Memory Hygiene Operations, Memory Management Reference, Memory Update Workflow, Never Save (+6 more)

### Community 38 - "Skill Creation Checklist"
Cohesion: 0.15
Nodes (12): 1. Choose the Type, 2. Determine Scope, 3. Write the Frontmatter, 4. Structure the SKILL.md, 5. Add Supporting Files (if needed), 6. Verify, Common Skill Patterns Worth Creating, Naming Conventions (+4 more)

### Community 39 - "Font Pairing Principles"
Cohesion: 0.17
Nodes (11): 1. Structure Contrast, 2. Proportion Contrast, 3. Era Contrast, 4. Weight Contrast, Decision Tree, Font Pairing Principles, Pairing Rules, Single Font Strategy (Strict Mode) (+3 more)

### Community 40 - "Power Design"
Cohesion: 0.17
Nodes (10): A Claude skill for decks *and* websites that don't look like AI made them., Brand library — 72 pre-built systems, Credits, How the skill works (under the hood), Install, License, Power Design, The 20 slide rules, illustrated (+2 more)

### Community 41 - "Typographic Rhythm System"
Cohesion: 0.20
Nodes (9): Letter Spacing (Tracking), Line Height, Margin Rhythm, Measure (Line Length), Modular Type Scales, Responsive Strategy, Size Tiers (at 16px base), Typographic Rhythm System (+1 more)

### Community 42 - "Core Loop: Observe → Decide → Act → Verify"
Cohesion: 0.20
Nodes (9): 1. OBSERVE — Assess Current State, 2. DECIDE — Choose the Right Action, 3. ACT — Execute the Improvement, 4. VERIFY — Confirm the Improvement, Core Loop: Observe → Decide → Act → Verify, Critical Rules, Self-Healing & Continuous Improvement, Self-Improvement Session (when explicitly invoked) (+1 more)

### Community 43 - "Extract a brand — the Firecrawl recipe"
Cohesion: 0.25
Nodes (7): Common gotcha — white-fill SVG logos, Convert it into a `brand-style.md` file, Extract a brand — the Firecrawl recipe, Fast scan — what you actually need, Live examples in this repo, The one-shot scrape, What you need

### Community 44 - "Section 4: Typography"
Cohesion: 0.25
Nodes (8): Principle: Font Pairing, Principle: Hierarchy via Limited Sizes, Principle: Line-Height (leading), Principle: Line Length, Principle: Minimum Readable Size, Principle: Modular Type Scale, Principle: Tracking / Letter-Spacing, Section 4: Typography

### Community 45 - "Design Principles for Codified Slide Generation"
Cohesion: 0.29
Nodes (6): Appendix A: Numbers Cheat Sheet, Appendix B: Sources, Design Principles for Codified Slide Generation, Section 12: Williams's CRAP (the four laws everything maps to), Section 13: Resolved Contradictions, TL;DR — The 20 Rules That Matter Most for Slides

### Community 46 - "Section 5: Color & Contrast"
Cohesion: 0.29
Nodes (7): Principle: 60-30-10 Color Distribution, Principle: Color Harmony Schemes, Principle: Don't Encode Meaning in Hue Alone, Principle: HSL Reasoning over Hex, Principle: Single-Accent System, Principle: WCAG Contrast Minimums, Section 5: Color & Contrast

### Community 47 - "Section 6: Spatial Systems"
Cohesion: 0.29
Nodes (7): Principle: 8-Point Grid, Principle: Active vs Passive Whitespace, Principle: Golden Ratio (1.618), Principle: Modular / Columnar Grid, Principle: Rule of Thirds, Principle: Whitespace Ratio (negative space), Section 6: Spatial Systems

### Community 48 - "Section 3: Gestalt Principles"
Cohesion: 0.29
Nodes (7): Principle: Closure & Continuity, Principle: Common Region (containers), Principle: Figure/Ground, Principle: Proximity, Principle: Similarity, Principle: Symmetry, Section 3: Gestalt Principles

### Community 49 - "Section 1: Cognitive Load & Attention"
Cohesion: 0.29
Nodes (7): Principle: Don't Make Me Think, Principle: Fitts's Law, Principle: Hick's Law, Principle: Miller's Law (working-memory limit), Principle: One Idea Per Slide, Principle: Signal-to-Noise Ratio, Section 1: Cognitive Load & Attention

### Community 50 - "Section 4: Color, Contrast & Theming"
Cohesion: 0.29
Nodes (7): Principle: 60-30-10 on the Web, Principle: Dark Mode as a First-Class Theme, Principle: Never Hue Alone, Principle: OKLCH Ramps, Principle: Semantic Token Architecture, Principle: WCAG 2.2 Contrast (web targets), Section 4: Color, Contrast & Theming

### Community 51 - "build-pairings.py"
Cohesion: 0.53
Nodes (5): derive_contrast_type(), derive_scale(), main(), parse_weights_from_css(), Extract wght@ values for a specific font from the CSS import URL.

### Community 52 - "generate-og-images.py"
Cohesion: 0.73
Nodes (5): create_prediction(), download_image(), log(), main(), poll_prediction()

### Community 53 - "Section 11: Information Density & Charts"
Cohesion: 0.33
Nodes (6): Principle: Chart Title = Conclusion, Not Topic, Principle: Information Density Budget, Principle: Sparkline & Small-Multiples, Principle: Tufte's Data-Ink Ratio, Principle: When to Split a Slide, Section 11: Information Density & Charts

### Community 54 - "Section 2: Visual Hierarchy"
Cohesion: 0.33
Nodes (6): Principle: Color-Based Emphasis (single accent), Principle: F-Pattern / Z-Pattern Reading, Principle: Focal Point (single), Principle: Scale-Based Emphasis, Principle: Weight-Based Emphasis, Section 2: Visual Hierarchy

### Community 55 - "Section 10: Image, Visual & Iconography Treatment"
Cohesion: 0.33
Nodes (6): Principle: Full-Bleed vs Framed Imagery, Principle: Icon Sizing & Pairing, Principle: Image-Text Overlay (legibility), Principle: Photo vs Illustration vs Diagram (decision rule), Principle: Rule of Thirds in Composition, Section 10: Image, Visual & Iconography Treatment

### Community 56 - "Section 8: Slide-Specific Rules"
Cohesion: 0.33
Nodes (6): Principle: Glanceable Comprehension (3-second rule), Principle: Mayer's Multimedia Learning Principles, Principle: Presenter Mode vs Document Mode (the two valid modes), Principle: Reject the 6×6 Rule, Principle: Tufte's PowerPoint Critique (chartjunk + cognitive style), Section 8: Slide-Specific Rules

### Community 57 - "Section 7: Conversion & Landing-Page Structure"
Cohesion: 0.33
Nodes (6): Principle: Canonical Landing-Page Spine, Principle: CTA Design, Principle: One Primary Action Per View (Hick's Law applied), Principle: Scarcity & Friction, Honestly, Principle: Trust & Social Proof Placement, Section 7: Conversion & Landing-Page Structure

### Community 58 - "Section 1: Responsive & Fluid Layout"
Cohesion: 0.33
Nodes (6): Principle: Capped Measure & Container Widths, Principle: Content-Out Breakpoints, Principle: Fluid Type & Space (Utopia method), Principle: Intrinsic Layout (let the browser do the math), Principle: Mobile-First Cascade, Section 1: Responsive & Fluid Layout

### Community 59 - "Section 2: Visual Hierarchy & Scanning on Screen"
Cohesion: 0.33
Nodes (6): Principle: Don't Make Me Think (structural clarity), Principle: F-Pattern (text) / Z-Pattern (hero) Scanning, Principle: One Focal Point Per Section, Principle: Scale-Based Emphasis (web scale), Principle: The Five-Second Fold, Section 2: Visual Hierarchy & Scanning on Screen

### Community 60 - "Section 6: Interaction, State & Feedback"
Cohesion: 0.33
Nodes (6): Principle: Empty, Loading & Error States, Principle: Five States for Every Interactive Element, Principle: Motion Discipline, Principle: Perceived Performance & Optimistic UI, Principle: Touch, Pointer & Hover Parity, Section 6: Interaction, State & Feedback

### Community 61 - "Section 9: Accessibility"
Cohesion: 0.40
Nodes (5): Principle: Color-Blind Safe Palettes, Principle: Minimum Type Size for Projection, Principle: Motion & Animation, Principle: WCAG 2.2 Contrast (already in §5) + projection buffer, Section 9: Accessibility

### Community 62 - "Section 7: Alignment & Rhythm"
Cohesion: 0.40
Nodes (5): Principle: Edge Safe-Zone, Principle: Optical vs Mathematical Alignment, Principle: Strict Grid Alignment, Principle: Vertical Rhythm / Baseline Grid, Section 7: Alignment & Rhythm

### Community 63 - "Design Principles for Codified Website Generation"
Cohesion: 0.40
Nodes (5): Appendix A: Numbers Cheat Sheet, Appendix B: Sources, Design Principles for Codified Website Generation, Section 13: Resolved Contradictions, TL;DR — The 20 Rules That Matter Most for Websites

### Community 64 - "Section 5: Spatial Systems & Grid"
Cohesion: 0.40
Nodes (5): Principle: 12-Column Fluid Grid + Gap, Principle: 8-Point Spacing Scale, Principle: Consistent Radius & Elevation Tokens, Principle: Vertical Rhythm & Section Cadence, Section 5: Spatial Systems & Grid

### Community 65 - "Section 3: Typography on Screen"
Cohesion: 0.40
Nodes (5): Principle: 16 px Floor & Fluid Modular Scale, Principle: Line Length, Leading & Paragraph Rhythm, Principle: System Font Stack as a Valid Default, Principle: Web Font Loading Strategy, Section 3: Typography on Screen

### Community 66 - "Section 9: Navigation & Information Architecture"
Cohesion: 0.40
Nodes (5): Principle: Findability — Search, Breadcrumbs, Footer, Principle: Predictable Global Nav, Principle: Skip Link & Keyboard Path, Principle: Sticky Headers, Sanely, Section 9: Navigation & Information Architecture

### Community 67 - "Section 8: Forms"
Cohesion: 0.40
Nodes (5): Principle: Inline Validation & Error Recovery, Principle: Label, Type, Autocomplete, Principle: Minimum Fields & Field Grouping, Principle: Mobile Form Ergonomics, Section 8: Forms

### Community 68 - "Section 11: Accessibility (WCAG 2.2, operational)"
Cohesion: 0.40
Nodes (5): Principle: Live Regions & Dynamic Content, Principle: Names, Roles, Values (ARIA only when needed), Principle: Reduced Motion, Contrast, Zoom, Reflow, Principle: Semantic Structure & Landmarks, Section 11: Accessibility (WCAG 2.2, operational)

### Community 69 - "Section 10: Performance (Core Web Vitals as a Design Constraint)"
Cohesion: 0.50
Nodes (4): Principle: Asset Budgets, Principle: Critical Rendering Path, Principle: The Three Core Web Vitals, Section 10: Performance (Core Web Vitals as a Design Constraint)

### Community 70 - "Section 12: Semantic HTML, SEO & Social"
Cohesion: 0.50
Nodes (4): Principle: Crawlable, Indexable, Shareable, Principle: Structured Data, Principle: The Document Head Contract, Section 12: Semantic HTML, SEO & Social

## Knowledge Gaps
- **437 isolated node(s):** `Before writing anything`, `11:00am: the day's main post`, `2:30pm: highlight, recap, or filler that ties in`, `7:00pm: teaser for tomorrow`, `7pm the night before: make them want it` (+432 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Design Principles for Codified Website Generation` connect `Design Principles for Codified Website Generation` to `Section 5: Spatial Systems & Grid`, `Section 3: Typography on Screen`, `Section 9: Navigation & Information Architecture`, `Section 8: Forms`, `Section 11: Accessibility (WCAG 2.2, operational)`, `Section 10: Performance (Core Web Vitals as a Design Constraint)`, `Section 12: Semantic HTML, SEO & Social`, `Power Design`, `Section 4: Color, Contrast & Theming`, `Section 7: Conversion & Landing-Page Structure`, `Section 1: Responsive & Fluid Layout`, `Section 2: Visual Hierarchy & Scanning on Screen`, `Section 6: Interaction, State & Feedback`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Why does `Design Principles for Codified Slide Generation` connect `Design Principles for Codified Slide Generation` to `Section 4: Typography`, `Section 5: Color & Contrast`, `Section 6: Spatial Systems`, `Section 3: Gestalt Principles`, `Section 1: Cognitive Load & Attention`, `Section 11: Information Density & Charts`, `Section 2: Visual Hierarchy`, `Section 10: Image, Visual & Iconography Treatment`, `Section 8: Slide-Specific Rules`, `Section 9: Accessibility`, `Section 7: Alignment & Rhythm`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **What connects `Before writing anything`, `11:00am: the day's main post`, `2:30pm: highlight, recap, or filler that ties in` to the rest of the system?**
  _479 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_generate_captions.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05555555555555555 - nodes in this community are weakly interconnected._
- **Should `generate_captions.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10317460317460317 - nodes in this community are weakly interconnected._
- **Should `_pick_pool_photo` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Should `render_generated_images` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._