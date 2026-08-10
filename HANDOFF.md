# Handoff Checklist

For Micah. Everything that has to happen before you leave for this to keep
working without you. Work top to bottom.

---

## 1. Access your dad needs (do this first, it blocks everything else)

| What | Why | Status |
|---|---|---|
| **Claude paid plan** on his own account | The Code tab requires Pro, Max, Team, or Enterprise. Nothing works without it | |
| **GitHub account**, added as a **collaborator** on `micahh3n/backyard-brew-social` | The repo is public so he can clone it without this, but `/sync` cannot push without it | |
| **Meta Business Suite** admin on the Facebook Page and Instagram | Scheduling the week | |
| **Google Business Profile** owner or manager | The highest-value growth work | |
| **Gemini** account | Making graphics | |
| **ChatGPT** account | Removing the Gemini watermark | |
| **Canva** account | Placing the logo | |
| **Instagram and Facebook** logins for the bar | Stories, comments, groups | |

**The GitHub one is the trap.** Cloning works for anyone because the repo is
public. Pushing does not. If he is not a collaborator and signed in, `/sync`
will pull fine and then silently fail to send anything back. Add him at
Settings → Collaborators before you go, and watch a real `/sync` succeed.

---

## 2. Things only you can fill in

- [ ] **Facebook groups.** The table in `playbook/3-EVERY-DAY.md` has the
      post-type-to-group-type mapping done but the actual group names are
      blank. Fill them in, or sit with him and do it together
- [ ] **Pick the Saturday and Sunday events.** Ranked options are in
      `references/growth-playbook.md`. Choose before you leave so he is
      executing a decision instead of making one
- [x] **Website's Sunday hours — resolved 2026-08-10.** The website itself
      was fixed back in the 2026-08-04 theme update and has stayed correct
      through later updates. The real open item now: **Yelp, Restaurantji,
      and UDisc still show Sunday as closed**, and UDisc also has a stale
      6:30am breakfast window and an "under construction" course flag. All
      three need dad's own login — see `references/growth-playbook.md`
      section 1 for the full list, plus a real 2026-08-04 Google Business
      Profile audit (star rating, review count, wrong attributes, the
      disc-golf-category strategy) that's now folded into that same file.
- [ ] **Name the fourth employee** in `references/operations-reality.md`, or
      delete the placeholder line
- [ ] **Run `/photos` on the backlog.** As of 2026-08-10 there are still
      about 94 unnamed photos sitting in `photos/`. Clear them so he starts
      clean

---

## 3. Get it onto his Mac

Have him do it himself while you watch. If you do it for him, he will not
know how to fix it later.

1. Install the Claude app, sign in, click **Code**
2. **Local** → **Select folder** → his home folder
3. Paste: *"Clone https://github.com/micahh3n/backyard-brew-social into this
   folder, then run bash setup.sh inside it."*
4. Accept the permission prompts
5. **Select folder** again → the new `backyard-brew-social` folder
6. Type `/` and confirm all six commands appear

---

## 4. Do one real week together

Not a demo. An actual week that actually gets posted. This is the part that
makes it stick.

- [ ] He dumps photos off his phone, runs `/photos`, approves the names
- [ ] He runs `/sunday` and reads the output
- [ ] He schedules all 21 in Meta Business Suite himself, you watching
- [ ] He invites a Collab partner on the Thursday Instagram post
- [ ] He adds the location tag to a post
- [ ] He posts one Reel from the shot list
- [ ] He adds photos and one Post to Google Business Profile
- [ ] He answers a real review with `/reply`
- [ ] He runs `/sync` and you confirm it landed on your end

**Sit on your hands.** If you touch the keyboard, he learns nothing. Let him
be slow.

---

## 5. Print and leave these by the computer

`playbook/pdf/` has all four:

1. START-HERE
2. MAKE-A-GRAPHIC
3. EVERY-DAY
4. EVERY-WEEK

Editable Word versions are in `playbook/editable/` if he wants to write on
them.

---

## 6. Tell him the three things that matter most

Everything else is detail. These three carry the business:

1. **Post every day, and never fewer than 2 stories.** Consistency beats
   quality here. A quiet week costs more than a mediocre post.
2. **Google Business Profile is worth more than Instagram.** It is the most
   neglected thing and the highest return. Photos and one Post every week.
3. **Never answer a bad review angry. Use `/reply`.** That is what it is for.

---

## 7. First month

- **Week 1:** check in mid-week. Ask what was confusing, not whether it went
  well
- **Week 2:** let him run it alone. Review the output after, not during
- **Week 4:** run `/growth-week` together and look at whether Tuesday and
  Wednesday moved

If something in the sheets turns out wrong or confusing, fix the markdown and
push it. He runs `/sync` and it updates on his end.

---

## What is already done

- The brand skill knows the voice, the facts, the operations, the weak days,
  the staff, the growth strategy, and how to reply to people
- Six commands: `/sunday` `/photos` `/graphic` `/reply` `/sync` `/growth-week`
- Four printed sheets, in PDF and editable Word
- Nothing posts automatically. Every post is still a person choosing to post it
