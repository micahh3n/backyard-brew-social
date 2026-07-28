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

if [ -L "$SKILL_DEST" ]; then
  rm "$SKILL_DEST"
  echo "Replaced the old brand skill link."
elif [ -e "$SKILL_DEST" ]; then
  # A real folder is already there. Never delete it silently.
  BACKUP="$SKILL_DEST.backup.$(date +%Y%m%d%H%M%S)"
  mv "$SKILL_DEST" "$BACKUP"
  echo "Found an existing brand skill folder. Moved it to:"
  echo "  $BACKUP"
fi

ln -s "$SKILL_SRC" "$SKILL_DEST" 2>/dev/null || true

# Git Bash on Windows silently copies instead of linking and still exits 0,
# so trust the filesystem rather than the exit code.
if [ -L "$SKILL_DEST" ]; then
  echo "Linked the brand skill into ~/.claude/skills/"
  echo "It updates automatically whenever you git pull."
else
  [ -e "$SKILL_DEST" ] || cp -r "$SKILL_SRC" "$SKILL_DEST"
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
  "$REPO/.claude/commands/graphic.md" \
  "$REPO/.claude/commands/reply.md" \
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
echo "  4 commands ok"

cat <<'DONE'

Setup complete.

Start Claude Code:

    cd ~/backyard-brew-social
    claude

Then type / to see the commands:

    /sunday        the week's posts
    /graphic       a promo image prompt
    /reply         a response to a review or comment
    /growth-week   what to work on this week

Printed sheets are in playbook/. To rebuild the PDFs after editing one:

    python3 playbook/make-pdfs.py

Start with playbook/1-START-HERE.md
DONE
