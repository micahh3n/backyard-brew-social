# How To Use This Every Week (the whole job)

Once setup is done, your entire weekly involvement is **one Sunday sitting**:
drop photos during the week, review + manually schedule on Sunday, done.

> **Upgrading from the old auto-posting system?** Open `posts.csv` and check
> for any leftover rows still marked `status = approved` from before this
> update -- those won't post automatically anymore (the hourly posting job is
> gone). For each one, either re-add it as a fresh row so it goes through
> the new Sunday flow, or manually post it once yourself and then change its
> status to `scheduled`.

---

## During the week

**Drop in this week's photos** (optional but recommended)
Drag photos into the `photos` folder in GitHub Desktop. **Naming them well
also saves API cost** — a photo the system can match by filename never has
to be sent to Claude to be looked at, which is both free and more reliable
than a guess.

*Tied to a specific night's event:* name it `{date}_{event keyword}[.jpg/.png]`:

| You drop this | What it does |
|---|---|
| `2026-07-13_bingo.jpg` | Fresh photo for Monday's Bingo post |
| `2026-07-13_bingo_teaser.jpg` | Different photo for the night-before teaser |
| `2026-07-13_bingo_deal.jpg` | A photo of that day's featured drink deal — gets composited into a small callout badge on the flyer |
| `2026-07-13_bingo_art.png` | A finished graphic you made — posted exactly as-is, no editing |
| *(nothing)* | Falls back to the default photo — still works |

The exact event keywords the system knows today:

| Day | Event | Keyword |
|---|---|---|
| Monday | Bingo Night | `bingo` |
| Tuesday | Pickleball Open Play | `pickleball` |
| Wednesday | Tacos + Poker Club | `poker` |
| Thursday | Ladies Night + Line Dancing | `linedancing` |
| Friday | Karaoke Night | `karaoke` |
| Saturday | Pool Night | `pool` |

For a special one-off event, use whatever keyword you put in that event's
`posts.csv` row.

*Not tied to a specific dated event* (a candid shot, a vibe/atmosphere photo,
a shoutout-worthy moment): drop it with any name and the system will look at
it and decide — but if you already know what it is, tag it and skip the
guess entirely, for free:

| You drop this | What it does |
|---|---|
| `campfire_vibe.jpg` | A "behind the scenes"-style candid post — no AI look required |
| `regular_winning_spotlight.jpg` | A community shoutout post |
| *(no tag, just a normal name)* | The system looks at it once and decides — see below on how that's kept cheap |

**Why this doesn't run up a bill even if you drop photos constantly:** every
photo the system has to actually *look at* (no matching filename, no
`_vibe`/`_spotlight` tag) is sent to Claude exactly **once, ever** — the
result is cached by filename (`photo_classifications.json`, committed back
to the repo automatically), so a photo that doesn't turn into a post never
gets re-checked on a future Sunday. You can keep dumping photos in
year-round without that cost compounding.

**Add any special events** (only if you have one)
Open `posts.csv` and add ONE row for a party/guest/holiday. Fill in: `date`, `photos`,
`event`, `key_details`, `platforms`. Leave the rest blank.
- Want it promoted repeatedly leading up? Also fill **`promote_from`** with the date to
  start the hype. The system builds the whole countdown for you.
- Want to cancel one night this week? Add a row with that `date` and set `status` = `skip`.

Push it up (GitHub Desktop: **Commit to main** → **Push origin**) whenever convenient.

---

## Sunday: the ~1 hour review-and-schedule sitting

**1. Pull the week's generated content**
GitHub Desktop → **Fetch/Pull origin**. The Sunday job runs on its own and fills
in everything: captions, flyer images, and a visual preview page.

**2. Open `preview/this-week.html` in your browser**
Double-click the file (or open it from File Explorer). You'll see every post
for the week as a card: the finished image, the scheduled time, and both
captions underneath, in order. This is your at-a-glance review — no
spreadsheet-reading required for a normal week.

**3. Edit anything you want in `posts.csv`**
Only open the spreadsheet if you want to change a caption's wording or a
`scheduled_time`. Every column is already filled in for you:
- `fb_caption` / `ig_caption` — edit any wording you want, just type over it.
- `scheduled_time` — change it if you want a different time (format: exact `YYYY-MM-DD HH:MM`).
- `generated_image` — the finished flyer image for that row; this is what you'll attach.
- Don't want a post to go out? Set its `status` to `skip`.

**4. Manually schedule each post**
For each post (in the order shown in the preview page): open Facebook or
Instagram's own **"Schedule Post"** feature (in the app, or in Meta Business
Suite), paste the caption, attach the image at the path shown in
`generated_image`, and set the date/time already suggested. Repeat for each
post — with 2-3 posts/day, expect roughly 15-20 posts to schedule most weeks,
a couple minutes each.

**5. Mark it done and push**
Change that row's `status` from `needs_review` to `scheduled` (just for your
own tracking — nothing reads this back). Once you're through the list,
**Commit + Push** one more time. That's it for the week.

---

## What happens automatically (you do nothing)

- **Every Sunday**, the system generates the whole week's captions, flyer
  images (with real-photo template variety), and the visual preview page.
- **You get 2 posts a day minimum, occasionally 3** — the system fills quiet
  days with real-photo content (behind-the-scenes shots, community
  spotlights, event recaps) and evergreen content (a featured Wisconsin
  drink, a course/trail feature, or a weather-tied post), so posting is
  never sparse even on days without a scheduled event.
- **Suggested posting times** are already baked in (late-morning for the
  day's main post, afternoon for the occasional 3rd post, evening for the
  next day's teaser) — you're free to change any of them.

---

## How to know it's working

- **`status.log`** in the repo is a plain-English diary: "Sunday job done:
  generated N new post rows" means success; a "flyer render failed" line
  tells you exactly which row fell back to its plain photo and why. A
  "caption API usage" line shows real token/cache numbers for that run, if
  you ever want to sanity-check cost.
- **GitHub → Actions tab** shows a green check for the Sunday run.
- If `preview/this-week.html` looks thin some week (only 1-2 posts on a
  quiet day), that's the "never forces a post" safety net — drop a couple
  more real photos into `photos/` and next Sunday will have more to work with.

---

## The golden rules

- You **only edit** `recurring_events.csv` (when your schedule changes) and
  `posts.csv` (special events, caption tweaks, `scheduled`/`skip` status).
  Everything in `scripts/` runs itself.
- **Nothing posts automatically anywhere.** You paste every post yourself
  into Facebook/Instagram's own scheduler — the system's whole job is to get
  the caption + image ready for you, not to touch your accounts.
- There is **no Meta/Facebook developer setup anywhere in this system** —
  only your Anthropic API key (`ANTHROPIC_API_KEY` in GitHub Secrets).
