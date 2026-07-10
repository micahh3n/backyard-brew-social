"""
scheduling.py - Pure fill-target math for the guaranteed daily posting
cadence (config.MIN_DAILY_POSTS minimum, occasional bonus up to
config.MAX_DAILY_POSTS). No I/O, no side effects -- generate_captions.py's
build_extra_rows() consumes this to decide how many fill posts each day of
the upcoming week needs and where to slot them in time.
"""

from __future__ import annotations

import config


def compute_fill_targets(counts: dict, week_dates: list,
                         min_posts: int = None, max_posts: int = None,
                         bonus_budget: int = None) -> dict:
    """Return {date: extra_posts_needed} for every date in week_dates.

    First pass: top up any day below min_posts (using its existing baseline
    count from `counts`) to exactly min_posts.
    Second pass: spend bonus_budget bonus slots on the days with the most
    remaining headroom below max_posts, earliest date breaking ties, so a
    handful of days occasionally get a 3rd post instead of every day.
    """
    min_posts = config.MIN_DAILY_POSTS if min_posts is None else min_posts
    max_posts = config.MAX_DAILY_POSTS if max_posts is None else max_posts
    bonus_budget = config.BONUS_POSTS_PER_WEEK if bonus_budget is None else bonus_budget

    targets = {}
    for d in week_dates:
        baseline = counts.get(d, 0)
        targets[d] = max(0, min(min_posts, max_posts) - baseline)

    def headroom(d):
        filled = counts.get(d, 0) + targets[d]
        return max_posts - filled

    remaining_budget = bonus_budget
    while remaining_budget > 0:
        eligible = [d for d in week_dates if headroom(d) > 0]
        if not eligible:
            break
        eligible.sort(key=lambda d: (-headroom(d), week_dates.index(d)))
        chosen = eligible[0]
        targets[chosen] += 1
        remaining_budget -= 1

    return targets


def time_for_fill_slot(index: int) -> str:
    """Clock time for the Nth (0-indexed) fill post scheduled on one day.

    Afternoon first -- that's the documented "occasional 3rd post" slot --
    then morning, then evening, repeating if a single day somehow needs more
    than three (never happens under config.MAX_DAILY_POSTS, but keeps this
    function total rather than partial).
    """
    slots = [config.EXTRA_POST_TIME_AFTERNOON, config.EXTRA_POST_TIME_MORNING,
             config.EXTRA_POST_TIME_EVENING]
    return slots[index % len(slots)]
