import config
import scheduling


def test_compute_fill_targets_fills_empty_days_to_minimum():
    week_dates = ["2026-06-01", "2026-06-02", "2026-06-03"]
    counts = {}
    targets = scheduling.compute_fill_targets(counts, week_dates, min_posts=2,
                                              max_posts=3, bonus_budget=0)
    assert targets == {"2026-06-01": 2, "2026-06-02": 2, "2026-06-03": 2}


def test_compute_fill_targets_only_tops_up_short_days():
    week_dates = ["2026-06-01", "2026-06-02"]
    counts = {"2026-06-01": 2, "2026-06-02": 1}
    targets = scheduling.compute_fill_targets(counts, week_dates, min_posts=2,
                                              max_posts=3, bonus_budget=0)
    assert targets == {"2026-06-01": 0, "2026-06-02": 1}


def test_compute_fill_targets_never_exceeds_max_posts_via_bonus():
    week_dates = ["2026-06-01", "2026-06-02"]
    counts = {"2026-06-01": 2, "2026-06-02": 2}
    targets = scheduling.compute_fill_targets(counts, week_dates, min_posts=2,
                                              max_posts=3, bonus_budget=5)
    # Only 1 bonus slot exists per day (2 -> 3), even though budget is 5.
    assert targets == {"2026-06-01": 1, "2026-06-02": 1}


def test_compute_fill_targets_spends_bonus_budget_on_most_headroom_first():
    week_dates = ["2026-06-01", "2026-06-02", "2026-06-03"]
    counts = {"2026-06-01": 2, "2026-06-02": 2, "2026-06-03": 2}
    targets = scheduling.compute_fill_targets(counts, week_dates, min_posts=2,
                                              max_posts=3, bonus_budget=1)
    assert sum(targets.values()) == 1
    assert targets["2026-06-01"] == 1  # earliest date wins the tiebreak


def test_compute_fill_targets_uses_config_defaults_when_not_overridden():
    week_dates = ["2026-06-01"]
    targets = scheduling.compute_fill_targets({}, week_dates, bonus_budget=0)
    assert targets["2026-06-01"] == config.MIN_DAILY_POSTS


def test_time_for_fill_slot_rotates_afternoon_first():
    assert scheduling.time_for_fill_slot(0) == config.EXTRA_POST_TIME_AFTERNOON
    assert scheduling.time_for_fill_slot(1) == config.EXTRA_POST_TIME_MORNING
    assert scheduling.time_for_fill_slot(2) == config.EXTRA_POST_TIME_EVENING
    assert scheduling.time_for_fill_slot(3) == config.EXTRA_POST_TIME_AFTERNOON
