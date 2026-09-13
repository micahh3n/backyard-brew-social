# Backyard Brew: Start Here

Everything for the bar's social media and online presence. Written so anyone
can pick it up without asking Micah.

## Where to find things

Open the **backyard-brew-social** folder. Everything you need sits at the
top:

| I need... | Open this |
|---|---|
| The vendor sign-in sheet (print or edit) | **1 Vendor Market** |
| The vendor signup list, message templates, vendor map | **1 Vendor Market** |
| A poster or flyer to print or post | **2 Posters and Flyers** |
| Order slips | **2 Posters and Flyers** |
| A photo | **3 Photos** |
| The logo | **4 Logo** |
| How to do something | **5 How-To Guides** |
| The pickleball bracket | **Pickleball.html** |

**Never open "Claude Files - Do Not Touch."** Claude keeps its own files in
there. If you need something from it, ask Claude.

## The how-to guides

| Guide | When you need it |
|---|---|
| **0 START HERE** | This page |
| **Make a Graphic** | Making a poster or promo image |
| **Every Day** | The daily routine. Stories, groups, comments |
| **Every Week** | Sunday. Writing the whole week of posts |

---

## First time on this Mac only

Skip this if the **backyard-brew-social** folder is already on the computer.

You need the folder before you can open it. Let Claude fetch it:

1. Open the Claude app, click the **Code** tab
2. Choose **Local**, click **Select folder**, and pick your **home folder**
   (the one with your name on it)
3. Paste this into the message box:

> Clone https://github.com/micahh3n/backyard-brew-social into this folder,
> then run bash "Claude Files - Do Not Touch/setup.sh" inside it.

4. Accept when it asks permission
5. When it finishes, click **Select folder** again and choose the new
   **backyard-brew-social** folder

Done once, never again.

**Do not skip the setup part.** iPhone photos are HEIC files, and without
that step nothing on the computer can read them, so `/photos` will not be able
to see what your pictures are. It also adds the PDF builder and the backup
poster maker.

---

## Opening it

Everything happens in the **Claude app**. No Terminal, ever.

1. Open the Claude app
2. Click the **Code** tab at the top
3. Choose **Local**, click **Select folder**, pick the
   **backyard-brew-social** folder
4. Type `/` in the message box

That is it. After the first time, the folder is already in the sidebar, so
you just click it.

### The six commands

Type `/` and a menu appears. Six commands do the work:

| Type this | What happens |
|---|---|
| `/sunday` | Writes all 21 posts for the week, plus a Google Business post |
| `/photos` | Looks at your new photos and names them for you |
| `/graphic` | Writes the Gemini prompt for a poster, then the captions |
| `/reply` | Turns a review or comment into a professional response |
| `/sync` | Gets Micah's latest changes and sends yours to him |
| `/growth-week` | Asks how last week went, then gives you a short list of what to do next |

You do not have to use the commands. Plain English works too. "Write me a post
for Friday" does the same thing as `/sunday` for one day.

### It already knows the bar

You do not need to explain anything. It knows the hours, the events, the
prices, the memberships, the colors, the fonts, how the bar sounds, which
nights are slow, who works there, and what the goals are.

So you can just ask:

> What are some good events that would bring people in on a Sunday?

> Why do you think Tuesdays aren't busier?

> Someone asked in a comment if dogs are allowed. What do I say?

> Write something for the disc golf course for tomorrow.

If it ever gets a fact wrong, tell it. Then tell Micah so the file gets fixed
for next time.

---

## Changing the schedule or events

The weekly schedule and one-off events live in Claude's files. Don't edit them
yourself. Tell Claude what changed:

> Karaoke moved to 8pm starting next week

> Add a Halloween party on October 31

---

### Dropping in photos

**Dump them straight off your phone into the 3 Photos folder. Do not rename anything.**

Then type `/photos`. Claude opens each one, sees what is actually in it, and
names them all properly. It shows you the list first and waits for you to say
yes. It also skips blurry shots and near-duplicates.

That is the whole job. If you ever want to name one yourself, the pattern is
`2026-09-14_bingo.jpg`, and the event keywords are `bingo`, `pickleball`,
`poker`, `market`, `karaoke`, `pool`.

### Sharing with Micah

Both computers use the same folder through GitHub. Type `/sync` to send your
photos and changes to him and pull down anything he sent you.

Worth doing after adding photos, and any time something feels out of date.

---

## The weekly rhythm

**Sunday, about an hour.** Run `/sunday`, get all 21 posts, schedule them in
Meta Business Suite for the week. See the Every Week guide.

**Every day, about 15 minutes.** Stories, share the 11am post to Facebook
groups, answer comments. See the Every Day guide.

**As needed.** Make a graphic (the Make a Graphic guide), reply to a review (`/reply`).

**Whenever you want a plan.** Run `/growth-week`.

---

## Three rules

1. **Nothing posts by itself.** Claude writes it, you post it. Nothing goes
   out without a person choosing to send it.
2. **Wisconsin only.** Never mention a beer, brand, or product that is not
   made in Wisconsin. This is the one rule with no exceptions.
3. **Look at it before you post it.** Especially graphics. Check the spelling,
   check nothing looks warped, check it sounds like us.

---

## Two things about the app

**It asks permission before doing things.** The first few times, Claude will
ask before editing a file or running something. Click Accept. If the asking
gets old, change the mode next to the message box from **Manual** to
**Accept edits**.

**Stay in one session for the weekly work.** Clicking **+ New session**
starts an isolated copy of the folder, which may not include photos you just
added. Use the session already sitting in the sidebar.

---

## Printing or changing these guides

To print one, open it from **5 How-To Guides** and print it. Double-click
opens it in Preview.

**To change a guide, ask Claude:**

> Add these Facebook groups to the daily sheet: [names]

> Change the story minimum from 2 to 3

It updates the guide and makes a fresh PDF.

---

## If something is not working

Ask Claude. Describe what happened in plain words:

> The /sunday command isn't showing up when I type slash

> It wrote a caption mentioning a beer we don't carry

> The PDFs won't rebuild

It can read its own setup and fix most things. If it cannot, text Micah.
