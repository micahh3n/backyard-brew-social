---
description: Write the whole week's social posts (21 captions) ready to schedule in Meta Business Suite
---

Write a full week of Backyard Brew social posts, delivered in chat, ready to
copy into Meta Business Suite.

## Before writing anything

1. Read the `backyard-brew-brand` skill, including
   `references/caption-voice-rules.md`. Every voice rule, the weekly hook and
   membership ratios, the anti-slop pass, and the Facebook vs Instagram
   difference all live there. Follow them exactly.
2. Read `recurring_events.csv` for the six recurring events, Monday through
   Saturday.
3. Read `posts.csv` for any one-off or special events, and to see what was
   said recently so nothing repeats.
4. Look in `photos/` for anything new dropped in since last time.

Ask which week this is for if it is not obvious. Default to the upcoming
Monday through Sunday.

## The schedule: 3 posts a day, every day, all seven days

21 posts total. Fixed slots at **11:00am, 2:30pm, and 7:00pm**, every day,
including days with no recurring event.

### 11:00am: the day's main post
The recurring event if there is one. Sunday has none, so use a vibe,
spotlight, or feature post.

**Write in anticipation, never as if the event is already happening.** 11am is
hours before anything starts. Bingo is at 6:30pm. Market & Brews starts at
4pm. "Tonight," "this afternoon," and "starting at 6:30" are correct. "The
tents are up" and "the music is playing" are wrong.

### 2:30pm: highlight, recap, or filler
A **different photo and a different angle** than the 11am post. Food
spotlight, a `_vibe` or `_spotlight` candid, a winner shoutout, the tap wall.
Never the same photo as that morning's post.

**The same tense rule applies Monday through Friday**, because the property
does not open until 4pm those days. At 2:30pm on a Tuesday nothing is open, so
nothing can be described as underway. Only Saturday and Sunday, which both
open at 11am, can describe the place as already active in this slot.

### 7:00pm: teaser for tomorrow
Posted today, previewing the next calendar day. If tomorrow has no event
(Saturday previewing Sunday), use a close-out or vibe post instead.

**Teasers get heavier FOMO** than the other two slots. There is nothing to act
on yet, so lean into scarcity and anticipation. Today and filler posts should
instead push interaction and walking in the door: concrete hooks, not urgency
for its own sake.

## Picking photos

For each slot, in order:
1. An exact `{date}_{keyword}` dated match
2. `scripts/generate_captions.py`'s `find_photo()` / `find_food_photo()` for
   the undated rotation pool. Call these with a quick `python -c` from
   `scripts/` rather than eyeballing the rotation
3. The recurring event's default photo from `recurring_events.csv`

For the 2:30pm slot also check for unused `_vibe` and `_spotlight` photos via
`_pick_pool_photo`. **Open and actually look at any `_spotlight` photo before
writing its caption.** The tag does not tell you what is in the frame, and a
winner shot needs different copy than a drink feature.

Reusing a photo across days is fine and expected. Reusing one twice in the
same day is not.

**A finished graphic the owner drops in** (a poster with the details already
on it, not a candid) posts as-is with no editing. If it is for an event not in
either CSV, use the details printed on the graphic and mention that it may
need a permanent row added.

## Before delivering: run the tally

`caption-voice-rules.md` sets ratios across the whole 21-post batch, not per
post. Count them before delivering and adjust:

- Interactive hooks: about 7 of 21, spread across different days and slots
- Membership mentions: about 7 of 21, alternating Beer Club and Course
  Membership
- Food mentions: most days, not only Wednesday
- Every post: a concrete same-day reason to physically show up

Then run the anti-slop pass from that same file. No em dashes anywhere. No
phrase reused across the batch, not just across adjacent posts. Facebook and
Instagram taking genuinely different angles rather than being reworded copies.

## Deliver

Give all 21 posts in chat, grouped by day, each with:
- Date, day, and time slot
- The photo filename to attach
- The Facebook caption
- The Instagram caption
- The Instagram hashtags, marked as a first comment

**The chat answer is the deliverable. Do not write to `posts.csv` and do not
offer to.** He copies straight from chat into Meta Business Suite.
