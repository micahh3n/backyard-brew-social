# Design: Undated Event/Food Photo Pools with LRU Rotation

Date: 2026-07-10
Status: Approved (talked through live in conversation before this doc was written)

## Goal / success criteria

Today, a recurring event's weekly flyer photo is either an exact dated match
(`{date}_{slug}.jpg`, which requires the owner to know and type the specific
upcoming date) or the same static `_default_art` poster, forever. The owner
wants a simpler workflow: drop a batch of photos into `photos/` any time,
with no date required. If a photo's filename contains an event's keyword
(e.g. "bingo"), it should automatically enter that event's rotation and get
used on some future week — the static poster should only ever be a last
resort, never the default experience.

Two additional pieces came out of the same conversation:
- **Food photos** (hot dogs, tacos, breakfast burritos) should attach as a
  **second photo** on the specific day(s) that food is served, not compete
  with or replace the event's own photo.
- **Rotation must not permanently retire a photo.** The owner does not want
  "used once, gone forever" — he wants to not see the *same* photo two weeks
  in a row, but any photo should be eligible to come back around once the
  rest of the pool has had a turn.

## Current state

- `generate_captions.find_photo(post_date_str, slug, want_teaser,
  default_photo)` only ever checks for an *exact* dated filename match
  (`{date}_{slug}[_art]` / `{date}_{slug}_teaser[_art]`); if none exists, it
  falls straight to `default_photo` (the static `_default_art` file from
  `recurring_events.csv`). There is no undated "pool" tier today.
- `classify_photos.py`'s vision classification handles otherwise-unlabeled
  photos, but routes matches into *separate* carousel/vibe/spotlight posts
  (`build_extra_rows()`) — never back into the main recurring event's own
  flyer. `classify_photos.VIDEO_EXTENSIONS` and `read_capture_time()`
  already exist and are directly reusable here.
- `store.load_posts()` returns full row history; nothing today computes
  "when was this specific photo filename last used" — that's new.
- `posts.csv`'s `photos` column already supports a comma-separated list
  (used today for carousel posts), but `generate_captions.render_generated_images()`
  only ever processes `photos.split(",")[0]` into the actual flyer image —
  additional photos are just inert filenames sitting in the column today.
- `build_preview.py`'s `_card_html()` renders exactly one `<img>`
  (`generated_image`) per card. A second photo in the `photos` column is
  currently invisible in the review page — the owner would have no way to
  see or grab it.
- `recurring_events.csv`'s six recurring events cover Monday-Saturday; there
  is no Sunday recurring event today.

## Approach

### New config data

`config.EVENT_PHOTO_KEYWORDS` — one entry per recurring event, matched
case-insensitively as a substring anywhere in the filename:

```python
EVENT_PHOTO_KEYWORDS = {
    "Bingo Night": ["bingo"],
    "Pickleball Open Play": ["pickleball"],
    "Tacos + Poker Club": ["poker"],
    "Ladies Night + Line Dancing": ["linedancing", "ladiesnight", "ladies"],
    "Karaoke Night": ["karaoke"],
    "Pool Night": ["pool"],
}
```

`config.FOOD_PHOTO_KEYWORDS` — one entry per food keyword, mapping to the
event(s) it attaches to as a second slide:

```python
FOOD_PHOTO_KEYWORDS = {
    "hotdog": ["Bingo Night", "Pickleball Open Play"],
    "taco": ["Tacos + Poker Club"],
    "nachos": ["Tacos + Poker Club"],
    "quesadilla": ["Tacos + Poker Club"],
    "breakfastburrito": ["Pool Night"],
}
```

Flagging explicitly: `breakfastburrito` only reaches Saturday (Pool Night)
because no Sunday recurring event exists in `recurring_events.csv` today.
"Weekends" as the owner described it doesn't fully apply until/unless a
Sunday event is added — out of scope for this spec, noted for the owner.

### Shared keyword-matching + LRU helper

A single new function, added to `generate_captions.py` alongside
`find_photo` (it already imports `classify_photos` for
`VIDEO_EXTENSIONS`/`read_capture_time`, and needs the same `parse_date`/
`slug` helpers already local to this module), does the matching + rotation
logic, used by both the event-pool lookup and the food-photo lookup:

```python
def _pool_candidates(keywords, exclude_filenames, posts_history):
    """Every eligible photo whose filename contains any of `keywords`,
    excluding anything in exclude_filenames (a event's own static
    default_photo, plus anything already claimed by suffix conventions:
    _art/_teaser/_deal/_vibe/_spotlight), paired with when it was last
    used (None if never)."""
```

