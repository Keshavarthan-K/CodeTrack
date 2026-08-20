"""
Analytics repository.

CRITICAL RULE (see project spec section 28):
Every query in this file must derive counts from
`SolvedProblem.first_solved_at`. Never from a submission timestamp,
and never from a count of Accepted submissions. `SolvedProblem` is
already a deduplicated "solve event" table (one row per user+problem,
enforced by the `uq_user_problem` unique constraint) - that dedup is
what makes these queries correct.

This file is the only place that writes raw SQLAlchemy queries for
analytics; services/analytics_service.py builds on top of these
primitives and adds business logic (date-range resolution, streaks).

Note: the strftime()-based grouping below is SQLite-specific (this
project currently only targets SQLite). If you ever move to Postgres,
swap strftime() for date_trunc()/EXTRACT().
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import Problem, SolvedProblem


def count_total_solved(db: Session, user_id: int) -> int:
    return (
        db.query(func.count(SolvedProblem.id))
        .filter(SolvedProblem.user_id == user_id)
        .scalar()
        or 0
    )


def count_solved_in_range(
    db: Session,
    user_id: int,
    start: datetime,
    end: datetime,
) -> int:
    """
    Counts solve events whose first_solved_at falls in the half-open
    interval [start, end). Both bounds are expected to already be in
    UTC, matching how first_solved_at is stored.
    """
    return (
        db.query(func.count(SolvedProblem.id))
        .filter(
            SolvedProblem.user_id == user_id,
            SolvedProblem.first_solved_at >= start,
            SolvedProblem.first_solved_at < end,
        )
        .scalar()
        or 0
    )


def solved_dates(db: Session, user_id: int) -> list[date]:
    """
    Every distinct UTC calendar date on which the user recorded at
    least one *first* solve. Powers streaks and the calendar heatmap.
    One date appears once no matter how many problems were first
    solved that day.
    """
    rows = (
        db.query(func.strftime("%Y-%m-%d", SolvedProblem.first_solved_at))
        .filter(SolvedProblem.user_id == user_id)
        .distinct()
        .all()
    )
    return sorted(datetime.strptime(r[0], "%Y-%m-%d").date() for r in rows)


def daily_counts(
    db: Session,
    user_id: int,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> list[dict]:
    query = db.query(
        func.strftime("%Y-%m-%d", SolvedProblem.first_solved_at).label("day"),
        func.count(SolvedProblem.id).label("count"),
    ).filter(SolvedProblem.user_id == user_id)

    if start is not None:
        query = query.filter(SolvedProblem.first_solved_at >= start)
    if end is not None:
        query = query.filter(SolvedProblem.first_solved_at < end)

    rows = query.group_by("day").order_by("day").all()
    return [{"date": row.day, "count": row.count} for row in rows]


def monthly_counts(
    db: Session,
    user_id: int,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> list[dict]:
    query = db.query(
        func.strftime("%Y-%m", SolvedProblem.first_solved_at).label("month"),
        func.count(SolvedProblem.id).label("count"),
    ).filter(SolvedProblem.user_id == user_id)

    if start is not None:
        query = query.filter(SolvedProblem.first_solved_at >= start)
    if end is not None:
        query = query.filter(SolvedProblem.first_solved_at < end)

    rows = query.group_by("month").order_by("month").all()
    return [{"month": row.month, "count": row.count} for row in rows]


def yearly_counts(
    db: Session,
    user_id: int,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> list[dict]:
    query = db.query(
        func.strftime("%Y", SolvedProblem.first_solved_at).label("year"),
        func.count(SolvedProblem.id).label("count"),
    ).filter(SolvedProblem.user_id == user_id)

    if start is not None:
        query = query.filter(SolvedProblem.first_solved_at >= start)
    if end is not None:
        query = query.filter(SolvedProblem.first_solved_at < end)

    rows = query.group_by("year").order_by("year").all()
    return [{"year": row.year, "count": row.count} for row in rows]


def platform_counts(db: Session, user_id: int) -> dict[str, int]:
    rows = (
        db.query(Problem.platform, func.count(SolvedProblem.id))
        .join(SolvedProblem, SolvedProblem.problem_id == Problem.id)
        .filter(SolvedProblem.user_id == user_id)
        .group_by(Problem.platform)
        .all()
    )
    return {platform: count for platform, count in rows}


def difficulty_counts(db: Session, user_id: int) -> dict[str, int]:
    rows = (
        db.query(Problem.difficulty, func.count(SolvedProblem.id))
        .join(SolvedProblem, SolvedProblem.problem_id == Problem.id)
        .filter(SolvedProblem.user_id == user_id)
        .group_by(Problem.difficulty)
        .all()
    )
    return {(difficulty or "Unrated"): count for difficulty, count in rows}


def rating_wise_counts(db: Session, user_id: int) -> list[dict]:
    """Solved-problem count bucketed by CF-style rating, for a distribution chart."""
    rows = (
        db.query(Problem.rating, func.count(SolvedProblem.id))
        .join(SolvedProblem, SolvedProblem.problem_id == Problem.id)
        .filter(SolvedProblem.user_id == user_id, Problem.rating.isnot(None))
        .group_by(Problem.rating)
        .order_by(Problem.rating)
        .all()
    )
    return [{"rating": rating, "count": count} for rating, count in rows]
