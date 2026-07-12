## Sunday Social Media

No GitHub Actions, no Anthropic API key -- this all runs through Claude Code
directly now. When Micah says something like **"run sunday social media"**
(or similar -- "generate this week's posts", "do sunday"), do this in the
chat, right then:

1. Read `recurring_events.csv` for the six recurring events (Mon-Sat) and
   check `photos/` for anything new dropped in since last time, plus
   `posts.csv` for any pending one-off/special-event rows.
2. Consult the `backyard-brew-brand` skill for voice, colors, and messaging
   rules -- write every caption yourself in that voice. Don't reuse the same
   opening/CTA/hook two posts in a row; check `posts.csv`'s recent rows for
   what was said last time.
3. For each of Mon-Sun, decide the photo: an exact `{date}_{keyword}` dated
   match first, then `scripts/generate_captions.py`'s `find_photo()` /
   `find_food_photo()` (the undated event/food photo pool, LRU-rotated --
   call these via a quick `python -c` from `scripts/`, don't reinvent the
   rotation by eye), then the recurring event's static default photo.
   Sunday itself has no recurring event -- use a `_vibe`/`_spotlight`-tagged
   photo or whatever's on-brand and available that week.
4. Give Micah both captions (FB + IG) and a suggested post time for every
   day, Mon-Sun, directly in chat. Offer to write it into `posts.csv` too if
   he wants a saved record, but the chat answer is the deliverable.
5. Anytime he hands you a photo to edit, keep it on-brand: colors/fonts from
   `scripts/config.py`'s `COLORS`, the existing flyer look in
   `scripts/flyer_render.py`/`scripts/process_photos.py` (reuse that
   pipeline for a finished flyer; for a quick edit, just match the palette).

`scripts/generate_captions.py` and `scripts/classify_photos.py` are now pure
helper libraries (photo/schedule logic only, no API calls) -- there's no
`main()`/CLI entry point anymore. Nothing in `scripts/` auto-runs; you do
this by hand each time you're asked.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
