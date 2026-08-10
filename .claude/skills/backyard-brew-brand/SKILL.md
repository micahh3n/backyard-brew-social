---
name: backyard-brew-brand
description: Everything Claude needs to work for Backyard Brew, the disc golf + hiking + craft beer bar in Ashwaubenon, WI - brand voice, colors, fonts, hours, events, how the business actually operates, how it grows, and how it replies to people. Read BEFORE writing any caption, graphic prompt, review reply, comment, or growth recommendation, and before answering any question about what the bar should do. Trigger on "Backyard Brew", "@BackyardBrewGB", the backyard-brew-social repo, or any question about the bar's posts, events, reviews, marketing, staffing, or slow days.
---

# Backyard Brew Brand Identity

## Start here: which file answers your question

This skill is the whole brain. Load the reference that matches the task
before writing anything.

| Doing this | Read |
|---|---|
| Writing a caption or post | `references/caption-voice-rules.md` |
| Writing a Gemini prompt or making a graphic | `references/graphics-workflow.md` |
| Replying to a review, comment, or DM | `references/reply-rules.md` |
| Growth, SEO, marketing, new event ideas | `references/growth-playbook.md` |
| What the bar should DO, staffing, slow days, money | `references/operations-reality.md` |
| Thursday's vendor market | `references/backyard-market-brews.md` |

**Any question about the business beyond brand facts starts with
`operations-reality.md`.** It records which days underperform, who works
there, what the owner is trying to achieve, and the constraints an idea has to
survive. Recommending an event the bar already runs, or one that needs staff
it does not have, means that file got skipped.

**Who is asking.** As of late August 2026 the owner runs the social media, the
graphics, and the replies himself. His son built all of this and then left for
college. Assume the person asking wants the finished thing rather than a
tutorial, and that he is doing this between everything else involved in
running a bar. Keep answers short and usable. The printed sheets in
`playbook/` are the human-facing versions of these same processes.

**He works in the Claude desktop app on a Mac, not a terminal.** Never tell
him to open Terminal or run a command. Run it yourself and say what happened.
Skip anything that reads like developer instructions.

## What this business is

A one-of-a-kind outdoor-activity bar in Ashwaubenon, WI (Green Bay area) combining three things nowhere else pairs: an 18-hole disc golf course, 3.5 miles of hiking/snowshoeing trails, and a craft beverage bar pouring **overwhelmingly Wisconsin-made** beer, wine, hard teas, seltzers, and craft soda. Indoor bar has bags, beer pong, pool, darts, and poker machines. Opened August 2024.

> **Known exception, documented so nobody "corrects" it away: a small "Domestics" tap category
> carries a couple of non-Wisconsin beers (Miller Lite, Corona Extra) alongside the Wisconsin
> list.** This is a deliberate small exception to the Wisconsin-only identity, not an error and
> not a contradiction to fix. Keep saying "100% Wisconsin" / "zero outside brands" in the
> *identity/voice* sense — it's still true as the brand's overwhelming character and the thing
> that makes it unique — but don't publish it as a literal, absolute, fact-checkable claim
> (e.g. in schema markup, an FAQ, or a GEO-targeted sentence meant to be quoted verbatim) without
> scoping it, since a customer or an AI system could take it at face value against the actual tap
> list. If this exception ever grows past these two, update this note.

**The core identity: local Wisconsin pride + outdoor adventure + community. Not a sports bar, not a brewery — genuinely something else.** Every piece of content should lean into that uniqueness rather than reading like generic bar marketing.

## Facts (verified — use these exact values)

- **Address:** 3640 Sand Acres Dr, Ashwaubenon, WI 54115
- **Phone:** 920-309-5817
- **Website:** backyard-brew.com
- **Tagline:** "Craft Brews & Things To Do"
- **Sub-tagline:** "Disc Golf, Hiking Trails, Craft Beer, All In Your Backyard"
- **Social:** Instagram `@BackyardBrewGB` (primary, highest priority) · TikTok `@backyard.brewgb` · Facebook "Backyard Brew"
- **Disc golf course:** 18 holes, "Easy" rated, ~1.6 miles, ~1 hour round, USD 5/day paid at the bar
- **Course Membership — USD 150/yr:** unlimited disc golf, hiking & snowshoeing, free tap beer every month, free personal pitcher on your birthday
- **Beer Club — USD 200/yr:** USD 2 off your first beer every day, USD 1 off all night at parties, free tap beer every month, personal pitcher on your birthday (confirmed 2026-07-31)

