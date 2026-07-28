#!/usr/bin/env bash
#
# One-time setup for the Backyard Brew workspace.
# Works on macOS and on Windows via Git Bash.
#
#   cd ~/backyard-brew-social
#   bash setup.sh
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SRC="$REPO/.claude/skills/backyard-brew-brand"
SKILL_DEST_DIR="$HOME/.claude/skills"
SKILL_DEST="$SKILL_DEST_DIR/backyard-brew-brand"

echo "Backyard Brew setup"
echo "  repo: $REPO"
echo

# --- Python -----------------------------------------------------------------
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Python is not installed."
  echo "Install it from https://www.python.org/downloads/ and run this again."
  exit 1
fi
echo "Python: $($PY --version)"

# --- Dependencies -----------------------------------------------------------
echo
echo "Installing dependencies..."
"$PY" -m pip install --quiet --upgrade pip
"$PY" -m pip install --quiet -r "$REPO/requirements.txt"
"$PY" -m playwright install chromium
echo "Dependencies installed."

# --- Make the brand skill available from any folder -------------------------
# Claude Code picks the skill up automatically inside this repo. Linking it
# into the user skills folder means it also works from anywhere else.
echo
mkdir -p "$SKILL_DEST_DIR"

# Marks a copy this script made, so re-running can replace it instead of
# stacking up backups. Backups go OUTSIDE the skills folder -- anything left
# inside it gets loaded by Claude as a second, stale copy of the skill.
MARKER=".installed-by-backyard-brew-setup"
BACKUP_DIR="$HOME/.claude/skill-backups"

if [ -L "$SKILL_DEST" ]; then
  rm "$SKILL_DEST"
elif [ -f "$SKILL_DEST/$MARKER" ]; then
  rm -rf "$SKILL_DEST"          # our own copy from a previous run
elif [ -e "$SKILL_DEST" ]; then
  # Someone else's folder. Never delete it silently, and never leave it in
  # the skills directory where Claude would load it as a duplicate.
  mkdir -p "$BACKUP_DIR"
  BACKUP="$BACKUP_DIR/backyard-brew-brand.$(date +%Y%m%d%H%M%S)"
  mv "$SKILL_DEST" "$BACKUP"
  echo "Moved a pre-existing brand skill folder out of the way:"
  echo "  $BACKUP"
fi

# Clean up backups an older version of this script wrongly left in the skills
# folder, where they load as duplicate skills.
for stray in "$SKILL_DEST".backup.*; do
  [ -e "$stray" ] || continue
  mkdir -p "$BACKUP_DIR"
  mv "$stray" "$BACKUP_DIR/$(basename "$stray")"
  echo "Moved a stray duplicate out of the skills folder: $(basename "$stray")"
done

ln -s "$SKILL_SRC" "$SKILL_DEST" 2>/dev/null || true

# Git Bash on Windows silently copies instead of linking and still exits 0,
# so trust the filesystem rather than the exit code.
if [ -L "$SKILL_DEST" ]; then
  echo "Linked the brand skill into ~/.claude/skills/"
  echo "It updates automatically whenever you git pull."
else
  [ -e "$SKILL_DEST" ] || cp -r "$SKILL_SRC" "$SKILL_DEST"
  touch "$SKILL_DEST/$MARKER"
  echo "Copied the brand skill into ~/.claude/skills/"
  echo "This system does not support links, so it is a copy."
  echo "Re-run 'bash setup.sh' after a git pull to refresh it."
fi

# --- Verify -----------------------------------------------------------------
echo
echo "Checking..."
FAILED=0
for f in \
  "$SKILL_DEST/SKILL.md" \
  "$SKILL_DEST/references/operations-reality.md" \
  "$SKILL_DEST/references/reply-rules.md" \
  "$SKILL_DEST/references/graphics-workflow.md" \
  "$SKILL_DEST/references/growth-playbook.md" \
  "$SKILL_DEST/references/caption-voice-rules.md" \
  "$REPO/.claude/commands/sunday.md" \
  "$REPO/.claude/commands/photos.md" \
  "$REPO/.claude/commands/graphic.md" \
  "$REPO/.claude/commands/reply.md" \
  "$REPO/.claude/commands/sync.md" \
  "$REPO/.claude/commands/growth-week.md" \
; do
  if [ ! -r "$f" ]; then
    echo "  MISSING: $f"
    FAILED=1
  fi
done

"$PY" "$REPO/playbook/make-pdfs.py" --selfcheck >/dev/null && echo "  PDF builder ok"

if [ "$FAILED" -ne 0 ]; then
  echo
  echo "Something is missing. Send this output to Micah."
  exit 1
fi

echo "  brand skill ok"
echo "  6 commands ok"

cat <<'DONE'

Setup complete.

Open the Claude app, click the Code tab, choose Local, and select this
folder. Then type / to see the commands:

    /sunday        the week's posts
    /photos        name new photos for you
    /sync          share with the other computer
    /graphic       a promo image prompt
    /reply         a response to a review or comment
    /growth-week   what to work on this week

Printed sheets are in playbook/pdf/. Editable Word versions, which open in
Pages, are in playbook/editable/.

Start by reading playbook/pdf/1-START-HERE.pdf
DONE
