"""
Analytics service.

Resolves "today" / "this week" / "this month" / "this year" into
concrete UTC datetime ranges (in the configured APP_TIMEZONE), then
delegates the actual counting to app.repositories.analytics_repository,
which is the only place allowed to touch first_solved_at directly.

Also owns streak calculation, which is pure Python logic over the
distinct set of solve dates.
"""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.config import settings
from app.repositories import analytics_repository as repo

TZ = ZoneInfo(settings.APP_TIMEZONE)


# ---------------------------------------------------------------------
# Date-range helpers
# ---------------------------------------------------------------------

def _now_local() -> datetime:
    return datetime.now(TZ)


def _local_midnight(d: date) -> datetime:
    return datetime(d.year, d.month, d.day, tzinfo=TZ)


def today_range() -> tuple[datetime, datetime]:
    now = _now_local()
    start = _local_midnight(now.date())
    end = start + timedelta(days=1)
    return start, end


def this_week_range() -> tuple[datetime, datetime]:
    """Week starts Monday, matching ISO weekday conventions."""
    now = _now_local()
    start = _local_midnight(now.date() - timedelta(days=now.weekday()))
    end = start + timedelta(days=7)
    return start, end


def this_month_range() -> tuple[datetime, datetime]:
    now = _now_local()
    start = _local_midnight(now.date().replace(day=1))
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    return start, end


def this_year_range() -> tuple[datetime, datetime]:
    now = _now_local()
    start = _local_midnight(date(now.year, 1, 1))
    end = start.replace(year=start.year + 1)
    return start, end


# ---------------------------------------------------------------------
# Core stats
# ---------------------------------------------------------------------

def get_total_solved(db: Session, user_id: int) -> int:
    return repo.count_total_solved(db, user_id)


def get_today_count(db: Session, user_id: int) -> int:
    start, end = today_range()
    return repo.count_solved_in_range(db, user_id, start, end)


def get_this_week_count(db: Session, user_id: int) -> int:
    start, end = this_week_range()
    return repo.count_solved_in_range(db, user_id, start, end)


def get_this_month_count(db: Session, user_id: int) -> int:
    start, end = this_month_range()
    return repo.count_solved_in_range(db, user_id, start, end)


def get_this_year_count(db: Session, user_id: int) -> int:
    start, end = this_year_range()
    return repo.count_solved_in_range(db, user_id, start, end)


def get_daily_counts(db: Session, user_id: int, days: int | None = None) -> list[dict]:
    """
    Note: grouping is by UTC calendar day (see analytics_repository
    docstring), while today/week/month/year totals above are resolved
    in APP_TIMEZONE. For APP_TIMEZONE=UTC (the default) these agree
    exactly; for other timezones the daily *breakdown* buckets by UTC
    day while the *summary* numbers use local day boundaries.
    """
    start = None
    if days is not None:
        start = datetime.now(TZ).astimezone(ZoneInfo("UTC")) - timedelta(days=days)
    return repo.daily_counts(db, user_id, start=start)


def get_monthly_counts(db: Session, user_id: int) -> list[dict]:
    return repo.monthly_counts(db, user_id)


def get_yearly_counts(db: Session, user_id: int) -> list[dict]:
    return repo.yearly_counts(db, user_id)


def get_platform_counts(db: Session, user_id: int) -> dict[str, int]:
    return repo.platform_counts(db, user_id)


def get_difficulty_counts(db: Session, user_id: int) -> dict[str, int]:
    return repo.difficulty_counts(db, user_id)


def get_rating_distribution(db: Session, user_id: int) -> list[dict]:
    return repo.rating_wise_counts(db, user_id)


# ---------------------------------------------------------------------
# Streaks
# ---------------------------------------------------------------------

def compute_longest_streak(dates: list[date]) -> int:
    """Longest run of consecutive calendar dates in a sorted, deduped date list."""
    if not dates:
        return 0

    longest = 1
    current = 1

    for prev, curr in zip(dates, dates[1:]):
        if curr == prev + timedelta(days=1):
            current += 1
            longest = max(longest, current)
        elif curr == prev:
            # Shouldn't happen (dates are distinct), but guard anyway.
            continue
        else:
            current = 1

    return longest


def compute_current_streak(dates: list[date], today: date) -> int:
    """
    Number of consecutive days, counting back from today (or from
    yesterday if nothing was solved yet today), where at least one
    new problem was first-solved. Returns 0 if the chain is already
    broken (i.e. nothing solved today or yesterday).
    """
    if not dates:
        return 0

    date_set = set(dates)

    if today in date_set:
        cursor = today
    elif (today - timedelta(days=1)) in date_set:
        # Still "alive" - today just hasn't happened yet.
        cursor = today - timedelta(days=1)
    else:
        return 0

    streak = 0
    while cursor in date_set:
        streak += 1
        cursor -= timedelta(days=1)

    return streak


def get_streaks(db: Session, user_id: int) -> dict:
    dates = repo.solved_dates(db, user_id)
    today = _now_local().date()
    return {
        "current_streak": compute_current_streak(dates, today),
        "longest_streak": compute_longest_streak(dates),
    }


def get_calendar_heatmap(db: Session, user_id: int) -> list[dict]:
    """date -> count for every day with at least one solve. Powers a GitHub-style heatmap."""
    return repo.daily_counts(db, user_id)


# ---------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------

def get_dashboard(db: Session, user_id: int) -> dict:
    streaks = get_streaks(db, user_id)
    return {
        "total_solved": get_total_solved(db, user_id),
        "today": get_today_count(db, user_id),
        "this_week": get_this_week_count(db, user_id),
        "this_month": get_this_month_count(db, user_id),
        "this_year": get_this_year_count(db, user_id),
        "current_streak": streaks["current_streak"],
        "longest_streak": streaks["longest_streak"],
        "platforms": get_platform_counts(db, user_id),
    }