> **Why prices read "USD 5" here and nowhere else (do not "fix" this — 2026-08-01).**
> The skill loader substitutes a dollar sign followed by a number with the
> arguments this skill was invoked with. Written the normal way, the day pass and
> both membership discounts silently turned into words from the invocation string
> ("planning/day paid at the bar", "party off your first beer"). Every price in
> this list is therefore written USD-first so it survives loading.
> **In captions, graphics, and anything a customer sees, always render them with a
> dollar sign: USD 5 is written as a dollar sign then 5.** The USD form is a
> storage format for this file only, never customer-facing copy.

**Hours (confirmed 2026-07-10 — the automation's version is correct):**
- Mon-Thu: 4pm-9pm
- Fri: 4pm-12am
- Sat: 11am-12am
- Sun: 11am-7pm-ish

**Breakfast service has been discontinued entirely (2026-07-26)** — never mention breakfast in
any caption, graphic, or copy for this brand going forward.

**Pizza (confirmed 2026-07-31):** the bar carries 12 inch pizzas from **two separate local pizza
companies, Renard's and Jolly Bob's**. They are NOT hand-made or made in-house — never say
"hand-made", "house-made", or "from scratch". Renard's is not a cheese supplier and Jolly Bob's
is not a crust supplier; they are two pizza makers whose pizzas are carried. Say "pizzas from
Renard's and Jolly Bob's".

The backyard-brew.com website's own Sunday-closed bug is fixed (shipped 2026-08-04, confirmed
still correct as of the 2026-08-09 update) — don't say the website is wrong anymore. The
Sunday-hours problem now lives on Yelp, Restaurantji, and UDisc instead, which still show Sunday
as closed. See `references/growth-playbook.md` for the full list and what's wrong on each.
Content/captions should follow the hours above regardless of what any one listing says.

## Colors (extracted from the logo — use these exact hex values)

| Color | Hex | Use |
|---|---|---|
| Deep Navy | `#0B1C2D` | Primary — backgrounds, dominant areas |
| Gold/Amber | `#C8922A` | Primary accent — CTAs, borders, highlights, logo ring |
| Warm Yellow | `#F5C842` | Secondary accent — sun/energy pops, don't overuse |
| Cream | `#F5EFD8` | Text on dark backgrounds |
| Disc Blue | `#4A90C4` | Supporting only — beer foam/disc details, never dominant |

## Fonts already established in this brand's content pipeline

- **Anton** — bold condensed display, primary headline font
- **Barlow Condensed** (Medium/SemiBold/Bold) — workhorse body/detail font
- **Alfa Slab One** — heavier slab alternative for food-forward events (used for Bingo Night, Tacos + Poker Club specifically)
- **Pacifico** — script accent, small flourishes only (a footer tagline), never a headline

Logo: navy circle, gold ring, disc golf basket + beer mug icon, sun rays, "Backyard Brew" arched text, "Craft Brews & Things To Do" sub-banner. Design identity is **retro outdoor badge / patch aesthetic** — vintage national park meets craft brewery. Bold, warm, slightly rugged. Not sleek/tech, not cute/trendy.

## Voice

Energetic, community-first, outdoorsy, Wisconsin-proud, fun without being try-hard. Feels like a friend texting you about a cool spot — never corporate, never a copywriting checklist that reads the same way every time (vary the opening move, vary how membership gets mentioned, don't recite the same lines every post — see `references/caption-voice-rules.md` for the full rule set already tuned for this brand's caption generator).

**Non-negotiable: Wisconsin-only, with one documented exception.** Never name-drop or reference any non-Wisconsin brand, chain, or product — **except Miller Lite and Corona Extra**, which are real, on-tap Domestics (see the Facts section above). Don't feature them as the subject of a post, but don't scrub them from a tap-wall photo either. Packers/Brewers/Green Bay references are welcome where natural.

**Always lean into:** the genuine uniqueness (bar + disc golf + hiking, nowhere else like it), Wisconsin exclusivity, the community/regulars vibe, real specifics over generic bar copy.

**Avoid:** generic bar copy, national brand name-drops, overly polished marketing speak, anything that reads like a chain restaurant.

