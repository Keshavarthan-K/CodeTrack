from sqlalchemy import String, DateTime, Integer, UniqueConstraint
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)
from datetime import datetime,UTC
from typing import List
from .database import Base


class User(Base):
    __tablename__ = "users"


    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100))

    leetcode_username: Mapped[str] = mapped_column(String(100), unique=True)

    codeforces_username: Mapped[str] = mapped_column(String(100), unique=True)

    codechef_username: Mapped[str] = mapped_column(String(100), unique=True)

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    solved_problems: Mapped[List["SolvedProblem"]] = relationship(
    back_populates="user",
    cascade="all, delete-orphan"
)

from sqlalchemy import Integer

class Problem(Base):
    __tablename__ = "problems"

    __table_args__ = (
    UniqueConstraint(
        "platform",
        "platform_problem_id",
        name="uq_platform_problem"
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
    cascade="all, delete-orphan"
)

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class SolvedProblem(Base):
    __tablename__ = "solved_problems"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "problem_id",
            name="uq_user_problem"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    problem_id: Mapped[int] = mapped_column(
        ForeignKey("problems.id")
    )

    first_solved_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC)
    )

    language: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    user: Mapped["User"] = relationship(
    back_populates="solved_problems"
)

    problem: Mapped["Problem"] = relationship(
    back_populates="solved_by"
)