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

**Commit first, then pull, then push. Never stash.** Stashing looks tidy and
is the wrong tool here: if the stash succeeds but the pull fails, their work
sits in a stash they do not know exists and the tree looks empty. Committing
first means their work is safe in git before anything else happens, and the
rebase in step 3 sorts out the ordering.

### 1. See what is here

```bash
git status --short
```

### 2. Commit their work, if there is any

```bash
git add -A
git commit -m "<plain description of what actually changed>"
```

Write a real message describing what changed: `"Add 14 photos from Market &
Brews, name this week's photos"`. Never `"update"`.

**If there is nothing to commit, skip this step.** Do not create an empty
commit. Carry on to the pull, since there may still be changes to receive.

### 3. Get their changes

```bash
git pull --rebase origin main
```

### 4. Send yours

```bash
git push origin main
```

### 5. Confirm it actually landed

```bash
git status --short --branch | head -1
```

Do not report success off the back of the push command alone. Confirm the
branch is not ahead of `origin/main`, and say plainly if it still is.

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

**"Permission denied" while pulling, on a file nobody touched.** A syncing
folder (OneDrive, Dropbox, iCloud) or another program is holding the file
open. The pull usually still succeeds. Re-run `git status --short` and check
the real state rather than trusting the warning, and only raise it if
something actually failed to update.

**A leftover stash.** Older versions of this command used `git stash`. If
`git stash list` shows anything, their work may be stranded there. Compare it
against the working tree with `git stash show --name-only`, restore anything
missing, and only then drop it. Never drop a stash you have not looked at.

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
