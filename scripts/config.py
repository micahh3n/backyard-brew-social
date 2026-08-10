"""
config.py - Single source of truth for Backyard Brew's brand, timing, and rules.

Everything brand-specific lives here so the logic files stay clean. If the bar's
schedule or colors change, this is usually the only file to edit -- voice/hashtag
rules live in the backyard-brew-brand skill, since Claude Code writes captions
directly now rather than through an API call.
"""

from __future__ import annotations

import os
from zoneinfo import ZoneInfo

try:
    # Registers .heic/.heif support with PIL's Image.open() globally, for
    # every script in this repo -- iPhones (the owner's photo source) shoot
    # HEIC by default. Import config first (every script already does) and
    # every later `Image.open()` call transparently handles HEIC too.
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:  # library not installed yet (e.g. local dry run)
    pass

# ---------------------------------------------------------------------------
# Paths (resolved relative to the repo root, which is the parent of /scripts)
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTOS_DIR = os.path.join(REPO_ROOT, "photos")
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")
LOGO_DIR = os.path.join(ASSETS_DIR, "logo")
RECURRING_CSV = os.path.join(REPO_ROOT, "recurring_events.csv")
POSTS_CSV = os.path.join(REPO_ROOT, "posts.csv")
STATUS_LOG = os.path.join(REPO_ROOT, "status.log")
# Where process_photos.py writes finished images for manual review/posting
# (rendered for the weekly preview page, not auto-posted).
GENERATED_DIR = os.path.join(REPO_ROOT, "photos", "_generated")

# ---------------------------------------------------------------------------
# Timezone -- everything schedules in Central time (Wisconsin).
# ---------------------------------------------------------------------------
TIMEZONE = ZoneInfo("America/Chicago")

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
}

HOURS = {
    "Monday": "4pm-9pm",
    "Tuesday": "4pm-9pm",
    "Wednesday": "4pm-9pm",
    "Thursday": "4pm-9pm",
    "Friday": "4pm-12am",
    "Saturday": "11am-12am",
    "Sunday": "11am-7pm-ish",
}

MEMBERSHIPS = (
    "Course Membership $150/yr: unlimited disc golf, hiking & snowshoeing, "
    "free tap beer every month, free personal pitcher on your birthday. "
    "Beer Club $200/yr: $2 off your first beer every day, $1 off all night at "
    "parties, free tap beer every month, personal pitcher on your birthday."
)

# Food facts captions must not get wrong (confirmed 2026-07-31).
# The pizzas are CARRIED from two separate local pizza companies. They are not
# hand-made, house-made, or from scratch, and Renard's/Jolly Bob's are not
# ingredient suppliers - they are the pizza makers.
PIZZA = "12 inch pizzas from Renard's and Jolly Bob's"

# Breakfast service ended 2026-07-26. Never mention breakfast.
BREAKFAST_SERVED = False

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
# Per-day content angle -- baked into the caption prompt per event so each
# night has its own hook, not a generic "come on in".
# ---------------------------------------------------------------------------
EVENT_ANGLES = {
    "Bingo Night": "Prize-reveal angle -- what are we playing for this week?",
    "Pickleball Open Play": "Challenge/competitive angle -- think you can beat the regulars?",
    "Tacos + Poker Club": "Food first, then the game -- the tacos are the hook.",
    "Backyard Market & Brews": "Community and local-business-first angle, above everything else -- this is a "
        "small-business showcase, not a party night. Center the vendors and musician as real people/local "
        "businesses worth supporting, not just 'stuff to look at.' FOMO on the weekly-rotating vendor + musician "
        "lineup -- 'you never know who'll be out,' never 'gone forever' (vendors do repeat). Never plug disc "
        "golf/hiking/pickleball as part of THIS event's core pitch -- those are separate draws. Don't tie in "
        "taco night (not reconfirmed as running alongside). CTAs: vendor/musician signup (DM or "
        "crew@backyard-brew.com), 'bring cash, bring friends, bring the leashed pup.' Avoid 'Thursdays are for "
        "the backyard' / 'See you in the backyard' and overly polished ad language.",
    "Karaoke Night": "'Weekend starts NOW' energy.",
    "Pool Night": "Tournament angle -- beat the bartender, win a flight.",
    "Packers Sundays": "SEASONAL (Sept-Jan only). Backyard-tailgate angle, not sports-bar angle -- a round on "
        "the course before kickoff, the game outside, Wisconsin taps, tailgate food. Packers references welcome. "
        "Kickoff time is NEVER fixed -- confirm that week's real time with the owner before naming one in a post; "
        "if unconfirmed, write around 'gameday'/'kickoff' with no specific time rather than guessing.",
    "Wisconsin Spotlight": "Feature the specific drink named in key_details -- pure appreciation, no CTA pressure.",
    "Course & Trail Feature": "Feature the specific trail/course detail named in key_details -- outdoorsy pride angle.",
    "Weather Vibes": "Tie the specific weather named in key_details to disc golf/hiking/patio appeal.",
}

