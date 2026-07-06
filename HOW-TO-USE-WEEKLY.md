# How To Use This Every Week (the whole job)

Once setup is done, your entire weekly involvement is **three things**: drop photos,
approve on Sunday, done. Here's the rhythm.

---

## The 10-minute Sunday routine

**1. Drop in this week's photos** (optional but recommended)
Drag photos into the `photos` folder in GitHub Desktop. Name them by date + event:

| You drop this | What it does |
|---|---|
| `2026-07-13_bingo.jpg` | Fresh photo for Monday's Bingo post |
| `2026-07-13_bingo_teaser.jpg` | Different photo for the night-before teaser |
| `2026-07-13_bingo_art.png` | A finished graphic you made — posted exactly as-is, no editing |
| *(nothing)* | Falls back to the default photo — still works |

The event keyword to use in the filename is the first word the system knows:
`bingo`, `pickleball`, `poker`, `discgolf`, `friday`, `saturday`. For a special
event, just match whatever you named the photo in the `posts.csv` row.

**2. Add any special events** (only if you have one)
Open `posts.csv` and add ONE row for a party/guest/holiday. Fill in: `date`, `photos`,
`event`, `key_details`, `platforms`. Leave the rest blank.
- Want it promoted repeatedly leading up? Also fill **`promote_from`** with the date to
  start the hype. The system builds the whole countdown (≈2 wks / 1 wk / 3 days / night-before
  / day-of) for you, each with a different caption. One row = the whole campaign.
- Want to cancel one night this week? Add a row with that `date` and set `status` = `skip`.

**3. Push it up**
In GitHub Desktop: bottom-left summary box → **Commit to main** → top → **Push origin**.
This sends your photos and edits to the system.

**4. (Sunday evening) Review what it wrote**
The Sunday job runs automatically Sunday afternoon and fills `posts.csv` with the week's
posts at `status = needs_review`. In GitHub Desktop click **Pull origin** to get them, then
open `posts.csv` and for each post:
- Read `fb_caption` and `ig_caption`. Edit any wording you want — just type over it.
- Check `scheduled_time` — change it if you want a different time.
- Check `enhance` — `text_overlay` makes a flyer, `none` keeps the real photo. Change if you like.
- When happy, change `status` from `needs_review` to **`approved`**.
- Don't want a post to go out? Set its `status` to `skip`.

Then **Commit + Push** one more time. **That's it for the week.**

---

## What happens automatically (you do nothing)

- **Every hour**, the system checks for `approved` posts whose time has arrived and posts them.
- Each Instagram post also **auto-reposts to your Story** and drops the **hashtags in the
  first comment** (your caption stays clean).
- Every post gets the **Backyard Brew location tag** automatically.
- After a post publishes, its `status` flips to `posted` so it never double-posts.

---

## How to know it's actually working

- **The posts appear** on your Facebook and Instagram at their scheduled times. (Best proof.)
- **`status` changes to `posted`** in `posts.csv` after each one goes out (Pull origin to see it).
- **`status.log`** in the repo is a plain-English diary: "POSTED 'Bingo Night'…" lines mean
  success; any "POST FAILED" or "MISSING PHOTO" line tells you exactly what to fix.
- **GitHub → Actions tab** shows a green check for every hourly run.

## When something's off

| You see | What it means / do |
|---|---|
| `MISSING PHOTO` in status.log | The photo filename in that row isn't in `photos/`. Fix the name or drop the file, push. |
| A post stuck at `approved`, never `posted` | Its time hasn't passed yet, OR a post failed and is retrying — check status.log. |
| `TOKEN EXPIRES IN x DAYS` | Your Meta token is near its 60-day limit. Redo Parts 3c–3d of SETUP.md and update the `META_PAGE_ACCESS_TOKEN` secret. |
| Captions sound generic/templated | The Anthropic API hiccupped and used the simple fallback. Just edit the caption by hand, or re-run the Sunday job. |
| A whole week is blank | The Sunday job didn't run — check the Actions tab for a red run, and that your secrets are set. |

---

## The golden rules

- You **only edit** `recurring_events.csv` (when your schedule changes) and `posts.csv`
  (approvals + special events). Everything in `scripts/` runs itself.
- **Nothing posts without your `approved`.** The system never goes rogue.
- **Public repo = keep it to event stuff.** Don't put anything private in this folder.
