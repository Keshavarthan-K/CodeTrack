"""
Spec section 43, Cases 2-4: a re-accepted submission of an
already-solved problem must never inflate a later day/month/year's
count. Everything must be derived from first_solved_at, which is
exactly what analytics_repository/service do - these tests just
confirm it holds across day/month/year boundaries.
"""

from datetime import datetime, UTC

from app.database.models import Problem, SolvedProblem
from app.repositories import analytics_repository as repo


def _add_problem(db, pid="1-A", platform="codeforces"):
    p = Problem(
        platform=platform,
        platform_problem_id=pid,
        title="Problem A",
        difficulty="Easy",
        rating=800,
        url="https://codeforces.com/problemset/problem/1/A",
    )
    db.add(p)
    db.flush()
    return p


def _solve(db, user, problem, when: datetime):
    s = SolvedProblem(
        user_id=user.id,
        problem_id=problem.id,
        first_solved_at=when,
        language="C++",
    )
    db.add(s)
    db.commit()
    return s


# --- Case 2: cross-day ------------------------------------------------

def test_case2_cross_day(db_session, user):
    problem = _add_problem(db_session)
    # first_solved_at is fixed at Aug 1. A later Aug 2 "accepted again"
    # never creates a second SolvedProblem row (uq_user_problem in the
    # DB schema enforces this at the sync layer) - here we directly
    # assert the analytics read side: only Aug 1 gets credit.
    _solve(db_session, user, problem, datetime(2026, 8, 1, 10, 0, tzinfo=UTC))

    aug1 = repo.count_solved_in_range(
        db_session, user.id,
        datetime(2026, 8, 1, tzinfo=UTC), datetime(2026, 8, 2, tzinfo=UTC),
    )
    aug2 = repo.count_solved_in_range(
        db_session, user.id,
        datetime(2026, 8, 2, tzinfo=UTC), datetime(2026, 8, 3, tzinfo=UTC),
    )

    assert aug1 == 1
    assert aug2 == 0


# --- Case 3: cross-month -----------------------------------------------

def test_case3_cross_month(db_session, user):
    problem = _add_problem(db_session)
    _solve(db_session, user, problem, datetime(2026, 1, 31, 23, 0, tzinfo=UTC))

    monthly = {row["month"]: row["count"] for row in repo.monthly_counts(db_session, user.id)}

    assert monthly.get("2026-01") == 1
    assert monthly.get("2026-02", 0) == 0


# --- Case 4: cross-year -------------------------------------------------

def test_case4_cross_year(db_session, user):
    problem = _add_problem(db_session)
    _solve(db_session, user, problem, datetime(2025, 12, 31, 23, 0, tzinfo=UTC))

    yearly = {row["year"]: row["count"] for row in repo.yearly_counts(db_session, user.id)}

    assert yearly.get("2025") == 1
    assert yearly.get("2026", 0) == 0


def test_multiple_problems_solved_same_day_count_together(db_session, user):
    p1 = _add_problem(db_session, pid="1-A")
    p2 = _add_problem(db_session, pid="1-B")
    _solve(db_session, user, p1, datetime(2026, 8, 5, 9, 0, tzinfo=UTC))
    _solve(db_session, user, p2, datetime(2026, 8, 5, 15, 0, tzinfo=UTC))

    daily = {row["date"]: row["count"] for row in repo.daily_counts(db_session, user.id)}
    assert daily["2026-08-05"] == 2
