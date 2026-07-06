# Content Variety Expansion — Design Spec

Date: 2026-07-06
Status: Approved by owner, ready for implementation planning.

## Goal

The current system posts exactly two things per event: a "today" post and a
"tomorrow" teaser. That's reliable, but on its own it reads as a content mill,
not a bar people want to follow. This spec adds three new, opportunistic post
types — carousels, behind-the-scenes/vibe posts, and community spotlights — so
the account grows real engagement and personality on top of the existing
event-promotion cadence, without becoming spammy and without adding manual
work to the owner's weekly routine.

This expansion sits entirely inside the existing Sunday-generate /
owner-approves / hourly-post architecture already built in
`backyard-brew-social`. It does not change that architecture, the CSV-only
review workflow, or any existing recurring/one-off/countdown-campaign logic.

## New content types

### 1. Carousel
Triggered automatically when 3+ plain photos (no override suffix) share the
same real-world event/night, as determined by the classification step below.
Generates one *additional* post — a swipeable multi-photo recap — alongside
the normal today/teaser posts for that event. Never replaces the single-photo
today post.

### 2. Behind-the-scenes / vibe
Candid, non-event, no-CTA content — a sunset on the course, a regular losing
at pool, the bartender prepping. Voice is personality-first: no foot-traffic
CTA, no membership mention, no urgency. Its job is likability, not conversion.

### 3. Community spotlight
A dedicated shoutout post — a review screenshot, a posed victory/celebration
photo, a named regular's win streak. Voice specifically credits the
person/moment. The owner has already secured permission from anyone
photographed before the photo ever reaches this system, so no rights-flagging
step is needed here — this is purely an editorial/format decision, not a
consent gate.

All three land in `posts.csv` at `status = needs_review`, exactly like every
other row in the system today. The owner's weekly review habit doesn't
change — the pool of what shows up in that review just gets richer.

## Photo classification (the mechanism that makes "no renaming required" work)

New script: `scripts/classify_photos.py`, runs as part of the Sunday job,
before caption generation.

For every photo in `/photos/` not yet consumed by a previous run:

1. **Read the embedded EXIF timestamp.** Used only as a secondary signal:
   (a) picking which week's occurrence of a recurring event to attach an
   ambiguous photo to, and (b) detecting bursts of photos taken within a few
   minutes of each other, for carousel grouping. It is explicitly NOT the
   primary signal for "what event is this" — a bingo-themed photo taken on a
   Wednesday must still classify as bingo content.
2. **One vision classification call to Claude per photo.** Asks whether the
   image matches a known recurring event (bingo, pickleball, poker, disc golf
   league, line dancing, pool night), reads as a candid/atmosphere shot, or
   reads as spotlight-worthy (review screenshot, posed victory/celebration
   moment). This call classifies only — it does not write captions; caption
   generation continues to use the existing brand-voice prompt in
   `anthropic_client.py`, keyed off the event/post-type it's told, not the
   pixels.
3. **A filename suffix always overrides the AI's guess**, exactly like `_art`
   already overrides auto-suggested enhance mode today. The owner can still
   rename files to force a specific date, event, or post type whenever they
   want deterministic control — this is optional per-file, not required.
4. **Low-confidence photos are left alone.** Not forced into a post. They
   remain in `/photos/` as unconsumed candidates for a future run, once either
   the owner tags them or more surrounding photos give the classifier enough
   context.

### Cost/scale note
Classification is a lightweight vision call, not a generation call. Batches
of 30-50 photos in one Sunday run remain inexpensive (low single-digit cents)
and add well under a minute to the job, even at "upload many at once" scale.

## Volume control (avoiding spam)

