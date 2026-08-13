# Backyard Market & Brews (Sunday)

Sunday's headline event. Read this before writing any Backyard Market & Brews caption — it has
its own messaging guardrails that don't apply to the rest of the weekly calendar.

**Extremely community and local-business focused, above everything else (Micah's call,
2026-07-26).** This is a small-business showcase, not a party — the vendors and the musician are
the whole point. Center real local people and their businesses, not "stuff to look at" or generic
bar-event energy.

**Moved from Thursday to Sunday starting 2026-08-30 (Micah's call, 2026-08-12)** — Thursday's
4pm-dusk window stopped working as days got dark too early for an evening market. The last
Thursday occurrence, 2026-08-27, ran as a one-off themed special, "Moonlight Market" (full moon,
vendors bring lights, hiking trails open to all attendees that night) — see `posts.csv` for that
post. It's the same market on a themed night, not a new or separate recurring event; don't confuse
it with a monthly thing. Thursday currently has no weekly event. There's a possible future move
back to Thursday, indoors, once it gets too cold to run the market outside — **not decided, no
details yet, backburner only.** Don't invent specifics for it.

## What it is

A weekly vendor market held every Sunday at Backyard Brew, 3640 Sand Acres Dr, Ashwaubenon, WI.
Local makers, artisans, and small businesses set up booths in the yard while guests shop, drink,
and listen to live music.

## Schedule

- Recurring every Sunday, rain or shine
- **Market runs noon-4pm.** Live music plays within that window, a different local musician/act
  each week. Vendor/staff setup is 9am-11:45am.
- **Seasonal (Sept-Jan): also Sunday football.** The game plays during the market — backyard
  tailgate framing, not sports-bar framing (a round on the course before kickoff, the game
  outside, Wisconsin taps, tailgate food; Packers references welcome). Kickoff time is NEVER
  fixed — it changes weekly with the NFL schedule. Never guess it or reuse last week's; confirm
  that week's real time with the owner before naming one in a post. If unconfirmed, write around
  "gameday"/"kickoff" with no specific time rather than inventing one. Outside Sept-Jan, none of
  this football framing applies — it's market-only.
- Disc Golf League runs separately, Thursday afternoons — unrelated to this event now that they
  no longer share a day.

## What happens

- Local vendors set up booths selling handmade goods, art, and other small-business products
- Guests browse the market, buy Wisconsin craft beer from the bar, and can eat while they shop
- Live, local music plays as the backdrop for the evening
- Vendor lineup rotates — not always the same vendors week to week, so there's variety even for
  repeat visitors

## Vendor standards (screening criteria)

- Vendors must have an established online presence (Facebook, Instagram, Etsy, etc.) with an
  existing following
- Not open to private sellers or word-of-mouth-only vendors
- Vendor inquiries: DM the bar's social accounts or email crew@backyard-brew.com

## Musician standards

- Local musicians/performers only
- Inquiries: DM or email crew@backyard-brew.com (same contact as vendors)

## Messaging & tone guidelines

- **Community and local business come first, in every caption.** Name the fact that these are
  real neighbors running real small businesses — that's the hook, not "cool stuff to buy" or
  generic market/party energy.
- **FOMO-driven:** emphasize that the lineup (both vendors and music) changes weekly, so missing
  a Sunday means missing something you won't see again this exact way.
- Casual, community-first, never corporate.
- **Do NOT imply vendors never repeat** — frame it as "you never know who'll be out," never
  "gone forever" in a way that contradicts the fact that vendors do come back.
- Encourage engagement: ask followers to tag friends who sell things, tag vendors they want to
  see back.
- **Standard CTAs:** vendor sign-up (email/DM), musician sign-up (email/DM), "bring cash, bring
  friends, bring the leashed pup."
- **"Rain or shine" is a fact for the schedule, not a required line (Micah's call, 2026-07-29).**
  Use it when weather is genuinely a question that week (the forecast is bad, or someone asked)
  and leave it out otherwise. It got into nearly every draft of a multi-post batch purely because
  it reads like a standard event detail, and the repetition went stale fast. The same caution
  applies to the other always-true details here: "noon-4pm" and "30+ vendors" are true every
  single week, which makes them repetition risks across a batch rather than lines every post owes.
- **Avoid:** "Sundays are for the backyard," "See you in the backyard," overly polished/ad-like
  language, plugging disc golf/hiking/pickleball as part of THIS event's core pitch (those are
  separate draws — don't dilute the market/music FOMO angle with them).
- **Do NOT mention taco night** as tied to this event unless separately reconfirmed — it hasn't
  been reconfirmed as still running alongside the market.
- **Never mention breakfast** — breakfast service was discontinued entirely (2026-07-26), across
  every day of the week, not just Sunday.
- **Don't default to "the yard" as the go-to word for the market space** (Micah's call,
  2026-07-26) — it reads flat and repeats fast across three posts in one week. Vary it: tents,
  booths, vendor tables, "every booth," the specific sensory detail, or just skip naming the
  space at all and describe what's happening instead. "35 acres" is the brand's own established
  term for the property elsewhere — fine to borrow occasionally, but don't lean on any single
  noun every time either.
- **Lean more interactive than the rest of the week's calendar, not less** (Micah's call,
  2026-07-26) — community engagement IS the point of this event, so most Market & Brews posts
  (not just the ~1/3 weekly quota from `caption-voice-rules.md`) should invite a real reaction:
  comment what they're hoping to find, tag a vendor-friend, name a favorite booth. This is a
  deliberate exception to the general hook ratio, scoped to this event specifically.

## Contact

Vendor and musician inquiries both go to **crew@backyard-brew.com** (or DM the bar's socials).

## Photo situation (open gap as of 2026-07-26)

Two existing files in `photos/` are Market & Brews graphics, but **both are stale, one-off dated
promos, not reusable defaults**:
- `market&brews_art.PNG` — generic "Shop Local. Eat Local. Drink Local." poster, but hardcodes
  "Thursday, July 23" in the design.
- `Backyard Market & Brews PROMO.png` — hardcodes both "Thursday, July 23" AND that week's
  musician's name ("Live Music by Josh Berton").

`recurring_events.csv`'s Sunday row points `default_photos` at `marketbrews_default_art.jpg`,
which **does not exist yet**. Because the vendor lineup and musician change weekly, a single
static default may never really fit this event the way it does for Bingo/Pickleball/etc. Two
options for Micah to choose between later:
1. Drop a fresh dated graphic each week (e.g. `{date}_market.png`) with that week's musician's
   name baked in, matching the existing dated-photo-match convention in `find_photo()`.
2. Supply one evergreen, undated candid (vendor tents, market crowd, no date/name text) as the
   `marketbrews_default_art.jpg` fallback for weeks nothing else is dropped in.

**Decided 2026-07-26: text-only for now.** Post the Market & Brews "today" caption with no
dedicated photo until Micah supplies one — don't force an unrelated photo onto it. A generic
bar/patio candid is an acceptable placeholder on secondary filler/teaser posts about this event
only (not the headline post itself). Revisit if Micah starts dropping weekly graphics or an
evergreen shot.
