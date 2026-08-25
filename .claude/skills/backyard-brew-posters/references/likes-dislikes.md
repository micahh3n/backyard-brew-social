# What Micah likes and does not like

Built from the Sunday Market & Brews poster session (2026-08-19), where every
item below was either asked for or rejected out loud. Add to it whenever he
corrects a poster — that is how this stays a one-shot skill instead of a
starting point.

## Likes — do these by default

**Photo**
- Full-bleed, edge to edge. The photo IS the poster's background.
- Real shots from the bar's own library. Genuine people, real booths, real
  crowd. That authenticity is the point — he said "so it is genuine."
- Professional photos over phone snaps when both exist.

**Type**
- Chunky, friendly display faces that stop a scroll. His words: "way cuter
  font so it pops better but doesn't look sloppy."
- Big. The headline should read across a room.
- Barlow Condensed, letterspaced and uppercase, for every small line.

**Color and structure**
- Navy ground, gold blocks, cream text. Dark scrims top and bottom over the
  photo, clear photo in the middle.
- Solid gold bars and blocks for the loudest information. High contrast,
  flat color, no gradient fills.
- A thin gold frame line inset from the edge — makes it read as designed
  rather than a snapshot with text on it.
- A big logo. He asked for it larger, twice.

**Content**
- Two-in-one when the event has two audiences: sell the event to customers
  AND recruit vendors on the same graphic. Don't make him choose.
- Emoji for icon rows. He asked for them over hand-drawn SVG icons.
- Brand-voice lines like "Bring cash, bring friends, bring the leashed pup."

**Delivery**
- An editable Claude Design canvas AND finished full-size PNGs. He wants to
  be able to tweak, but he also wants something he can post immediately.
- Print 18×24 and 4:5 feed, every time.

## Dislikes — never do these

- **Shaped photo windows.** Arches, circles, rounded cutouts, any frame that
  crops the photo into a shape. His words: "it looks awkward when you use
  that weird photo shape."
- **Sunbursts, rays, or any pattern behind the type.** Asked to "ditch the
  sunburst idea." Busy backgrounds fight the photo.
- **Anton as a poster headline.** Technically fine, no personality. It reads
  generic next to the chunky faces he actually likes.
- **Hand-drawn SVG icons.** He asked for real emoji instead.
- **Address, website, or social handle on the art.** Removed on request —
  "i will elaborate in the caption."
- **Expiring one-off ribbons** like "NEW DAY — STARTING AUG 30." Same reason:
  caption's job, and it makes the poster single-use.
- **Anything that reads like a Canva template.**
- **Made-up facts.** Never a fixed vendor count ("30+"), never a commission
  claim, never a detail the brand skill doesn't confirm.
- **Long email addresses in a display font.** Lilita One's hyphen reads like
  an en-dash and `backyard-brew.com` becomes ambiguous. Contact strings go in
  Barlow Condensed Bold.

## Judgement calls he has already made

- **Vendor contact is DM**, not email, on the art.
- **Font is chosen per poster**, not locked — but *you* choose it, from the
  shortlist in `fonts.md`. Do not ask him.
- **Photo is chosen by you**, not by him. Pick, build, show. He'll say if he
  wants a different one.
- **Caption only when he asks for it.**
- **Vendor-facing copy says two things and stops: the space is free, and DM
  us.** Nothing else. No screening criteria, no setup times, no bring-your-own
  list, no email address (2026-08-19, after a Facebook event description came
  back with all of it). The screening rule (established shops with an online
  following, no private sellers) is real, but Micah handles it in the DM rather
  than publishing it. This applies to captions and event descriptions as much
  as to the art. Do not talk him into adding it back.

## Copy edits he has made by hand (2026-08-19)

He rewrote four lines on the Sunday market poster in the canvas editor. The
pattern behind them:

| I wrote | He changed it to | The lesson |
|---|---|---|
| "A weekly showcase of local small businesses" | "SUPPORTING AND SHOWCASING LOCAL BUSINESSES, ONE WEEK AT A TIME" | Active and warmer. "Supporting" beats a flat description — the bar is doing something for these businesses, not just hosting them. |
| "Bring cash, bring friends, bring the leashed pup." | "Bring your friends, bring the pup, and drink some craft beer" | Don't tell people to bring cash. Don't say "leashed" — it reads like a rule. End on the beer. |
| "Calling every local maker & small business" | "CALLING ALL LOCAL SMALL BUSINESSES AND MUSICIANS" | Name musicians explicitly — they are a recruiting target too, not a footnote. "Small businesses" over "makers". |
| "DM us to claim a booth — vendors & musicians welcome" | "DM us to claim a booth" | CTAs are short. One action, no qualifiers hanging off it. |

Generalize: shorter CTAs, warmer and more active positioning lines, no
instructions that read as rules, and craft beer earns a mention in the
customer-facing line.

