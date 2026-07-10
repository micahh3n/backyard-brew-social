# Backyard Brew Social — One-Time Setup Guide

You only do this **once**. Total time: about 10 minutes. Nowhere in here do
you paste anything into a chat — your API key goes straight into GitHub's
locked "Secrets" box, which Part 2 points you to.

**The two parts:**
1. Put the folder on GitHub with GitHub Desktop
2. Get an Anthropic API key and paste it into GitHub Secrets

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

### 1c. Publish it to GitHub
1. Click the **Publish repository** button (top bar).
2. This repo doesn't post anywhere automatically anymore, so it's fine to leave
   **"Keep this code private"** checked if you'd rather it not be public.
3. Name can stay `backyard-brew-social`. Click **Publish Repository**.

Done. From now on, your normal rhythm is: drag photos into the `photos` folder,
edit the spreadsheets, then in GitHub Desktop click **Commit to main** (bottom-left)
and **Push origin** (top bar). That's how your changes reach the system.

---

## Part 2 — Get an Anthropic API key

This is what writes your captions every Sunday. No Meta/Facebook developer
setup exists anywhere in this system anymore — this is the only key you need.

1. Go to **https://console.anthropic.com** and sign up/log in.
2. **API Keys → Create Key**. Copy the key it shows you (you won't be able to
   see it again after leaving the page).
3. Add a little billing credit on the account — captions for this volume of
   posting cost roughly a few dollars a month at most.
4. In your repo on GitHub.com: **Settings** (top tab) → **Secrets and
   variables → Actions** → **New repository secret**.
5. Name: `ANTHROPIC_API_KEY`. Value: the key you copied. Click **Add secret**.

That's the entire setup. See **HOW-TO-USE-WEEKLY.md** for your simple every-week routine.
