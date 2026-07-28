# Making a Graphic

The exact process Micah used for every poster the bar has posted. Follow it in
order. About 15 minutes once you have done it twice.

**What you need open:** the Claude app (Code tab), Gemini, ChatGPT, Canva.

---

## Step 1. Pick your photo first

Before anything else, find a real photo of the bar, the course, the food, or
the event. A real photo of the actual place is what makes these look good
instead of looking generated.

Have the logo ready too. It is in `assets/logo/`.

---

## Step 2. Ask Claude for the prompt

In the Claude app, type:

```
/graphic bingo night this monday
```

Replace that with whatever the graphic is for. Claude may ask which photo you
are using. Tell it what is in the photo, like "the tap wall" or "the first tee
at sunset," so the prompt matches.

**What you get back:** one block of text to copy, plus the captions.

That block already includes the brand colors, the fonts, the retro badge
style, the 4:5 size, instructions to leave an empty circle for the logo, and a
list of AI junk to avoid. You do not need to add anything to it.

---

## Step 3. Run it through Gemini

Go to Gemini Image. Then:

1. Attach your photo
2. Attach the logo
3. Paste the prompt
4. Send

**It must be 4:5 vertical.** The prompt says so, but check the result. If it
comes out square or wide, ask Gemini to redo it at 4:5.

**Not happy with it?** Say what is wrong and ask again. "Make the headline
bigger." "The colors are too dark." "Keep the photo but change the layout."
Two or three tries is normal.

**Still bad after three tries?** Skip to the backup at the bottom of this
sheet.

---

## Step 4. Remove the watermark

Gemini puts a small watermark in the bottom right corner.

Save the image, open ChatGPT, upload it, and ask it to remove the watermark
from the bottom right corner.

Check the corner afterward. Sometimes it smudges the area instead of cleaning
it.

---

## Step 5. Put the real logo on in Canva

Gemini leaves an empty circle in the design. That circle is where the real
logo goes.

We do this by hand because AI cannot draw our logo correctly. It always gets
it slightly wrong, and slightly wrong looks worse than not having it.

1. Open Canva, upload the image
2. Upload the logo from `assets/logo/`
3. Drag the logo onto the empty circle
4. Resize so it sits inside the circle cleanly, not overlapping the edges
5. Download as PNG

---

## Step 6. Name it and check it

Save it into the `photos/` folder using the date and event:

```
2026-09-14_bingo.jpg
```

**Now look at it properly. This step is why our graphics look right.**

- [ ] Every word spelled correctly. Read each one out loud
- [ ] Nothing warped. Check hands, faces, letters, straight lines
- [ ] The time and price are actually correct
- [ ] The logo sits in the circle cleanly
- [ ] No beer or brand showing that is not made in Wisconsin
- [ ] It sounds like us. Not like a generic bar ad

**Anything wrong, fix it before posting.** A misspelled poster stays on the
internet.

---

## Step 7. Post it

Claude already gave you the Facebook and Instagram captions in step 2. Change
anything that does not sound right, then post or schedule it.

Instagram hashtags go in the first comment, not the caption.

---

## Backup: when Gemini will not cooperate

Some graphics fight you. Lots of text is usually the reason, because AI is bad
at spelling.

We have a version that cannot get it wrong. It builds the poster with the real
fonts and the real logo instead of generating it, so the spelling and colors
are always exactly right.

Ask Claude:

> Gemini keeps messing this up. Can you build it with the flyer renderer
> instead?

It handles the rest. First time only, it may ask you to run a setup command.

Best choice for anything with a lot of words on it.

---

## What good looks like

- A real photo of our actual place, not a stock bar
- Navy and gold, the retro outdoor badge feel
- Few words, big and correctly spelled
- Our real logo, sharp
- Nothing about it says a computer made it