## Sticker overlays (added 2026-08-19)

He likes a **sticker** as a way to bolt a secondary message onto a poster
without touching the layout: "maybe even with a graphic ... as like a sticker
almost." Build them as a tilted die-cut vinyl sticker, absolutely positioned
over the clear photo band so nothing reflows when it is deleted:

- `transform: rotate(-7deg)`, navy fill, **thick cream border**
  (`9px solid #F5EFD8` on the poster, `6px` on social) — the cream edge is
  what makes it read as a sticker instead of a badge
- `border-radius: 34px` / `24px`, heavy shadow `0 20px 48px rgba(4,12,21,0.68)`
- Emoji on top, two short display-font lines, one tiny Barlow caption
- Put the whole thing in one commented block so removing it is one delete

**Trademarks.** Never put a sports team's logo, wordmark, or "G" on a poster —
those are protected marks and this is advertising for a business. Naming the
team in text ("PACKERS SUNDAYS") to say which game is on is normal and fine;
the logo is the line. Same rule for any brand that is not Backyard Brew's own.

**Seasonal elements get a comment and a note to Micah.** Football is Sept-Jan
only, and the brand skill forbids stating a kickoff time without confirming it
that week — so a football sticker carries no time, and the canvas annotation
tells him to delete it outside the season.

## The reskin correction (2026-08-24)

Micah, on the first Karaoke and Tacos + Poker posters: *"yes they look good but
there is no variation. it literally looks like a re skin of the market one.
they all need to be different based on the night."*

**`anatomy.md` is the MARKET poster's recipe, not the house template.** Pouring
a new event into the same centred stack — logo on top, qualifier over event
name, gold time bar, positioning line, 3-up emoji row, voice line, gold callout
— produces a poster that is recognisably the same graphic with the words
swapped. That is the failure mode this section exists to prevent.

**Every night gets its own composition.** What stays constant is the *brand*:
navy ground, gold blocks, cream type, a full-bleed real photo, the thin gold
frame, and a big logo. What must change per night is the *structure* — where
the logo sits, how the headline is set and aligned, what carries the day/time,
what device does the shouting.

Systems built so far, so the next one is different again:

| Night | System |
|---|---|
| Sunday Market & Brews | Centred stack, soft gradient scrims top and bottom, 3-up emoji feature row, gold callout block at the foot. (`anatomy.md`) |
| Tacos + Poker Club | Hard-edged navy slab across the bottom half with a gold rule on its top edge, everything ragged-left, logo top-RIGHT, gold day-tab top-LEFT, a gold CTA band flush to the slab's bottom. |
| Karaoke Night | Gold marquee band straight across the middle of the photo carrying the headline, logo top-LEFT, gold day-tab top-RIGHT, navy footer band with an inline gold-diamond fact row and a cream-OUTLINED CTA box (not a gold slab). |

Ideas still unused: headline rotated or bleeding off an edge; a vertical gold
band down one side; the photo as a hard-edged panel inset in a navy field; the
day/time set huge as the dominant element instead of the event name.

**A night without a 3-up emoji row is fine.** The emoji row is one device among
several, not a required slot — both 2026-08-24 posters dropped it and replaced
it with an inline fact row separated by gold SVG diamonds. Bring it back when a
layout has room for it, not out of habit.

## Photo hunting (learned 2026-08-24)

- **Search the unclassified backlog before concluding a photo does not exist.**
  There was no file with `poker` in its name that was usable — `Poker_default_art.jpg`
  is old flyer art and `_retired/DO-NOT-POST_cash_on_poker_table.JPG` is actually
  LRC on a pool table with cash out. The real poker photos were sitting unnamed
  in the `IMG_9xxx.JPG` backlog (9291-9294, 9479-9483). Contact-sheet the backlog
  rather than trusting filenames.
- **Read the frame at poster scale for other people's trademarks.** Candid bar
  photos are full of them and they are much more visible at 18x24 than in a
  thumbnail. Things that forced a re-crop on this batch: a Packers shirt, a
  Bucks cap, a Miller Lite can (the bar's whole claim is 100% Wisconsin *craft*),
  and the poker table's own printed felt reading "BLACKJACK PAYS 3 TO 2 /
  INSURANCE PAYS 2 TO 1" directly under a POKER CLUB headline.
- **Song lyrics on the karaoke screens are published lyrics.** The packed-room
  shots have the screens mid-song and the words are legible at print size. Crop
  them out or pick another frame; do not put readable lyrics on the art.
- **Match the crop to the layout's photo band, not to the photo.** Work out
  which vertical slice the composition actually leaves uncovered, then crop so
  the subject lands there. On the karaoke marquee the microphone had to clear the
  band — buried behind the gold, the poster stopped reading as karaoke at all.
