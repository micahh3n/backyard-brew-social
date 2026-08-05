# Design: Manual-Posting Workflow, Authentic Captions, Real-Photo Flyers

Date: 2026-07-09
Status: Approved, pending spec review

## Goal / success criteria

Grow Backyard Brew's social reach and foot traffic by making the weekly content
engine produce posts that read as genuinely human and drive sharing/engagement
beyond the existing follower base, while cutting the maintenance burden of
Meta API auto-posting (App Review, token refresh) down to zero. Success looks
like: a ~1 hour Sunday session produces a week's worth of ready-to-paste posts
(caption + finished image) that the owner is comfortable publishing largely
as-is, using platform-native scheduling.

This spec does not attempt to guarantee engagement outcomes (no automation
can) — it defines the concrete levers available: shareability baked into
caption structure, real-photo-based eye-catching visuals, unbroken weekly
consistency, and a guaranteed 2-posts/day minimum (3 occasionally) at
reasoned, industry-benchmark posting times (Sections 7-9).

## Current state (context)

- `sunday-generate.yml` (GitHub Action) runs `generate_captions.py` weekly,
  writing new rows to `posts.csv` at `status=needs_review`. This job is kept.
- `hourly-post.yml` runs `post_to_meta.py` hourly, posting `approved` rows to
  FB + IG via the Meta Graph API, and is where `process_photos.py`'s flyer
  building currently happens (at post-time, not generation-time). Facebook
  posting is blocked on Meta App Review (`pages_manage_posts` Advanced
  Access); Instagram posting works today.
- `anthropic_client.py` generates fb/ig captions from a system prompt that
  hard-mandates several elements (hook question, Wisconsin-made mention,
  membership plug, "Tag your ___" close) on every single post, producing
  visibly formulaic output (verified against real generated captions in
  `posts.csv`).
- `process_photos.py` already implements a real-photo flyer system (retro
  badge: gold border, headline, logo watermark) via PIL — no AI image
  generation, fully free, always composites onto a real photo.

## Changes

### 1. Retire Meta API involvement entirely (posting AND voice-anchor)

- Delete `.github/workflows/hourly-post.yml` and `scripts/post_to_meta.py`.
- Delete `scripts/meta_client.py` outright, including the read-only
  `recent_page_posts()` "voice anchor" call. Owner explicitly chose zero Meta
  developer console involvement of any kind over the authenticity boost of
  matching literal past posts — captions still follow the detailed
  brand-voice rules in the system prompt (Section 5), just without live
  examples of past posts.
- `SETUP.md` is simplified to drop Meta developer-app/token setup entirely
  (Parts 2-6 as currently written) — the only remaining requirement is a
  GitHub account and an Anthropic API key. No `META_*` secrets exist at all.
- Drop the Meta App Review effort — no longer needed since nothing posts via
  API for either platform (Instagram's existing working auto-post is also
  turned off, for one consistent manual workflow rather than a
  partially-automated one).
- Remove token-refresh maintenance/docs tied to `META_PAGE_ACCESS_TOKEN`
  posting use.

### 2. Move flyer generation into the Sunday job

- `process_photos.process()` is called from within `generate_captions.py`'s
  Sunday run (not from the retired hourly job), once per generated row,
  writing the finished image to `photos/_generated/` (the existing
  `config.GENERATED_DIR`).
- `posts.csv` gains a column (e.g. `generated_image`) pointing to that output
  file, so the owner can find the exact image to attach when scheduling
  manually.
- Same graceful-degradation rule as today: if flyer rendering fails for any
  reason, fall back to the plain processed photo rather than blocking the row
  from appearing for review.

### 3. Real-photo deal compositing (no drink-name library)

- New filename suffix convention, matching the existing `_teaser`/`_art`
  pattern the owner already uses: `_deal` (e.g.
  `2026-07-14_pickleball_deal.jpg`).
- Matched by date + event slug exactly like today's teaser-photo lookup — no
  drink names, no separate asset folder, no renaming burden.
- If a `_deal` photo exists for that date/event, the flyer builder composites
  it into the graphic alongside the deal callout text (extends the existing
  logo-watermark compositing technique to this second asset).
- If no `_deal` photo is dropped, the flyer simply uses the normal event
  photo — this feature never blocks or degrades a post.

### 4. Flyer template variety

- Expand `process_photos.py` from one layout (retro badge) to 2-3 rotating
  layouts (e.g. current retro badge, a cleaner minimal-caption style, a bold
  poster style), chosen per post so consecutive weeks don't look visually
  identical.
