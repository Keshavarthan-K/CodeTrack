from datetime import UTC, datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100))

    # NOTE: nullable + no unique=True on the optional platform usernames.
    # The original schema had unique=True here, which broke the moment a
    # second user left leetcode_username/codechef_username blank (two
    # empty strings collide under a unique constraint). Only
    # codeforces_username is guaranteed non-blank right now, so it's the
    # only one that stays unique.
    leetcode_username: Mapped[str | None] = mapped_column(String(100), nullable=True)

    codeforces_username: Mapped[str] = mapped_column(String(100), unique=True)

    codechef_username: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    solved_problems: Mapped[List["SolvedProblem"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    rating_history: Mapped[List["RatingHistory"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    sync_states: Mapped[List["SyncState"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Problem(Base):
    __tablename__ = "problems"

    __table_args__ = (
        UniqueConstraint(
            "platform",
            "platform_problem_id",
            name="uq_platform_problem",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    platform: Mapped[str] = mapped_column(String(20))

    platform_problem_id: Mapped[str] = mapped_column(String(50))

    title: Mapped[str] = mapped_column(String(255))

    difficulty: Mapped[str | None] = mapped_column(String(20), nullable=True)

    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)

    url: Mapped[str] = mapped_column(String(500))

    solved_by: Mapped[List["SolvedProblem"]] = relationship(
        back_populates="problem",
        cascade="all, delete-orphan",
    )


class SolvedProblem(Base):
    __tablename__ = "solved_problems"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "problem_id",
            name="uq_user_problem",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"))

    first_solved_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
    )

    language: Mapped[str | None] = mapped_column(String(50), nullable=True)

    user: Mapped["User"] = relationship(back_populates="solved_problems")

    problem: Mapped["Problem"] = relationship(back_populates="solved_by")


class RatingHistory(Base):
    """
    One row per rating change (usually one per rated contest). See
    spec section 38. Powers the Codeforces/LeetCode/CodeChef rating
    graphs.
    """

    __tablename__ = "rating_history"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "platform",
            "contest_id",
            name="uq_user_platform_contest",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    platform: Mapped[str] = mapped_column(String(20))

    contest_id: Mapped[str] = mapped_column(String(50))

    contest_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    rating: Mapped[int] = mapped_column(Integer)

    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

    timestamp: Mapped[datetime] = mapped_column(DateTime)

    user: Mapped["User"] = relationship(back_populates="rating_history")


class SyncState(Base):
    """
    Tracks sync progress per user+platform so the daily scheduler can
    fetch/process only what's new instead of re-walking full history
    every run (spec section 40, "Incremental Sync"). Correctness must
    never depend on this table - it's purely an optimization, and the
    (user_id, problem_id) / (platform, platform_problem_id) unique
    constraints above are what actually guarantee no duplicates even
    if this bookkeeping is wrong or stale.
    """

    __tablename__ = "sync_states"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "platform",
            name="uq_user_platform_sync_state",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    platform: Mapped[str] = mapped_column(String(20))

    # Highest Codeforces submission id seen so far (CF submission ids
    # are monotonically increasing). Other platforms can store their
    # own cursor concept here as a string if needed.
    last_submission_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    last_sync_status: Mapped[str | None] = mapped_column(String(20), nullable=True)

    last_error: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user: Mapped["User"] = relationship(back_populates="sync_states")
