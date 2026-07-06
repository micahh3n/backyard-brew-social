"""
config.py - Single source of truth for Backyard Brew's brand, timing, and rules.

Everything brand-specific lives here so the logic files stay clean. If the bar's
schedule, colors, hashtags, or voice change, this is usually the only file to edit.
"""

from __future__ import annotations

import os
from zoneinfo import ZoneInfo

# ---------------------------------------------------------------------------
# Paths (resolved relative to the repo root, which is the parent of /scripts)
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTOS_DIR = os.path.join(REPO_ROOT, "photos")
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")
LOGO_DIR = os.path.join(ASSETS_DIR, "logo")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
RECURRING_CSV = os.path.join(REPO_ROOT, "recurring_events.csv")
POSTS_CSV = os.path.join(REPO_ROOT, "posts.csv")
STATUS_LOG = os.path.join(REPO_ROOT, "status.log")
# Where process_photos.py writes finished images that get posted.
GENERATED_DIR = os.path.join(REPO_ROOT, "photos", "_generated")

# ---------------------------------------------------------------------------
# Timezone -- everything schedules in Central time (Wisconsin).
# ---------------------------------------------------------------------------
TIMEZONE = ZoneInfo("America/Chicago")

# ---------------------------------------------------------------------------
# Anthropic model for caption generation. Sonnet is smart, fast, and cheap.
# Override by setting the ANTHROPIC_MODEL secret/env var.
# ---------------------------------------------------------------------------
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")

# ---------------------------------------------------------------------------
# Business identity (used inside the caption prompt and flyers)
# ---------------------------------------------------------------------------
BUSINESS = {
    "name": "Backyard Brew",
    "tagline": "Craft Brews & Things To Do",
    "sub_tagline": "Disc Golf, Hiking Trails, Craft Beer, All In Your Backyard",
    "address": "3640 Sand Acres Dr, Ashwaubenon, WI 54115",
    "city": "Ashwaubenon",
    "region": "Green Bay",
    "opened": "August 2024",
    "instagram": "@BackyardBrewGB",
    "facebook": "Backyard Brew",
    # Latitude/longitude of the bar -- used to auto-find the Meta location tag.
    "latitude": 44.4741,
    "longitude": -88.1013,
}

HOURS = {
    "Monday": "4pm-9pm",
    "Tuesday": "4pm-9pm",
    "Wednesday": "4pm-9pm",
    "Thursday": "4pm-9pm",
    "Friday": "4pm-12am",
    "Saturday": "11am-12am (breakfast 6:30am-1pm)",
    "Sunday": "11am-7pm-ish (breakfast 11am-1pm)",
}

MEMBERSHIPS = (
    "Course Membership $150/yr: unlimited disc golf, hiking & snowshoeing, "
    "free tap beer every month, free personal pitcher on your birthday. "
    "Beer Club $200/yr: $2 off your first beer every day, $1 off all night at "
    "parties, personal pitcher on your birthday."
)

# ---------------------------------------------------------------------------
# Brand colors (retro outdoor badge / vintage national park aesthetic)
# ---------------------------------------------------------------------------
COLORS = {
    "navy": "#0B1C2D",     # primary / backgrounds
    "gold": "#C8922A",     # CTAs, accents, borders
    "yellow": "#F5C842",   # secondary pops
    "cream": "#F5EFD8",    # text on dark
    "disc_blue": "#4A90C4",  # supporting only
}

# On-brand emoji set. Used sparingly, never spammed.
EMOJIS = ["\U0001F37A", "\U0001F3AF", "\U0001F332", "\U0001F3D2", "⛰️", "\U0001F37B"]

# ---------------------------------------------------------------------------
# Instagram hashtag pool. The caption stays clean; these go in the FIRST
# COMMENT. pick_hashtags() rotates a mix so the same set never repeats.
# ---------------------------------------------------------------------------
HASHTAG_POOL = [
    "#BackyardBrew", "#DiscGolf", "#GreenBay", "#Ashwaubenon",
    "#WisconsinBeer", "#CraftBeer", "#Wisconsin", "#DrinkWisconsinbly",
    "#GreenBayWI", "#WIbeer", "#DiscGolfLife", "#SupportLocal",
]
# #BackyardBrew is always included; the rest are mixed niche/local/broad.
HASHTAG_ALWAYS = "#BackyardBrew"

# ---------------------------------------------------------------------------
# Per-day content angle -- baked into the caption prompt per event so each
# night has its own hook, not a generic "come on in".
# ---------------------------------------------------------------------------
EVENT_ANGLES = {
    "Bingo Night": "Prize-reveal angle -- what are we playing for this week?",
    "Pickleball Open Play": "Challenge/competitive angle -- think you can beat the regulars?",
    "Tacos + Poker Club": "Food first, then the game -- the tacos are the hook.",
    "Disc Golf League + Ladies Night": "Calling all ladies + league leaderboard hype -- two angles, alternate or combine.",
    "Line Dancing + Karaoke Night": "'Weekend starts NOW' energy.",
    "Pool Night": "Tournament angle -- beat the bartender, win a flight.",
}

