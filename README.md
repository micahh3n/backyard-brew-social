# Backyard Brew — Weekly Social Content Workflow

Weekly Instagram + Facebook content generation for **Backyard Brew** (Ashwaubenon, WI).
Drop photos in a folder, let the system write captions and render flyers every Sunday,
then manually schedule each post to Facebook and Instagram yourself — complete control,
zero code, ~1 hour per week.

## Start here
- **Setting it up the first time?** → **[SETUP.md](SETUP.md)**
- **Using it week to week?** → **[HOW-TO-USE-WEEKLY.md](HOW-TO-USE-WEEKLY.md)**

## What's in here
```
photos/                 Your event photos (dropped during the week)
  _generated/           Finished flyer images the system renders on Sunday
assets/logo/            Your logo.png for watermarks/flyers
assets/fonts/           Brand fonts (auto-downloaded)
recurring_events.csv    Your standing weekly schedule — edit anytime
posts.csv               Special events + the system's weekly output (you mark as scheduled)
preview/                Generated HTML preview of the week's posts
  this-week.html        Visual card review of every post (double-click to open)
scripts/                The Python that does the work
  config.py             Brand voice, colors, timing, hashtags, campaign rhythms
  generate_captions.py  Sunday job: builds the week's posts + images + preview
  process_photos.py     Crop/resize/enhance + flyer builder (template variety + deal compositing)
  scheduling.py         Computes guaranteed 2-3 posts/day cadence across the week
  weather.py            Optional: pulls weather data for weather-tied posts
  build_preview.py      Renders the HTML preview page (preview/this-week.html)
  anthropic_client.py   Anthropic API wrapper for caption generation (with safe fallback)
  classify_photos.py    Photo classification helper for template selection
  store.py              CSV read/write helpers
.github/workflows/      Sunday job only (generates captions + images + preview)
status.log              Plain-English log of what happened
```

## How it flows
1. **Sunday job** reads your schedule + photos → generates captions, flyer images,
   computes posting times (2-3 posts/day), and creates a visual preview → writes rows
   to `posts.csv` at `needs_review` status.
2. **You** review the preview page (`preview/this-week.html`), optionally edit captions/times
   in `posts.csv`.
3. **You** manually schedule each post to Facebook or Instagram's own native scheduler
   (paste caption + attach image + set the suggested date/time).
4. **You** mark each row `status = scheduled` and push to GitHub (for your own tracking).

## Notes
- All drinks referenced are 100% Wisconsin-made; captions never name outside brands.
- Nothing posts without you manually scheduling it — you are always in control.
- The Sunday job logs everything in `status.log` — check it if you notice something unexpected.