Extra posts are capped at roughly 3-4/week, but this is a **ceiling, not a
quota** — the system never manufactures a carousel/vibe/spotlight post just to
hit a number. Each Sunday, every photo group that clears the classifier's
confidence bar becomes a candidate; if candidates exceed the cap, the
strongest matches (clearest classification, most photos in a carousel group)
are kept and the rest are left unconsumed for a future week. A thin photo
week might produce only one extra post, or zero — expected behavior, not a
bug, consistent with the existing system's "skip rather than force" pattern
(e.g. Sunday's optional teaser, campaign milestones already in the past).

**Hard daily cap, enforced in code — not an emergent side effect.** No matter
how many unused photos are sitting in `/photos/` (10 or 100), the system will
never schedule more than the normal today + teaser posts for that day, plus
at most **one** extra (carousel/vibe/spotlight), per platform, per day. This
is checked explicitly before anything gets a `scheduled_time` — it is not
just a hoped-for average from the weekly cap and spreading rules below. A
large photo backlog builds a longer runway of future candidates; it never
becomes pressure to post more right now.

## Scheduling for extra post types (no stacking, no spam)

The existing timing table only covers "today" and "teaser" slots. Extra posts
need their own placement rules so they never cluster:

- **One extra post per day, maximum**, enforced by the hard daily cap above.
  If three different bingo-themed carousels all qualify for the same week,
  only one gets scheduled — the others wait in the candidate pool for future
  weeks rather than piling onto Monday because they all matched "bingo."
- **Carousels post the day *after* the event they recap** (a "look back at
  last night" framing), in the evening engagement window — the same
  reasoning already used for teasers: evening is when people are relaxed and
  scrolling, not out living their lives.
- **Vibe and spotlight posts get slotted onto whichever day of the week is
  otherwise quietest** (i.e. doesn't already have 2 posts scheduled), using
  the same late-morning/evening windows already validated for today/teaser
  posts — not an arbitrary new time.
- These slots are marked with the same `TIMING_SOURCE = "default-fallback"`
  label as the rest of the schedule, and get folded into the same future
  Insights-driven optimal-time lookup once real account data exists — extra
  post types are not a separate scheduling system, just new entries in the
  same one.

## Caption voice differences

All post types share the same base brand-voice system prompt already defined
in `anthropic_client.py` (energetic, community-first, Wisconsin-proud, "friend
texting you about a cool spot," hook-first-line). Only the framing and CTA
rules change per type — the underlying voice never forks into a separate
writing style, so the account keeps sounding like Backyard Brew even as
content variety goes up:

- **Carousel:** same event-specific brand voice as an ordinary today/teaser
  post, since it's still promoting that night — just framed as a recap across
  multiple photos rather than a single moment.
- **Vibe/BTS:** no CTA, no membership mention, no urgency framing. Short,
  warm, personality-driven copy about the specific moment shown.
- **Spotlight:** built around crediting the person/moment by name where
  known. If the owner supplied context via an optional matching `posts.csv`
  row (same pattern as any one-off event — fill `event`/`key_details`), the
  caption uses those real facts. If not, the AI writes a plausible generic
  shoutout directly from what the photo shows (e.g. it cannot read a name off
  a photo, so a generic version may need a quick name fix before approval —
  same "review before approving" expectation as any other row).

## Caption freshness — closing the past_examples() gap

`generate_captions.py` already contains a hook, `past_examples()`, intended to
feed the caption prompt real reference captions so the AI writes in Backyard
Brew's actual established voice. Today it is a stub that always returns an
empty list — a real gap, and specifically the kind of gap that causes
"here we go again, same copy-paste post" drift over months of unattended
weekly runs, because the model currently has no memory of what it already
wrote for a given event.

This gets fixed as part of this feature, with two distinct jobs feeding into
one prompt addition:

1. **Voice anchor (positive examples).** A small set of the bar's real past
   captions (pulled once via the Graph API's post-history read access, per
   the original spec) shown to the model as "this is what authentic Backyard
   Brew voice sounds like" — unchanged from the original design, just no
   longer a stub.
2. **Repetition guard (negative examples) — the new piece.** Before
   generating a caption for a given event, `generate_captions.py` looks back
   through `posts.csv`'s own history (rows already `posted` or `approved` for
   that same event, most recent first) and pulls the last several real
   captions the system itself wrote for it. Those go into the prompt as an
   explicit instruction: *"here is exactly what you said the last few times
   for this event — do not reuse these hooks, phrases, sentence openings, or
   structures; write something genuinely different."*

The negative-example guard matters more than the positive one for the
specific "copy-paste" failure mode — voice-matching alone can still produce
structurally repetitive posts if the model isn't also told what to actively
avoid repeating. Both run together: authentic voice, never the same post
twice.

This requires no new files or schema — `posts.csv` already retains prior
weeks' rows (they aren't deleted after posting), so the history is already
sitting there; `generate_captions.py` just needs to actually read it.

## Posting mechanics: carousels on Meta's API

`meta_client.py` gains two new code paths, since Facebook and Instagram
handle multi-photo posts differently:

- **Instagram carousel:** each photo is uploaded as its own media container
  first, then bundled into one parent carousel container, then published as
  a single post. The existing hashtag-first-comment and Story-repost
  behavior still applies once the carousel is live (the Story repost uses
  just the single best/first photo from the set, since Stories don't support
  carousels).
- **Facebook multi-photo post:** each photo is uploaded unpublished first,
  then referenced together in one published post (the standard "swipeable
  album" style Facebook post).

The `photos` column already supports comma-separated filenames (built in from
day one for a different reason), so a carousel row simply lists 3+ filenames
instead of one — no schema change.

### Error handling for carousels
If any single photo in the set fails to upload, the whole carousel post is
held back (not partially published) and retried on the next hourly run —
consistent with the rest of the system's "never mark posted unless it fully
succeeded" rule.

## What does NOT change

- `posts.csv` schema — no new columns. `post_type` is already free text
  (`today`, `teaser`, `reminder_Nd`, and now also `carousel`, `vibe`,
  `spotlight`); `photos` already supports comma-separated filenames.
- The Sunday-generate / owner-approves / hourly-post job split.
- The CSV-only review workflow — explicitly reconsidered and reconfirmed
  during design (owner chose to keep it CSV-only for now rather than add a
  review UI; a visual review page remains a possible separate future
  project, out of scope here).
- All existing recurring-event, one-off, and countdown-campaign logic.

## Open items for implementation planning

- Exact vision-classification prompt wording and confidence threshold for
  "match" vs. "leave unclassified."
- Where classification results get cached/tracked so a photo already used
  once isn't reclassified or reused indefinitely (mirrors the existing
  `existing` dedupe-by-(date, event, post_type) pattern in
  `generate_captions.py`).
- Confirm Instagram/Facebook API rate limits are comfortable for the added
  carousel container calls at expected weekly volume.