- Selection logic: rotate deterministically (e.g. based on a hash of
  event+date, or round-robin against recent history) so it's varied but
  reproducible, not random-flaky between re-runs.

### 5. Caption authenticity rework

Problem (verified against real output): the system prompt currently mandates
the same elements in the same order on every post (hook question →
Wisconsin-made mention → membership plug → "Tag your ___"), producing
visibly formulaic captions.

Fix, in `anthropic_client.py`'s `_system_prompt()` / `_user_prompt()`:

- **Always included, never varies:** accurate event info for that day (what,
  when, key details) — this is the one non-negotiable constant.
- **Always included, wording/mechanism varies:** a share/engagement driver
  per post — but rotate the *mechanism* (tag-a-friend, comment-bait question,
  save-bait detail, a naturally quotable specific line) rather than repeating
  "Tag your ___" every time. The instinct to drive sharing stays; the
  execution rotates.
- **Frequent but variable wording:** membership/deal plugs stay common (the
  owner explicitly still wants them often) but must be phrased differently
  post to post — instructed to sound like a person casually working it into
  a different sentence each time, not reciting a fixed line.
- **Structural variety:** explicit instruction to vary the opening move
  (not always a question — sometimes a statement, a fragment, an aside).
  With the Meta voice-anchor feature removed (Section 1), there are no live
  "recent actual page posts" to reference — variety instead comes from the
  rotating-mechanism rules above plus the repetition guard below.
- Extend the existing repetition-guard (`avoid_examples`, sourced from this
  repo's own `posts.csv` history — no Meta API involved, currently used to
  avoid repeating exact past captions for the same event) to also cover
  *structure*, not just wording — e.g. pass along which "move" recent posts
  for this event used, and instruct the model to pick a different one.

This is a prompt-engineering-only change: no new infrastructure, no new
dependencies. Low risk, easy to iterate on after a few real weeks of output.

### 6. Bookkeeping for manual posting

- `posts.csv` gains a way to mark a row as handled after the owner pastes it
  into the native scheduler (e.g. a `status` value like `scheduled`, distinct
  from the old `posted`, which was only ever set by the now-retired API
  posting job). Optional for the system to function — purely for the owner's
  own tracking.

### 7. Guaranteed posting cadence: 2/day minimum, 3 occasionally

Today the system only reliably produces posts on days with a recurring event
(a same-day "today" post + a "teaser" post the evening before tomorrow's
event), and the extra content types (vibe/spotlight/carousel) are capped at
4 total per week — nowhere near daily. Since recurring events already cover
6 of 7 days, most days already get 2 baseline posts; the gap is (a) the one
day with no recurring event, and (b) hitting an occasional 3rd post on other
days.

- Raise `MAX_EXTRA_POSTS_PER_WEEK` to a per-day allowance (effectively: every
  day gets at least one extra/fill post if its baseline is under 2, and some
  days get a bonus 3rd) rather than a flat weekly ceiling of 4.
- Fill posts draw from a **mix of existing and new content types** (owner's
  explicit choice): existing vibe/behind-the-scenes, community spotlight, and
  carousel recaps, **plus** new evergreen buckets (Section 8) for more
  variety than cycling the same few types on repeat.
- The existing anti-stacking logic (`quietest_day`, daily/weekly caps) is
  kept as the mechanism — just retuned so "quietest day" still gets a post
  instead of zero.

### 8. New evergreen content types

To support 2-3 posts/day without the fill content feeling repetitive, add a
small set of new recurring buckets alongside the existing vibe/spotlight/
carousel types:

