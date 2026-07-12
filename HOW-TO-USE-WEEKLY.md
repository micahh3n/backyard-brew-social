# How To Use This Every Week

No GitHub Actions, no API key -- you drop photos in whenever, and when you
want the week's posts, you just ask Claude Code.

---

## During the week

**Drop in photos** (optional but recommended)
Naming them well means Claude Code (or you) doesn't have to guess what a
photo is.

*Tied to a specific night's event:* name it `{date}_{event keyword}[.jpg/.png]`:

| You drop this | What it does |
|---|---|
| `2026-07-13_bingo.jpg` | Fresh photo for Monday's Bingo post |
| `2026-07-13_bingo_teaser.jpg` | Different photo for the night-before teaser |
| `2026-07-13_bingo_deal.jpg` | A photo of that day's featured drink deal — gets composited into a small callout badge on the flyer |
| `2026-07-13_bingo_art.png` | A finished graphic you made — posted exactly as-is, no editing |
| *(nothing)* | Falls back to the default photo — still works |

The event keywords:

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

*Have a photo but don't know which specific date it'll get used on?* Just
include the event keyword in the filename with **no date at all** (e.g.
`party_bingo.jpg`). It automatically enters that event's rotation pool and
gets used on some future week whenever there's no exact dated match to
prefer. A photo is never permanently used up: it just avoids repeating
back-to-back, picking whichever eligible photo hasn't been used the longest.

**Food photos** ride along as a second photo on the day that food is
actually served, without replacing the event's own photo:

| Keyword | Attaches to |
|---|---|
| `hotdog` | Monday (Bingo) and Tuesday (Pickleball) |
| `taco`, `nachos`, `quesadilla` | Wednesday (Tacos + Poker Club) |
| `breakfastburrito` | Saturday (Pool Night) |
| `pizza` | Any day -- pizza's on the menu every day, so it only actually shows up on one rotating day per week rather than every single post |

*Not tied to a specific dated event* (a candid shot, a vibe/atmosphere photo,
a shoutout-worthy moment): tag it and Claude Code will use it directly, no
guessing needed:

| You drop this | What it does |
|---|---|
| `campfire_vibe.jpg` | A "behind the scenes"-style candid post |
| `regular_winning_spotlight.jpg` | A community shoutout post |
| *(no tag)* | Ask Claude Code to look at it directly and decide |

**Add any special events** (only if you have one)
Open `posts.csv` and add ONE row for a party/guest/holiday. Fill in: `date`,
`photos`, `event`, `key_details`, `platforms`. Leave the rest blank.

---

## Sunday (or whenever): ask for it

Just say something like **"run sunday social media"** to Claude Code. It
will:
1. Read `recurring_events.csv`, `posts.csv`, and `photos/` for the week.
2. Write Facebook + Instagram captions for Mon-Sun in Backyard Brew's voice.
3. Propose a posting time for each.
4. Hand you all of it directly in chat.

Then you copy/paste each caption into Facebook or Instagram's own
**"Schedule Post"** feature yourself, attaching the photo it points you to.

**Anytime** -- not just Sunday -- hand Claude Code a photo and ask for an
on-brand edit or flyer; it'll keep the colors/fonts consistent with
everything else.

---

## The golden rules

- You **only edit** `recurring_events.csv` (when your schedule changes) and
  `posts.csv` (special events, or if you want a saved record of what ran).
- **Nothing posts automatically anywhere.** You paste every post yourself.
- There is **no GitHub Actions, no Meta/Facebook developer setup, no API
  key** anywhere in this anymore.