**Emoji (revised 2026-07-26 — the fixed 5-emoji set is retired, Micah's call):** not limited to a
small approved list anymore. Use whatever emoji actually fits the specific thing being described
and the feeling it should land with — 🎤 for karaoke, 🎱 for pool, 🏓 for pickleball, 🃏 for poker,
🌭/🍕/🌮 for the food actually being served, 🐕 for the leashed-pup line, 🎸/🎶 for live music, etc.
Still used naturally and sparingly (one or two per post, not stacked/spammed) — the change is
about picking the *right* emoji for what's actually being said, not about using more of them.

Hashtag cluster (mix niche + local + broad, rotate rather than repeating the same set): `#BackyardBrew` `#DiscGolf` `#GreenBay` `#Ashwaubenon` `#WisconsinBeer` `#CraftBeer` `#Wisconsin` `#DrinkWisconsinbly` `#GreenBayWI` `#WIbeer` `#DiscGolfLife` `#SupportLocal`

## Recurring weekly events (the heartbeat of the content calendar)

| Day | Event | Angle |
|---|---|---|
| Monday | Bingo Night — 9 rounds themed bingo, 6:30pm, free w/ beer purchase, themed + beer + food + cash prizes, kids welcome w/ soda, name-that-tune at halftime. **LRC (Left Right Center, dice, 21+) runs every Monday after bingo ends** — see the money-language rule in `references/caption-voice-rules.md` before writing about it | Prize-reveal — what are we playing for this week? |
| Tuesday | Pickleball Open Play — free w/ beer purchase, 6:30pm, random doubles tournament, hot dogs served all night, winner gets free beer, enter by 6:40pm or auto-placed in losers bracket | Challenge/competitive — think you can beat the regulars? |
| Wednesday | Tacos + Poker Club — beef tacos, quesadillas, loaded nachos all day; poker starts 6pm, free to play w/ beer purchase | Food first, then the game — tacos are the hook |
| Thursday | Backyard Market & Brews (updated 2026-07-26) — weekly vendor market + live local music, 4pm-dusk, rain or shine, 30+ rotating local vendors + a different musician every week; Disc Golf League is separate, earlier in the afternoon | Extremely community/local-business-focused — a small-business showcase, not a party night. Full rules in `references/backyard-market-brews.md`, read it before writing this event's captions |
| Friday | Karaoke Night — 8pm start, all skill levels, variety of genres | "Weekend starts NOW" energy |
| Saturday | Pool Night — open pool tournament, winner plays the bartender for a flight | Tournament angle — beat the bartender, win a flight |

Monthly (bigger, party-style — check for current ones before assuming, this list grows): **Moonlight Brews** (full-moon nights, 7pm, beer specials + crafts), **Celebrate Summer Party** (solstice/BBQ-cookout theme).

**Seasonal, decided and built (2026-08-10):** **Packers Sundays** (September-January) — Sunday's dead 11am-7pm window. Backyard-tailgate framing (round on the course before kickoff, game outside, Wisconsin taps, tailgate food), not sports-bar framing. Packers references welcome. Full reasoning in `references/growth-playbook.md` section 6. Live as a seasonal row in `recurring_events.csv` and handled in the `/sunday` command — unlike the six events above, its kickoff time is deliberately never pre-set; it changes weekly with the NFL schedule, so it gets confirmed with the owner each week rather than guessed or reused from last week.

## Where this feeds into the actual automation

The weekly social-content automation lives in the `backyard-brew-social` repo. `scripts/config.py` is the single source of truth for everything above in code form (colors, angles, memberships, hours) — if brand facts ever change, update `config.py` there, not just this skill, since that's what actually generates the bar's content every week. This skill exists so any *other* Backyard Brew design/content work (outside that repo) stays consistent with what the automation already knows.

## Pre-flight for any Backyard Brew deliverable

- [ ] Colors are the exact hex values from the table above (no approximations, no new palette)
- [ ] Fonts come from the established set, in their roles (Pacifico never a headline; Alfa Slab One only for food-forward events)
- [ ] Zero non-Wisconsin brand names or references anywhere
- [ ] Hours and event facts match THIS file (the website itself is correct now — Yelp, Restaurantji, and UDisc are the stale ones, see `references/growth-playbook.md`)
- [ ] Captions follow `references/caption-voice-rules.md` — varied opener, varied membership mention, no recycled lines
- [ ] Aesthetic is retro outdoor badge / vintage national park — not sleek/tech, not cute/trendy
- [ ] No mention of breakfast anywhere (discontinued 2026-07-26)
- [ ] If it recommends an action, event, or priority: `references/operations-reality.md` was read, and the idea does not duplicate something already running or require staff that does not exist
- [ ] If it is a reply to a person: `references/reply-rules.md` was followed, the review was triaged A/B/C, and the draft was read out loud without sounding defensive

If any box fails, fix it before showing the result.
