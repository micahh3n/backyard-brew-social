# Backyard Brew

Everything for the bar's social media and online presence.

**The owner works in the Claude desktop app (Code tab) on a Mac, not the
terminal.** Never answer with "open Terminal and run X." If something needs a
command, run it yourself and report what happened. He is not a developer and
should never have to be.

## Read the brand skill first

`.claude/skills/backyard-brew-brand/` is the whole brain: voice, colors,
fonts, hours, events, how the business actually operates, how it grows, and
how it replies to people. **Load it before writing anything customer-facing or
answering any question about the bar.**

Its `SKILL.md` opens with a table routing each kind of task to the right
reference file. Use that table rather than guessing which file to open.

Two that matter most and get skipped most:

- `references/operations-reality.md` — which days underperform, who works
  there, what the owner wants, what constraints an idea has to survive.
  **Required before recommending any action, event, or priority.**
- `references/reply-rules.md` — required before replying to any review,
  comment, or message.

## The six commands

| Command | Does |
|---|---|
| `/sunday` | The week's 21 static posts plus a Google Business Profile post |
| `/photos` | Looks at unnamed photos and renames them to the convention |
| `/graphic` | Writes a Gemini Image prompt, then the captions |
| `/reply` | Turns a review or comment into a professional response |
| `/sync` | Pulls and pushes so both computers match |
| `/growth-week` | Reviews the week, returns a ranked action list |

Plain English works too. The commands just make it repeatable.

## Folder layout: keep the top level simple

The owner opens this folder in Finder and is not technical. The top level
holds **only** what a person opens. Never add loose files or new folders up
there. Anything Claude needs goes inside `Claude Files - Do Not Touch/`.

| Folder | What goes in it |
|---|---|
| `0 START HERE.pdf` | The map. Generated from `playbook/1-START-HERE.md` |
| `1 Vendor Market/` | `Sign-In Sheet.pdf` / `.docx`, `Vendor Signups.xlsx`, `Message Templates.docx`, `Vendor Map`. Before replacing the sign-in sheet, copy the current one to `Old Versions/Sign-In Sheet YYYY-MM-DD.docx` (and `.pdf`) |
| `2 Posters and Flyers/` | One folder per event holding only the finished PNGs, `Social Graphics/`, `Order Slips.pdf` |
| `3 Photos/` | Every photo. `/photos` names them here |
| `4 Logo/` | Logo files |
| `5 How-To Guides/` | Sheets 2-4 as PDFs |
| `Pickleball.html` | Stays loose at the top on purpose |
| `Claude Files - Do Not Touch/` | Everything else (below) |

Paths in this repo contain spaces, so always quote them in shell commands.

## The printed sheets

`Claude Files - Do Not Touch/playbook/` holds the human-facing versions of
these same processes, written for someone with no Claude experience. Markdown
is the source of truth; `python3 "Claude Files - Do Not Touch/playbook/make-pdfs.py"`
writes `0 START HERE.pdf` and `5 How-To Guides/`.

**When a process changes, update both** the relevant skill reference and the
matching playbook sheet. They describe the same work from two sides.

## Data files (all inside `Claude Files - Do Not Touch/`)

- `recurring_events.csv`: the six recurring weekly events. Source of truth
  for times and details
- `posts.csv`: one-off and special events
- `3 Photos/` (top level): `{date}_{keyword}` for dated events, bare keyword
  for the rotation pool, `_vibe` / `_spotlight` for candids
- `4 Logo/` (top level) and `fonts/`: real logo and brand fonts
- `poster-work/<slug>/`: poster working files; finished PNGs go to
  `2 Posters and Flyers/`
- `scripts/config.py`: paths and brand facts in code form. **If a brand fact
  changes, update both `config.py` and the skill**, since both get read

## Scripts

`generate_captions.py` and `classify_photos.py` are helper libraries for photo
and schedule logic. No CLI, no API calls, nothing auto-runs.

`flyer_render.py` builds brand-exact flyers in HTML/CSS via Playwright. This
is the fallback when Gemini cannot render text correctly. Setup:
`bash "Claude Files - Do Not Touch/setup.sh"`.

## Other skills worth reaching for

Beyond `backyard-brew-brand`, these live in `.claude/skills/` in this repo — they sync with everything else (git or however this folder gets shared), so they're available on any machine with this repo, no separate plugin install needed. Don't limit yourself to just this list, but these are the easy-to-miss ones:

- `google-fonts` — if a flyer or graphic ever needs a font pairing decision, use this instead of guessing.
- `power-design` — if a one-off deck or full page (not a social graphic) is ever needed for the bar, this extracts brand DNA and applies real design principles instead of a generic template.
- `algorithmic-art` — generative textures/backgrounds, if a graphic ever wants something beyond a photo (e.g. an abstract disc-golf-themed pattern).
- `self-healing` — if the same correction keeps coming up across sessions, this is how to turn it into a permanent fix instead of relearning it each time.

## Nothing posts automatically

Claude writes, a person posts. There is no Meta API, no scheduled job, and no
API key anywhere in this repo.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
