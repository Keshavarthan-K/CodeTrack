"""
Spec section 31 example:

    Aug 1 -> 2 solves
    Aug 2 -> 1
    Aug 3 -> 3
    Aug 4 -> 0
    Aug 5 -> 2

    Longest = 3
    Current = 1   (only true if "today" is Aug 5)
"""

from datetime import date

from app.services.analytics_service import compute_current_streak, compute_longest_streak


def test_longest_streak_matches_spec_example():
    dates = [date(2026, 8, 1), date(2026, 8, 2), date(2026, 8, 3), date(2026, 8, 5)]
    assert compute_longest_streak(dates) == 3


def test_current_streak_when_today_extends_it():
    dates = [date(2026, 8, 1), date(2026, 8, 2), date(2026, 8, 3), date(2026, 8, 5)]
    assert compute_current_streak(dates, today=date(2026, 8, 5)) == 1


def test_current_streak_is_zero_after_a_gap():
    dates = [date(2026, 8, 1), date(2026, 8, 2), date(2026, 8, 3)]
    # today is Aug 6: nothing solved on Aug 5 or Aug 6 -> streak broken
    assert compute_current_streak(dates, today=date(2026, 8, 6)) == 0


def test_current_streak_counts_yesterday_if_today_not_yet_solved():
    dates = [date(2026, 8, 1), date(2026, 8, 2), date(2026, 8, 3)]
    # today is Aug 4, nothing solved yet today, but Aug 3 keeps it alive
    assert compute_current_streak(dates, today=date(2026, 8, 4)) == 3


def test_empty_dates_gives_zero_streaks():
    assert compute_longest_streak([]) == 0
    assert compute_current_streak([], today=date(2026, 8, 4)) == 0