# ---------------------------------------------------------------------------
# Default fallback posting schedule (used until real Insights data takes over).
# Times are 24h local. Keyed by (day_of_week, post_type). "today" = event day,
# "teaser" = the evening-before anticipation post. Reminder posts in a campaign
# reuse the "teaser" evening slot on their own day.
# ---------------------------------------------------------------------------
DEFAULT_TIMES = {
    ("Monday", "today"): "11:00",
    ("Tuesday", "today"): "11:00",
    ("Wednesday", "today"): "11:00",
    ("Thursday", "today"): "11:00",
    ("Friday", "today"): "11:00",
    ("Saturday", "today"): "11:00",
    ("Sunday", "today"): "11:00",   # only used if a Sunday one-off exists
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
# needs_review -> system generated it; owner should review/edit it
# skip         -> suppress this post entirely
# scheduled    -> owner manually pasted this into FB/IG's native scheduler
#                 (bookkeeping only -- nothing in the system reads this back)
# posted       -> legacy value from the old auto-posting job; still
#                 recognized as "already used" history, nothing sets it now
# campaign_source -> a promote_from row that was expanded into reminders; ignore
# ---------------------------------------------------------------------------
STATUS_PENDING = "pending"
STATUS_NEEDS_REVIEW = "needs_review"
STATUS_SKIP = "skip"
STATUS_SCHEDULED = "scheduled"
STATUS_POSTED = "posted"
STATUS_CAMPAIGN_SOURCE = "campaign_source"

# The exact column order for posts.csv. Keep in sync with the header row.
POSTS_COLUMNS = [
    "date", "time", "photos", "event", "key_details", "platforms",
    "promote_from", "post_type", "enhance", "fb_caption", "ig_caption",
    "scheduled_time", "generated_image", "status",
]

# ---------------------------------------------------------------------------
# Undated event/food photo pools. A photo whose filename contains one of
# these keywords (case-insensitive substring, anywhere) automatically enters
# that event's rotation instead of the system always falling back to the
# same static default poster. See generate_captions._pick_pool_photo().
# ---------------------------------------------------------------------------
EVENT_PHOTO_KEYWORDS = {
    "Bingo Night": ["bingo"],
    "Pickleball Open Play": ["pickleball"],
    "Tacos + Poker Club": ["poker"],
    "Backyard Market & Brews": ["market", "vendor", "marketbrews"],
    "Karaoke Night": ["karaoke"],
    "Pool Night": ["pool"],
    # Seasonal (Sept-Jan) -- see EVENT_ANGLES and recurring_events.csv for
    # the kickoff-time-is-never-fixed rule. Any candid tagged with one of
    # these keywords enters rotation the same as the other events.
    "Packers Sundays": ["packers", "football", "tailgate", "gameday"],
}

# Food photos attach as a SECOND photo on the mapped event's "today" post
# (never replacing the main event photo, never on teasers). "pizza" is
# served every day at the bar, so unlike the others it maps to every event
# but only actually attaches on one rotating day per week -- see
# OCCASIONAL_FOOD_KEYWORDS and generate_captions.find_food_photo().
# Sunday included for Packers Sundays (seasonal, Sept-Jan) -- tailgate food
# fits the same pizza rotation the other six days already use.
RECURRING_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

FOOD_PHOTO_KEYWORDS = {
    "hotdog": ["Bingo Night", "Pickleball Open Play"],
    "taco": ["Tacos + Poker Club"],
    "nachos": ["Tacos + Poker Club"],
    "quesadilla": ["Tacos + Poker Club"],
    "pizza": list(EVENT_PHOTO_KEYWORDS.keys()),
}

OCCASIONAL_FOOD_KEYWORDS = {"pizza"}
