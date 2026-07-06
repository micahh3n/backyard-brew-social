# Backyard Brew Social — One-Time Setup Guide

You only do this **once**. Work through it top to bottom. Total time: about an hour.
Nowhere in here do you paste a password or token into a chat — tokens go straight
into GitHub's locked "Secrets" box, which I'll point you to in Part 5.

**The five parts:**
1. Put the folder on GitHub with GitHub Desktop
2. Confirm your Instagram is a Business account linked to your Page
3. Create the Meta developer app + get your tokens (the big one)
4. Find your Page ID and Instagram ID
5. Paste everything into GitHub Secrets + run your first test

---

## Part 1 — GitHub Desktop (so you can drag photos, not use a website)

### 1a. Install it
1. Go to **https://desktop.github.com** and click the big **Download for Windows** button.
2. Run the downloaded `GitHubDesktopSetup.exe`. It installs and opens itself — no options to fuss with.
3. When it opens, click **Sign in to GitHub.com** and log in with your existing GitHub account.
4. It asks to "Configure Git" — just click **Continue** (your name/email are fine as-is).

### 1b. Add this folder as a repository
1. In GitHub Desktop's top-left menu: **File → Add local repository**.
2. Click **Choose…** and select this folder:
   `C:\Users\micah\OneDrive\Desktop\backyard-brew-social`
3. It'll say *"This directory does not appear to be a Git repository — Create a repository?"*
   Click the blue **create a repository** link.
4. On the next screen leave everything as-is and click **Create Repository**.

### 1c. Publish it to GitHub (must be PUBLIC)
1. Click the **Publish repository** button (top bar).
2. **Uncheck** the box that says **"Keep this code private."**
   > It has to be public — Instagram can only pull your photos from a public web
   > address. It's just event photos you're about to post publicly anyway.
3. Name can stay `backyard-brew-social`. Click **Publish Repository**.

Done. From now on, your normal rhythm is: drag photos into the `photos` folder,
edit the spreadsheets, then in GitHub Desktop click **Commit to main** (bottom-left)
and **Push origin** (top bar). That's how your changes reach the system.

---

## Part 2 — Confirm Instagram is a Business account linked to your Page

The system can only post to a **Business** Instagram account that's connected to
your Facebook Page. Let's make sure yours is (takes 3 minutes).

### 2a. Is it a Business account?
On your phone, in the **Instagram app**:
1. Go to your profile → tap the **≡ menu** (top right) → **Settings and privacy**.
2. Scroll to **Account type and tools** → **Switch account type**.
3. If it offers **Switch to professional account**, tap it and choose **Business**
   (not Creator). If it already says you're a Business/Professional account, you're set —
   back out without changing anything.

### 2b. Is it linked to the Backyard Brew Facebook Page?
Easiest path is from the Page side, on a computer:
1. Go to **https://business.facebook.com** and open **Business Settings** (gear icon).
2. Under **Accounts → Instagram accounts**, check that **@BackyardBrewGB** is listed
   and connected to the **Backyard Brew** Page.
3. If it's not there: on your phone, Instagram → **Settings → Accounts Center →
   Add accounts**, and connect the Backyard Brew Facebook Page.

> If any of this is confusing, that's normal — Meta moves these menus around.
> The goal is simply: **@BackyardBrewGB is a Business account, and it shows up
> connected to the Backyard Brew Page.** Once that's true, continue.

---

## Part 3 — Create the Meta developer app + get your tokens

This is the longest part. Go slow; it's just clicking.

### 3a. Make the app
1. Go to **https://developers.facebook.com** and click **Log In** (top right), using
   the Facebook account that manages the Backyard Brew Page.
2. First time only: it asks you to **register as a developer** — click **Get Started**,
   accept the terms, verify your account (phone/email) if asked.
3. Top right, click **My Apps → Create App**.
4. **Use case screen:** choose **Other** → **Next**.
5. **App type:** choose **Business** → **Next**.
6. **Details:** App name = `Backyard Brew Poster` (any name). Contact email = yours.
   Leave "Business portfolio" as-is → **Create app** (may ask your FB password).

### 3b. Add the tools the app needs
1. In your new app's left sidebar, find **Add products** (or the "+" next to Products).
2. Find **Instagram Graph API** → click **Set up**.
   (On some layouts this is bundled under **Instagram → API setup with Facebook login**.)
3. Also make sure **Facebook Login for Business** is added if prompted — click **Set up**.
   You won't build a login page; it just needs to exist for token generation.

