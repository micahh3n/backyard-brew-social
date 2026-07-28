# Backyard Brew: Start Here

Everything for the bar's social media and online presence. Written so anyone
can pick it up without asking Micah.

There are four sheets. This one is the map.

| Sheet | When you need it |
|---|---|
| **1-START-HERE** | This page. What everything is |
| **2-MAKE-A-GRAPHIC** | Making a poster or promo image |
| **3-EVERY-DAY** | The daily routine. Stories, groups, comments |
| **4-EVERY-WEEK** | Sunday. Writing the whole week of posts |

---

## First time on this Mac only

Skip this if the **backyard-brew-social** folder is already on the computer.

You need the folder before you can open it. Let Claude fetch it:

1. Open the Claude app, click the **Code** tab
2. Choose **Local**, click **Select folder**, and pick your **home folder**
   (the one with your name on it)
3. Paste this into the message box:

> Clone https://github.com/micahh3n/backyard-brew-social into this folder,
> then run bash setup.sh inside it.

4. Accept when it asks permission
5. When it finishes, click **Select folder** again and choose the new
   **backyard-brew-social** folder

Done once, never again.

The `setup.sh` part is optional. Skip it and everything below still works.
It only adds the PDF builder and the backup poster maker.

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

## Where things live

Everything is in the `backyard-brew-social` folder.

| Folder | What's in it |
|---|---|
| `playbook/` | These four sheets |
| `photos/` | Photos you drop in for posts |
| `assets/logo/` | The logo files |
| `recurring_events.csv` | The weekly schedule. Edit when events change |
| `posts.csv` | One-off events. Add a row for a party or holiday |

Open any of these in TextEdit. They are plain text files, so edit them
whenever something changes.

### Dropping in photos

**Dump them straight off your phone into `photos/`. Do not rename anything.**

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
Meta Business Suite for the week. Sheet 4.

**Every day, about 15 minutes.** Stories, share the 11am post to Facebook
groups, answer comments. Sheet 3.

**As needed.** Make a graphic (sheet 2), reply to a review (`/reply`).

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

## Reading, printing, and editing these sheets

Every sheet comes in three forms, all in the `playbook` folder:

| Folder | What it is | Open it with |
|---|---|---|
| `pdf/` | For printing and taping up | Preview. Just double-click |
| `editable/` | Word documents you can type into | **Pages**, already on the Mac |
| the `.md` files | What Claude reads | Nothing. Leave these alone |

**To change something, the easy way is to just ask Claude:**

> Add these Facebook groups to the daily sheet: [names]

> Change the story minimum from 2 to 3

It updates the sheet and rebuilds the PDF and the Word version together, so
all three stay matched.

**To type into it yourself**, open the file in `editable/` with Pages. Fill in
the Facebook groups table, cross things out, add notes. Print from Pages when
you are done.

One catch: edits made in Pages live only in that Word file. Claude will not
know about them. Anything that should stick permanently is better done by
asking Claude.

---

## If something is not working

Ask Claude. Describe what happened in plain words:

> The /sunday command isn't showing up when I type slash

> It wrote a caption mentioning a beer we don't carry

> The PDFs won't rebuild

It can read its own setup and fix most things. If it cannot, text Micah.
