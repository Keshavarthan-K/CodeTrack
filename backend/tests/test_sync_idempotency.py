"""
Spec section 43, Case 5: running the same sync twice must not create
duplicate Problem or SolvedProblem rows.

Also exercises the DB-level defense (uq_user_problem / uq_platform_problem)
that's supposed to back up the application-level dedup.
"""

from datetime import datetime, UTC

import pytest
from sqlalchemy.exc import IntegrityError

from app.database.models import Problem, SolvedProblem
from app.services.sync_service import sync_platform


def _problem_data(pid="1-A", when=None):
    return {
        "platform": "codeforces",
        "platform_problem_id": pid,
        "contest_id": 1,
        "index": "A",
        "title": "Theatre Square",
        "rating": 1000,
        "difficulty": "Easy",
        "tags": ["math"],
        "language": "GNU C++20",
        "first_solved_at": when or datetime(2026, 8, 1, tzinfo=UTC),
    }


def test_sync_is_idempotent(db_session, user):
    solved = [_problem_data("1-A"), _problem_data("1-B")]

    first = sync_platform(db_session, user, solved)
    assert first == {"new_problems": 2, "new_solves": 2}

    second = sync_platform(db_session, user, solved)
    assert second == {"new_problems": 0, "new_solves": 0}

    assert db_session.query(Problem).count() == 2
    assert db_session.query(SolvedProblem).count() == 2


def test_second_sync_only_adds_genuinely_new_problems(db_session, user):
    sync_platform(db_session, user, [_problem_data("1-A")])
    stats = sync_platform(db_session, user, [_problem_data("1-A"), _problem_data("1-B")])

    assert stats == {"new_problems": 1, "new_solves": 1}
    assert db_session.query(SolvedProblem).count() == 2


def test_db_rejects_duplicate_user_problem_pair(db_session, user):
    problem = Problem(
        platform="codeforces",
        platform_problem_id="1-A",
        title="Theatre Square",
        difficulty="Easy",
        rating=1000,
        url="https://codeforces.com/problemset/problem/1/A",
    )
    db_session.add(problem)
    db_session.flush()

    db_session.add(SolvedProblem(user_id=user.id, problem_id=problem.id,
                                  first_solved_at=datetime(2026, 8, 1, tzinfo=UTC)))
    db_session.commit()

    # Same user + same problem again -> must violate uq_user_problem
    db_session.add(SolvedProblem(user_id=user.id, problem_id=problem.id,
                                  first_solved_at=datetime(2026, 8, 2, tzinfo=UTC)))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_db_rejects_duplicate_platform_problem_pair(db_session):
    p1 = Problem(platform="codeforces", platform_problem_id="1-A", title="A",
                 difficulty="Easy", rating=800, url="u1")
    db_session.add(p1)
    db_session.commit()

    p2 = Problem(platform="codeforces", platform_problem_id="1-A", title="A duplicate",
                 difficulty="Easy", rating=800, url="u2")
    db_session.add(p2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
