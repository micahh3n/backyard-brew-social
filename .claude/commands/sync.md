---
description: Get the latest changes and share yours, so both computers stay matched up
---

Sync this folder with GitHub so the bar's computer and Micah's computer stay
matched: photos, schedule changes, playbook edits, everything.

**The person running this is not a developer.** Never show them raw git
output, never mention branches, staging, or remotes, and never leave them at a
prompt to resolve something. Do the work, then say what happened in plain
English.

## Do it in this order

### 1. See what is here

```bash
git status --short
```

### 2. Get their changes first

```bash
git stash push -u -m "sync-temp" 2>/dev/null; git pull --rebase origin main
```

Pulling before pushing avoids the most common failure. If nothing was stashed,
the stash command does nothing and that is fine.

### 3. Put local changes back

```bash
git stash pop 2>/dev/null || true
```

### 4. Save and share

```bash
git add -A
git commit -m "<plain description of what actually changed>"
git push origin main
```

Write a real commit message describing what changed: `"Add 14 photos from
Market & Brews, name this week's photos"`. Never `"update"`.

**If there is nothing to commit, say so and stop.** Do not create an empty
commit.

## When something goes wrong

**A merge conflict.** Do not hand it to them. Look at the conflicting file and
resolve it yourself:

- `posts.csv` or `recurring_events.csv`: keep both sides' rows, drop exact
  duplicates, keep the row order sensible.
- `status.log`: keep both sides, it is an append-only log.
- A playbook sheet or a skill file: read both versions and merge the intent.
  If both people genuinely changed the same sentence differently, keep the
  newer one and tell him what you overrode.

Then finish the sync. Only stop and ask if resolving it would lose real work.

**Not a git repository, or no remote.** The folder was probably downloaded as
a ZIP instead of cloned. Say that plainly and offer to reconnect it to
`https://github.com/micahh3n/backyard-brew-social`.

**Push rejected.** Pull again and retry once. If it still fails, explain in one
sentence and stop.

**Authentication failure.** He needs to sign in to GitHub. Do not try to work
around it, and never ask him to paste a token or password into the chat.

## Finish

Report in plain English:

- What came down from Micah, if anything (new photos, schedule changes)
- What went up from here
- Anything skipped or overridden, and why

Example:

> Got 3 new photos from Micah and an updated Thursday event time. Sent up your
> 14 new photos and the Facebook groups you added to the daily sheet. Both
> computers match now.