# ---------------------------------------------------------------------------
# Default fallback posting schedule (used until real Insights data takes over).
# Times are 24h local. Keyed by (day_of_week, post_type). "today" = event day,
# "teaser" = the evening-before anticipation post. Reminder posts in a campaign
# reuse the "teaser" evening slot on their own day.
# ---------------------------------------------------------------------------
DEFAULT_TIMES = {
    ("Monday", "today"): "12:00",
    ("Tuesday", "today"): "12:00",
    ("Wednesday", "today"): "12:00",
    ("Thursday", "today"): "12:00",
    ("Friday", "today"): "12:30",
    ("Saturday", "today"): "11:00",
    ("Sunday", "today"): "12:00",   # only used if a Sunday one-off exists
    # Teaser / reminder evening slot:
    ("Monday", "teaser"): "19:00",
    ("Tuesday", "teaser"): "19:00",
    ("Wednesday", "teaser"): "19:00",
    ("Thursday", "teaser"): "19:00",
    ("Friday", "teaser"): "19:00",
    ("Saturday", "teaser"): "21:00",
    ("Sunday", "teaser"): "19:00",
}
# If a (day, type) pair is missing, fall back to these.
DEFAULT_TIME_FALLBACK = {"today": "12:00", "teaser": "19:00", "reminder": "18:30"}

# Marks the timing source in code so we know when it becomes personalized.
TIMING_SOURCE = "default-fallback (not yet personalized to Backyard Brew's own data)"

# ---------------------------------------------------------------------------
# Campaign / reminder rhythms for one-off events with a promote_from date.
# Each number is "days before the event" to drop a reminder post. The day-before
# (1) and day-of (0) are handled by the normal teaser/today posts, so the
# campaign list only covers the earlier build-up milestones.
# ---------------------------------------------------------------------------
CAMPAIGN_RHYTHMS = {
    "standard": [14, 7, 3],      # ~2 wks, ~1 wk, ~3 days out (default)
    "light": [7],                # just a week out
    "heavy": [21, 14, 7, 3],     # 3 wks all the way in
}
DEFAULT_CAMPAIGN_RHYTHM = "standard"

# ---------------------------------------------------------------------------
# Platform export dimensions (width, height) for processed images.
# ---------------------------------------------------------------------------
DIMENSIONS = {
    "ig_feed": (1080, 1080),
    "ig_story": (1080, 1920),
    "fb_feed": (1200, 630),
    "fb_cover": (1920, 1005),
    "flyer": (1080, 1080),
}

# ---------------------------------------------------------------------------
# Valid values for the status column, documented for the owner.
# pending      -> owner just added a one-off; Sunday job will process it
# needs_review -> system generated it; owner should review/approve
# approved     -> owner OK'd it; hourly job will post when its time passes
# skip         -> suppress this post entirely
# posted       -> already published (set by the system)
# campaign_source -> a promote_from row that was expanded into reminders; ignore
# ---------------------------------------------------------------------------
STATUS_PENDING = "pending"
STATUS_NEEDS_REVIEW = "needs_review"
STATUS_APPROVED = "approved"
STATUS_SKIP = "skip"
STATUS_POSTED = "posted"
STATUS_CAMPAIGN_SOURCE = "campaign_source"

# The exact column order for posts.csv. Keep in sync with the header row.
POSTS_COLUMNS = [
    "date", "time", "photos", "event", "key_details", "platforms",
    "promote_from", "post_type", "enhance", "fb_caption", "ig_caption",
    "scheduled_time", "status",
]

# Long-lived Meta tokens last ~60 days. Warn when fewer than this many days
# are estimated to remain so the owner refreshes before it expires.
TOKEN_WARN_DAYS = 10

# ---------------------------------------------------------------------------
# Extra post types (carousel / vibe / spotlight) -- opportunistic, capped.
# ---------------------------------------------------------------------------
EXTRA_POST_TYPES = ("carousel", "vibe", "spotlight")
MAX_EXTRA_POSTS_PER_DAY = 1     # per platform, on top of today/teaser -- hard cap
MAX_EXTRA_POSTS_PER_WEEK = 4    # ceiling, not a quota
EXTRA_POST_TIME_EVENING = "19:30"
EXTRA_POST_TIME_MORNING = "11:30"


def pick_hashtags(seed: int, count: int = 6) -> str:
    """Return a rotating, deterministic hashtag string for the IG first comment.

    Always includes #BackyardBrew, then rotates through the rest of the pool so
    the same exact set never repeats week to week. `seed` should be something
    stable per-post (e.g. a hash of the date+event) so re-runs are consistent.
    """
    rest = [h for h in HASHTAG_POOL if h != HASHTAG_ALWAYS]
    if count < 1:
        count = 1
    n = min(count - 1, len(rest))
    start = seed % len(rest)
    rotated = [rest[(start + i) % len(rest)] for i in range(n)]
    return " ".join([HASHTAG_ALWAYS] + rotated)
