#!/usr/bin/env python3
"""
make-pdfs.py - Turn the playbook markdown sheets into printable PDFs.

Edit any playbook/*.md, run this, get updated PDFs in playbook/pdf/.
The markdown stays the source of truth so the sheets remain editable by
anyone with a text editor.

Usage:
    python3 playbook/make-pdfs.py
    python3 playbook/make-pdfs.py --selfcheck   # verify conversion, no render

Needs: pip install -r requirements.txt && playwright install chromium
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PLAYBOOK_DIR = Path(__file__).resolve().parent
OUT_DIR = PLAYBOOK_DIR / "pdf"

# Brand colors. Light background on purpose -- these get printed, and a navy
# page would eat a cartridge per sheet.
NAVY = "#0B1C2D"
GOLD = "#C8922A"
CREAM = "#F5EFD8"

CSS = f"""
@page {{ size: Letter; margin: 0.6in 0.65in; }}
* {{ box-sizing: border-box; }}
body {{
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 10.5pt; line-height: 1.5; color: #1a1a1a; margin: 0;
}}
h1 {{
  font-size: 22pt; color: {NAVY}; margin: 0 0 4pt; letter-spacing: -0.4pt;
  border-bottom: 3px solid {GOLD}; padding-bottom: 7pt;
}}
h2 {{
  font-size: 13.5pt; color: {NAVY}; margin: 20pt 0 6pt;
  border-left: 4px solid {GOLD}; padding-left: 8pt;
  page-break-after: avoid;
}}
h3 {{ font-size: 11.5pt; color: {NAVY}; margin: 13pt 0 4pt; page-break-after: avoid; }}
p {{ margin: 0 0 7pt; }}
ul, ol {{ margin: 0 0 8pt; padding-left: 18pt; }}
li {{ margin-bottom: 3pt; }}
strong {{ color: {NAVY}; }}
hr {{ border: 0; border-top: 1px solid #d8d8d8; margin: 16pt 0; }}
code {{
  font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 9.5pt;
  background: {CREAM}; padding: 1pt 4pt; border-radius: 3px; color: {NAVY};
}}
pre {{
  background: {NAVY}; color: {CREAM}; padding: 9pt 12pt; border-radius: 5px;
  overflow-x: auto; page-break-inside: avoid; margin: 0 0 9pt;
}}
pre code {{ background: none; color: {CREAM}; padding: 0; font-size: 10pt; }}
blockquote {{
  margin: 0 0 9pt; padding: 7pt 12pt; background: #f6f6f4;
  border-left: 3px solid {GOLD}; color: #333; font-style: italic;
}}
blockquote p {{ margin: 0; }}
blockquote p + p {{ margin-top: 7pt; }}
table {{
  width: 100%; border-collapse: collapse; margin: 0 0 11pt; font-size: 9.5pt;
  page-break-inside: avoid;
}}
th {{
  background: {NAVY}; color: {CREAM}; text-align: left; padding: 6pt 8pt;
  font-weight: 600;
}}
td {{ padding: 5pt 8pt; border-bottom: 1px solid #e2e2e2; vertical-align: top; }}
tr:nth-child(even) td {{ background: #fafaf8; }}
/* Blank fill-in cells get a visible ruled line to write on */
td:empty {{ border-bottom: 1px solid {GOLD}; min-width: 90pt; }}
.cb {{
  display: inline-block; width: 10pt; height: 10pt; border: 1.5px solid {NAVY};
  border-radius: 2px; margin-right: 6pt; vertical-align: -1pt;
}}
li.task {{ list-style: none; margin-left: -14pt; margin-bottom: 5pt; }}
.footer {{
  margin-top: 22pt; padding-top: 7pt; border-top: 1px solid #d8d8d8;
  font-size: 8pt; color: #888;
}}
"""

# `- [ ]` task items, after markdown has wrapped them in <li>
TASK_RE = re.compile(r"<li>\s*\[([ xX])\]\s*", re.I)


def md_to_html(md_text: str, title: str) -> str:
    """Convert one markdown sheet into a standalone printable HTML page."""
    import markdown as md_lib

    body = md_lib.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists"])
    body = TASK_RE.sub('<li class="task"><span class="cb"></span>', body)

    return (
        f"<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>{title}</title><style>{CSS}</style></head><body>{body}"
        f"<div class='footer'>Backyard Brew &middot; {title} &middot; "
        f"edit playbook/{title}.md and re-run make-pdfs.py</div>"
        f"</body></html>"
    )


LIST_START = re.compile(r"^\s*(?:[-*+]\s|\d+\.\s)")


def lint(md_text: str) -> list[str]:
    """Warn about a list glued to the line above it.

    Markdown silently swallows the list into the previous paragraph, which is
    the one mistake a non-markdown person makes constantly when editing these
    sheets. Cheap to detect, invisible until it prints wrong.
    """
    warnings = []
    lines = md_text.splitlines()
    for i, line in enumerate(lines[1:], start=2):
        prev = lines[i - 2]
        if LIST_START.match(line) and prev.strip() and not LIST_START.match(prev):
            # A wrapped continuation line inside a list item is fine.
            if prev.startswith(("  ", "\t")):
                continue
            warnings.append(f"  line {i}: list needs a blank line above it")
    return warnings


def _selfcheck() -> None:
    """Smallest thing that fails if the conversion breaks."""
    html = md_to_html(
        "# T\n\n- [ ] todo\n\n| a | b |\n|---|---|\n| 1 | |\n\n`code`\n", "T"
    )
    assert '<li class="task"><span class="cb"></span>todo' in html, "checkbox"
    assert "<table>" in html and "<th>a</th>" in html, "table"
    assert "<code>code</code>" in html, "inline code"
    assert "<h1>T</h1>" in html, "heading"
    assert lint("Do this:\n- a\n"), "lint should catch a glued list"
    assert not lint("Do this:\n\n- a\n- b\n"), "lint should pass a spaced list"
    assert not lint("- a\n  wrapped\n- b\n"), "lint should allow continuations"
    print("selfcheck ok")


def main() -> int:
    if "--selfcheck" in sys.argv:
        _selfcheck()
        return 0

    try:
        import markdown  # noqa: F401
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        print(f"Missing dependency: {exc.name}")
        print("Run:  pip install -r requirements.txt && playwright install chromium")
        return 1

    sheets = sorted(PLAYBOOK_DIR.glob("[0-9]-*.md"))
    if not sheets:
        print(f"No playbook sheets found in {PLAYBOOK_DIR}")
        return 1

    OUT_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for sheet in sheets:
            text = sheet.read_text(encoding="utf-8")
            for warning in lint(text):
                print(f"  ! {sheet.name}{warning}")
            html = md_to_html(text, sheet.stem)
            page.set_content(html, wait_until="load")
            out = OUT_DIR / f"{sheet.stem}.pdf"
            page.pdf(path=str(out), format="Letter", print_background=True)
            print(f"  {sheet.name}  ->  pdf/{out.name}")
        browser.close()

    print(f"\nDone. {len(sheets)} sheets in {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
