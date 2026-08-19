# Installing this skill

This folder is a Claude Code **skill**. Once it's in the right place, Claude
picks it up automatically — you just ask for a poster in plain English.

## Already have the repo?

If you've cloned `backyard-brew-social`, the skill is already active for any
Claude session started **inside that folder** — project skills load from
`.claude/skills/`. Nothing to install.

## To use it everywhere, not just in that folder

Copy the folder into your personal skills directory:

**Windows**

```bash
cp -r "path/to/backyard-brew-social/.claude/skills/backyard-brew-posters" "$HOME/.claude/skills/"
```

**Mac**

```bash
cp -R "path/to/backyard-brew-social/.claude/skills/backyard-brew-posters" ~/.claude/skills/
```

Restart Claude Code and it's live.

## What it needs on your machine

- **Google Chrome** — used headlessly to render the finished PNGs. Nothing
  opens on screen.
- **Python with Pillow** — `pip install Pillow`. Only used for cropping photos.
- **The photo library** — `photos/` in the `backyard-brew-social` repo. Without
  it Claude has nothing real to build on and will ask you for a picture.

Fonts are bundled in `assets/fonts/` — nothing to install.

## Using it

Just ask:

> make me a poster for karaoke night

> new poster for the Sunday market, push the live music angle

> redo the bingo poster with a different photo

Claude reads the event facts from the `backyard-brew-brand` skill, picks a
photo, picks a display font, builds it, and hands back an editable design link
plus finished PNGs — an 18×24 for printing and a 4:5 for Instagram and
Facebook.

## Keeping it current

The copy inside `backyard-brew-social` is the source of truth. When Micah
updates it and pushes, `git pull` and re-copy if you installed it to your
personal skills folder.

If Claude gets a poster wrong for you, tell it what you wanted instead and ask
it to record that in `references/likes-dislikes.md`. That file is the whole
reason the skill gets posters right the first time — it only stays useful if
corrections go into it.