Video files (`classify_photos.VIDEO_EXTENSIONS`) are excluded the same way
they already are for classification. **Critically, an event's own
`default_photo` filename must be excluded from its own pool** — e.g.
`Bingo_default_art.jpg` contains "bingo" too, and must never be treated as
a rotation candidate (it's the last-resort fallback, not a pool entrant, and
must remain reusable every week rather than being "used up").

**Selection rule (the LRU rotation):** among eligible candidates, pick the
one whose most recent appearance in `posts_history`'s `photos` columns is
oldest — a never-used photo has no last-used date at all and always wins
first. Ties among never-used candidates break toward newest real photo
capture time (`classify_photos.read_capture_time`), per the owner's
"newest first" preference for fresh content. This guarantees no photo
repeats until every other eligible photo has had a turn, while nothing is
ever permanently excluded — once the whole pool has cycled, it starts over
from whichever was used longest ago.

**Same-run awareness:** `posts_history` must include rows already built
*earlier in the same Sunday run*, not just what was already committed to
`posts.csv` before the run started — otherwise a "today" post and its own
"teaser" could both fall through to the pool and coincidentally pick the
identical undated photo, since the teaser's lookup wouldn't yet see the
just-picked row's history. `main()` already grows its `generated` list row
by row as it builds the week, so this just means passing `posts +
generated-so-far` (not a frozen snapshot from before the run) into every
pool lookup.

### Wiring into `find_photo`

`find_photo`'s documented preference order gains a middle tier:

```
today post:    {date}_{slug}[_art]  ->  pool photo (event keyword, LRU)  ->  default_photo
teaser:        {date}_{slug}_teaser[_art]  ->  {date}_{slug}[_art]  ->  pool  ->  default
```

This keeps "preference order" centralized in one function rather than
splitting it between `find_photo` and its caller. `find_photo` gains two
new parameters: `event` (to look up `EVENT_PHOTO_KEYWORDS`) and
`posts_history` (for the LRU lookup) — both already available in `main()`
at the call site.

### Food photo as a second slide

After a "today" post's main photo is resolved (not for teasers — explicitly
scoped out per the conversation), a separate lookup checks
`FOOD_PHOTO_KEYWORDS` for any keyword mapped to this event. If an eligible
food photo exists (same LRU rule, independent rotation from the event pool),
its filename is appended to the row's `photos` column:
`"{main_photo}, {food_photo}"`. This never blocks or delays the main post —
if no food photo is eligible, the row just has one photo, exactly as today.

The food photo is **not** run through `flyer_render`/text-overlay —
`render_generated_images()` already only processes `photos.split(",")[0]`,
so the food photo stays a plain, unprocessed reference in the CSV, the same
way carousel posts' 2nd-through-5th photos already work today. The owner
attaches it manually as a second slide when posting, same manual workflow
as everything else post-Meta-API-pivot.

### Preview page: show the second photo

`build_preview._card_html()` currently renders one `<img>`
(`generated_image`). It needs to additionally render any photos beyond the
first in the row's `photos` column, referenced directly from
`config.PHOTOS_DIR` (not `generated_image`, since they're never processed)
so the owner can actually see and grab the food-photo second slide during
review. A row with only one photo renders exactly as it does today — no
regression for the common case.

### Excluding pool-claimed photos from vision classification

A photo claimed by an event or food keyword must never also be classified
as vibe/spotlight/carousel material — one job per photo, and no wasted API
call. The keyword-matching check becomes a shared helper (used by both the
new pool lookup and by `classify_new_photos()`'s eligibility filter) rather
than duplicating substring-matching logic in two places.

## Testing strategy

No browser/API required for any of this — all string/logic-level, fast:

- Keyword matching resolves correctly across representative filenames
  (case-insensitive, substring anywhere, multiple keywords per event).
- An event's own `default_photo` filename is never treated as a pool
  candidate for its own event.
- LRU selection: never-used beats previously-used; among previously-used,
  oldest-last-used wins; ties among never-used break toward newest capture
  time.
- Exact dated match still takes priority over the pool (regression guard on
  `find_photo`'s existing contract).
- Food second-slide: appended only for its mapped event(s), only on "today"
  posts, never blocks the main post when no eligible food photo exists.
- `classify_photos`: keyword-claimed filenames are excluded from
  classification candidates.
- `build_preview`: a two-photo row renders both images; a one-photo row is
  unchanged from current behavior.

## Operational changes

None. No new dependencies, no CI changes — everything here operates on the
existing `photos/` folder and `posts.csv` structure.

## Explicitly out of scope

- Adding a Sunday recurring event (the `breakfastburrito` weekend gap noted
  above stays a gap until the owner decides he wants a Sunday event at all).
- Food second-slide on teaser posts (today-post only, per the conversation).
- Any change to one-off/pending event photo handling — this feature is
  scoped to the six recurring events in `recurring_events.csv`.
- Any change to the existing `_deal` photo-suffix mechanism — separate,
  untouched.