### 3c. Generate a token in the Graph API Explorer
1. In the left sidebar go to **Tools → Graph API Explorer**
   (or open **https://developers.facebook.com/tools/explorer**).
2. Top right, in **Meta App**, select **Backyard Brew Poster**.
3. Click **User or Page** dropdown → choose **Get Page Access Token** →
   pick the **Backyard Brew** Page. Approve the popups (say **yes/allow** to everything,
   and make sure the Backyard Brew Page and Instagram are checked in the permission list).
4. Click the **Permissions** dropdown and add each of these (type to search each one):
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_content_publish`
   - `instagram_basic`
   - `read_insights`
   - `instagram_manage_insights`
5. Click **Generate Access Token**. Approve any popup.
6. You now have a token in the **Access Token** box. **This is a short-lived token
   (about 1 hour).** We'll turn it into a 60-day one in the next step. Leave this tab open.

### 3d. Turn it into a long-lived (60-day) token
1. Open a new tab: **Tools → Access Token Debugger**
   (**https://developers.facebook.com/tools/debug/accesstoken**).
2. Paste the token from 3c into the box and click **Debug**.
3. At the bottom click **Extend Access Token**. It generates a **long-lived** token
   (valid ~60 days). **Copy that extended token** — this is the real one you'll save.

> Keep this token somewhere private for the next few minutes (a temporary note).
> You will paste it into GitHub Secrets in Part 5, then delete your note.
> **Every ~60 days** you'll repeat steps 3c–3d to refresh it — the system will post a
> reminder in `status.log` when it's within 10 days of expiring.

---

## Part 4 — Find your Page ID and Instagram ID

Still in the **Graph API Explorer** (the tab from 3c):

1. In the request box at the top, make sure the method is **GET**, then type:
   `me?fields=id,name` and click **Submit**. The **`id`** it returns is your
   **Facebook Page ID** → save it as `META_PAGE_ID`.
2. Now type: `me?fields=instagram_business_account` and click **Submit**.
   It returns `instagram_business_account { id: ... }`. That **`id`** is your
   **Instagram user ID** → save it as `META_IG_USER_ID`.

If step 2 returns nothing, your Instagram isn't linked to the Page yet — go back to Part 2.

You should now have three values written on your temporary private note:
- The long-lived token → `META_PAGE_ACCESS_TOKEN`
- The Page ID → `META_PAGE_ID`
- The Instagram ID → `META_IG_USER_ID`

Plus one more you already have or will make:
- Your Anthropic API key → `ANTHROPIC_API_KEY`
  (Get it at **https://console.anthropic.com** → **API Keys** → **Create Key**, and
  add a little billing credit. Captions cost roughly pennies per week.)

---

## Part 5 — Paste everything into GitHub Secrets

This is the **only** safe place these go. Never put them in the spreadsheets or in a chat.

1. In your web browser, go to your repo:
   `https://github.com/<your-username>/backyard-brew-social`
2. Click **Settings** (top tab of the repo) → in the left menu, **Secrets and
   variables → Actions**.
3. Click **New repository secret**. For each one below, put the **Name** exactly as
   shown, paste the **value** into the Secret box, and click **Add secret**:

   | Name (type exactly) | Value to paste |
   |---|---|
   | `ANTHROPIC_API_KEY` | your Anthropic key |
   | `META_PAGE_ACCESS_TOKEN` | the long-lived token from 3d |
   | `META_PAGE_ID` | the Page ID from Part 4 |
   | `META_IG_USER_ID` | the Instagram ID from Part 4 |

4. When all four show in the list, **delete your temporary note** with the tokens.

> GitHub Secrets are encrypted and hidden — even you can't read them back after saving,
> and they never appear in logs. That's exactly what we want.

---

## Part 6 — First test run

1. In your repo on GitHub, click the **Actions** tab.
2. If it says workflows are disabled on a fork/new repo, click the green **"I understand
   my workflows, go ahead and enable them."**
3. Click **Sunday - Generate Captions** in the left list → **Run workflow** → **Run workflow**.
4. Wait ~1 minute, refresh. A green check means it ran. Open GitHub Desktop and click
   **Fetch/Pull origin** to bring the results down — `posts.csv` now has the week's posts.
5. Open `posts.csv`, read a couple captions, change any `status` from `needs_review` to
   `approved` on ONE post whose time is in the past, then **Commit + Push**.
6. Back in **Actions**, run **Hourly - Post Approved** manually once. Check that the post
   shows up on your Facebook/Instagram. 🎉

If a run fails, click into it to see the red step — 90% of the time it's a secret name
typo or a token that needs refreshing. Fix and re-run.

---

See **HOW-TO-USE-WEEKLY.md** for your simple every-week routine.
