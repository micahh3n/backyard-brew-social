---
description: Look at the new photos and name them correctly, so nobody has to do it by hand
argument-hint: [optional: how many to do, e.g. "20"]
---

Name the unnamed photos in `photos/` by actually looking at them. $ARGUMENTS

Nobody should have to label photos by hand. He drops them in straight off his
phone with names like `IMG_4471.HEIC`, and this turns them into names the rest
of the system understands.

## Find what needs naming

```bash
cd scripts && python -c "
import os, config, classify_photos as c
files = sorted(f for f in os.listdir(config.PHOTOS_DIR)
               if not f.startswith('_') and c.needs_classification(f))
print(len(files)); print('\n'.join(files))
"
```

`needs_classification()` already skips anything correctly named, anything with
a `_vibe` / `_spotlight` / `_art` / `_teaser` / `_deal` tag, and anything that
already carries an event or food keyword. Never rename those.

**Work in batches of about 20.** There is a large backlog, and reading a
hundred images at once is slow and burns context. Do 20, finish them, then ask
whether to continue. If he gave a number in the arguments, use that instead.

## Look at each one

Actually open each image with the Read tool. Do not guess from the filename,
which is the whole point of this command.

For the date, use the photo's own capture time rather than today:

```bash
cd scripts && python -c "
import config, classify_photos as c, os
p = os.path.join(config.PHOTOS_DIR, 'IMG_4471.HEIC')
print(c.read_capture_time(p))
"
```

## Decide the name

Pick the pattern that fits what is actually in the frame.

| What you see | Name it | Example |
|---|---|---|
| A specific event, clearly identifiable | `{date}_{keyword}` | `2026-09-14_bingo.jpg` |
| An event, but no idea which date it belongs to | `{something}_{keyword}` | `crowd_bingo.jpg` |
| Food | `{food keyword}` in the name | `tacos_fresh.jpg` |
| Atmosphere, candid, the property, people hanging out | `{word}_vibe` | `campfire_vibe.jpg` |
| A winner, a regular, a moment worth shouting out | `{word}_spotlight` | `bingo_winner_spotlight.jpg` |
| A finished poster or flyer with text already on it | `{date}_{keyword}_art` | `2026-09-14_bingo_art.png` |

Event keywords: `bingo` (Mon), `pickleball` (Tue), `poker` (Wed), `market` /
`vendor` / `marketbrews` (Thu), `karaoke` (Fri), `pool` (Sat).

Food keywords: `hotdog`, `taco`, `nachos`, `quesadilla`, `pizza`.

**A dated name means "use this on that specific date."** Only use one when the
photo is clearly from, or clearly for, that day's event. When in doubt use the
undated form, which puts it in the rotation pool for future weeks. The
undated form is the safer default.

**Keep the file extension exactly as it was.** Do not convert HEIC to JPG here.

### Judgment calls

- **Blurry, dark, duplicate, or just bad?** Do not rename it. List it at the
  end under "skipped, not worth posting" and say why in three words.
- **Cannot tell what event it is?** Treat it as a `_vibe` photo. A good candid
  is more useful than a wrongly-labeled event photo.
- **Near-duplicates from a burst?** Name the best one and skip the rest. Say
  how many you skipped.
- **Anyone in the frame who looks unhappy to be photographed, or any shot that
  would embarrass a customer?** Skip it and say so.

## Show the plan before touching anything

Print a table: current name, new name, one short line on what is in the photo.
Group by type so it scans quickly.

**Wait for approval before renaming.** He may want to change some.

## Then rename

Use `git mv` rather than plain `mv`, so the change is tracked and can be
undone:

```bash
git mv "photos/IMG_4471.HEIC" "photos/2026-09-14_bingo.HEIC"
```

Never overwrite an existing file. If the target name is taken, add a short
distinguishing word rather than a number: `bingo_crowd_vibe.jpg`, not
`bingo_vibe_2.jpg`.

## Finish

Say how many were renamed, how many were skipped and why, and how many are
still waiting. Then remind him the changes are local until he saves and
shares them (`/sync`).