- **Wisconsin spotlight** — features a specific Wisconsin-made beer/wine/
  seltzer the bar carries (ties into the existing "100% Wisconsin-made"
  brand pillar, gives evergreen material with no photo dependency beyond
  what's already on hand).
- **Course/trail feature** — highlights the disc golf course or hiking
  trails (a hole, a trail view, a tip), reinforcing the "bar + disc golf +
  hiking, nowhere else like it" positioning.
- **Weather-tied post** — "perfect day for disc golf/hiking" framing tied to
  actual local weather. Uses Open-Meteo (free, no API key, no signup) for the
  forecast lookup; degrades gracefully to a generic outdoor-vibes post (no
  weather-specific claim) if the call fails, same fallback philosophy as
  everything else in this pipeline.

These reuse the same caption-generation pipeline (Section 5's voice rules
still apply) and the same flyer-compositing pipeline (Sections 2-4) — they
are new *content angles*, not new infrastructure.

### 9. Optimal posting times

Formalizes the "default-fallback (not yet personalized)" schedule in
`config.py` into a documented, intentional 2-3-slot daily schedule, grounded
in general hospitality/local-business social media benchmarks (not yet
personalized to this account's own Insights data — see below):

- **Late-morning slot (~11:00 AM):** the primary event-day announcement.
  Catches the lunch-break scrolling window where people commonly decide
  same-day evening plans.
- **Afternoon slot (~2:30-3:00 PM):** secondary touchpoint used for the
  occasional 3rd post / fill content (evergreen posts, spotlights) — a
  well-documented secondary engagement window that avoids bunching two posts
  too close to the morning slot.
- **Evening slot (~7:00-7:30 PM, 9:00 PM Saturdays):** the teaser/
  anticipation post for tomorrow's event, or the day's closing touchpoint —
  catches the evening scroll window when people plan next-day/weekend
  activities.

This replaces vague per-day defaults with an explicit, reasoned table (kept
in `config.py`'s `DEFAULT_TIMES`, updated to include the new afternoon slot).
`TIMING_SOURCE` stays flagged as industry-default until the owner optionally
pulls real "when your audience is most active" data from native IG/FB
Insights (a manual, no-API step — just reading the chart in the app), at
which point the table can be swapped for account-specific times.

### 10. Visual weekly preview page

The owner wants to *see* the week's assembled posts at a glance rather than
reading a spreadsheet. The Sunday job additionally generates a static HTML
file, `preview/this-week.html`, listing every generated row as a simple
visual card in schedule order: the finished flyer image, the scheduled
date/time, and both captions (fb/ig) as plain text underneath. No server, no
build step — just a plain HTML file with inline CSS that opens directly in
any browser (double-click, or `git pull` then open in File Explorer). This
is a pure read-only convenience view generated from the same `posts.csv`
data — `posts.csv` remains the actual source of truth the owner edits.

## Sunday workflow (end state)

1. During the week: owner drops photos into `photos/` as usual, optionally
   including a `_deal` photo when a specific drink is on special that day.
2. The Sunday GitHub Action runs automatically: generates captions (Section
   5 rules), builds flyer images (Sections 2-4), writes it all to
   `posts.csv` + `photos/_generated/` at `status=needs_review`, and builds
   `preview/this-week.html` (Section 10).
3. Owner: `git pull`, opens `preview/this-week.html` in a browser for an
   easy visual scan of the week; opens `posts.csv` alongside it only if they
   want to edit a caption's text or the scheduled time.
4. For each post: owner manually pastes the caption + attaches the generated
   image into Facebook/Instagram's native "Schedule Post" feature, setting
   the suggested date/time.
5. Owner marks the row `scheduled` in `posts.csv` (optional bookkeeping) and
   commits/pushes once, done for the week (~1 hour total).

## Error handling

Unchanged philosophy from the current system — a single bad row, missing
photo, or API hiccup must never block the rest of the week's rows from being
generated and shown for review:

- Missing dated photo → falls back to the event's default photo (existing
  behavior).
- Caption API failure → falls back to templated caption (existing behavior).
- Flyer render failure → falls back to the plain processed photo, not a
  crash (existing behavior extended to the new templates/compositing step).
- Malformed CSV row → isolated and logged, doesn't crash the whole Sunday run
  (existing behavior).

## Explicitly out of scope

- Any AI image-generation API (Gemini/Imagen, DALL-E, etc.) — rejected per
  owner's authenticity requirement; real-photo compositing only.
- A drink-name-based photo library/matching system — rejected as too much
  manual naming burden; superseded by the `_deal` suffix convention (Section
  3).
- Engagement-data-driven caption feedback loop (learning from which past
  posts performed best) — natural next step once real engagement data
  exists, not built now.
- Any change to Instagram's posting mechanism beyond turning it off (owner
  chose full-manual consistency over partial automation).
- The Meta voice-anchor feature (`recent_page_posts()`) — explicitly dropped
  along with all other Meta API involvement (Section 1); owner chose zero
  developer-console setup over this authenticity boost.
- Any dynamic/interactive preview (a real web app, live editing in-browser)
  — the weekly preview (Section 10) is a static, read-only HTML snapshot
  only; `posts.csv` stays the single place edits happen.
