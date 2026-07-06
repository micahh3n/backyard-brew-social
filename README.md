# Backyard Brew — Automated Social Posting

Automated weekly Instagram + Facebook posting for **Backyard Brew** (Ashwaubenon, WI).
Drop photos in a folder, fill a spreadsheet, approve once a week — the system writes
on-brand captions and posts them for you at optimal times, all week, hands-free.

## Start here
- **Setting it up the first time?** → **[SETUP.md](SETUP.md)**
- **Using it week to week?** → **[HOW-TO-USE-WEEKLY.md](HOW-TO-USE-WEEKLY.md)**

## What's in here
```
photos/                 Your event photos (public, so Instagram can fetch them)
  _generated/           Finished images the system renders & posts (auto)
assets/logo/            Your logo.png for watermarks/flyers
assets/fonts/           Brand fonts (auto-downloaded)
recurring_events.csv    Your standing weekly schedule — edit anytime
posts.csv               Special events + the system's weekly output you approve
scripts/                The Python that does the work
  config.py             Brand voice, colors, timing, hashtags, campaign rhythms
  generate_captions.py  Sunday job: builds the week's posts (never posts)
  process_photos.py     Crop/resize/enhance + flyer builder
  post_to_meta.py       Hourly job: posts approved content (the only publisher)
  anthropic_client.py   Caption generation (with safe fallback)
  meta_client.py        Facebook/Instagram Graph API wrapper
  store.py              CSV read/write helpers
.github/workflows/      The two scheduled jobs (Sunday + hourly)
status.log              Plain-English log of what happened
```

## How it flows
1. **Sunday job** reads your schedule + photos → generates captions & picks times →
   writes rows to `posts.csv` at `needs_review`.
2. **You** review/edit/approve in `posts.csv` (set `status = approved`).
3. **Hourly job** posts anything approved whose time has passed — Facebook feed,
   Instagram feed + Story, hashtags as the first comment, location tag — then marks it `posted`.

## Notes
- All drinks referenced are 100% Wisconsin-made; captions never name outside brands.
- Nothing posts without your approval. Failures retry automatically and are logged.
- Meta tokens last ~60 days; the log warns you before expiry.
