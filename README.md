# Backyard Brew — Weekly Social Content Workflow

Weekly Instagram + Facebook content for **Backyard Brew** (Ashwaubenon, WI).
No GitHub Actions, no API key -- ask Claude Code directly ("run sunday
social media") and get the week's captions + posting schedule in chat, plus
help editing photos on-brand.

## Start here
- **Using it week to week?** → **[HOW-TO-USE-WEEKLY.md](HOW-TO-USE-WEEKLY.md)**

## What's in here
```
photos/                 Your event photos (dropped anytime)
  _generated/           Finished flyer images (rendered on request)
assets/logo/            Your logo.png for watermarks/flyers
assets/fonts/           Brand fonts
recurring_events.csv    Your standing weekly schedule -- edit anytime
posts.csv               Special events + a saved record of past posts (optional)
scripts/                Reusable helpers Claude Code calls while doing this by hand
  config.py             Brand colors, timing, campaign rhythms
  generate_captions.py  Photo-picking + scheduling helpers (no CLI entry point)
  process_photos.py     Crop/resize/enhance + flyer builder
  classify_photos.py    Filename-convention helpers (_vibe/_spotlight tags, photo pool)
  build_preview.py      Optional HTML preview renderer
  store.py              CSV read/write helpers
status.log              Plain-English log, if you want a paper trail
CLAUDE.md               The instructions Claude Code follows for "run sunday social media"
```

## How it flows
1. **You ask** Claude Code: "run sunday social media" (or similar).
2. **Claude Code writes** the Mon-Sun captions + posting times directly in
   chat, using `recurring_events.csv`, `photos/`, and the brand voice rules
   (see `CLAUDE.md`).
3. **You** copy/paste each caption into Facebook or Instagram's own native
   scheduler yourself.
4. **Anytime**, hand Claude Code a photo and ask for an on-brand edit/flyer.

## Notes
- All drinks referenced are 100% Wisconsin-made; captions never name outside brands unless asked.
- Nothing posts automatically anywhere -- you paste every post yourself.
