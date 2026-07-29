# Backyard Brew — Social Media & Online Presence

Everything for the bar's Instagram, Facebook, Google Business Profile, and
growth. Ashwaubenon, WI.

Claude Code does the writing. A person does the posting. Nothing goes out
automatically.

---

## Using it (no terminal needed)

Open the **Claude app** → **Code** tab → **Local** → **Select folder** → pick
this folder. Type `/` and the commands appear.

The brand skill in `.claude/skills/` and the commands in `.claude/commands/`
load automatically when this folder is open. Nothing to install for that.

### Setup (run this)

```bash
bash setup.sh
```

Strongly recommended. Installs pillow-heif (without it nothing can read the
iPhone HEIC photos `/photos` has to look at), the PDF and Word builder, and
the local flyer renderer. Re-run it after a `git pull`.

You can also just ask Claude in the app: *"run bash setup.sh"*.

## Then read this

**[playbook/1-START-HERE.md](playbook/1-START-HERE.md)**

Four printable sheets, written for someone who has never used Claude Code:

| Sheet | For |
|---|---|
| [1-START-HERE](playbook/1-START-HERE.md) | What everything is and how to open it |
| [2-MAKE-A-GRAPHIC](playbook/2-MAKE-A-GRAPHIC.md) | Making a poster or promo image |
| [3-EVERY-DAY](playbook/3-EVERY-DAY.md) | Stories, Facebook groups, comments |
| [4-EVERY-WEEK](playbook/4-EVERY-WEEK.md) | Sunday. The whole week's posts |

Print them from `playbook/pdf/`. Edit the `.md` files anytime, then ask Claude
to *"rebuild the playbook PDFs"* (or run `python3 playbook/make-pdfs.py`).

---

## The six commands

Open this folder in the Claude app (Code tab), then type `/`:

| Command | Does |
|---|---|
| `/sunday` | The week's 21 static posts plus a Google Business Profile post |
| `/photos` | Looks at your unnamed photos and names them for you |
| `/graphic` | Writes a Gemini Image prompt, then the captions |
| `/reply` | Turns a review or comment into a professional response |
| `/sync` | Gets the other computer's changes and sends yours |
| `/growth-week` | Reviews the week, hands back a ranked action list |

Handing this over to someone? See **[HANDOFF.md](HANDOFF.md)**.

Plain English works too. Claude already knows the hours, events, prices,
voice, which nights are slow, and what the goals are.

---

## What's in here

```
playbook/               The four printable sheets, plus the PDF builder
.claude/skills/         The brand brain: voice, facts, operations, growth, replies
.claude/commands/       The six commands above
photos/                 Photos for posts. Drop them in anytime
  _generated/           Finished flyers rendered locally
assets/logo/            The real logo
assets/fonts/           Brand fonts
recurring_events.csv    The weekly schedule. Edit when events change
posts.csv               One-off and special events
scripts/                Photo, scheduling, and flyer-rendering helpers
  config.py             Brand facts in code. Update alongside the skill
  flyer_render.py       Brand-exact flyers via HTML/CSS, the no-AI fallback
CLAUDE.md               How Claude works in this repo
```

### Naming photos

| Name it | What happens |
|---|---|
| `2026-09-14_bingo.jpg` | Used for that date's Bingo post |
| `2026-09-14_bingo_teaser.jpg` | Used for the night-before teaser |
| `2026-09-14_bingo_art.png` | A finished graphic. Posted exactly as-is |
| `crowd_bingo.jpg` | Joins the Bingo rotation for future weeks |
| `campfire_vibe.jpg` | A candid, used for filler posts |
| `regular_winning_spotlight.jpg` | A community shoutout post |

Keywords: `bingo`, `pickleball`, `poker`, `market`, `karaoke`, `pool`. Food
photos ride along as a second photo: `hotdog`, `taco`, `nachos`,
`quesadilla`, `pizza`.

The full mapping lives in `scripts/config.py`.

---

## The rules

1. **Nothing posts automatically.** No API keys, no scheduled jobs, no Meta
   integration. Claude writes, you post.
2. **Wisconsin only.** Never mention a beer, brand, or product not made in
   Wisconsin.
3. **Look at it before you post it.** Spelling, distortion, whether it sounds
   like us.
