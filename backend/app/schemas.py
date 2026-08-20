"""
Pydantic response models for the API.

Keeping these separate from the SQLAlchemy models (app/database/models.py)
so the HTTP contract can evolve independently of the DB schema, and so
FastAPI gets automatic validation + OpenAPI docs for free.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DailyCount(BaseModel):
    date: str  # "YYYY-MM-DD"
    count: int


class MonthlyCount(BaseModel):
    month: str  # "YYYY-MM"
    count: int


class YearlyCount(BaseModel):
    year: str  # "YYYY"
    count: int


class RatingBucket(BaseModel):
    rating: int
    count: int


class PlatformCounts(BaseModel):
    codeforces: int = 0
    leetcode: int = 0
    codechef: int = 0


class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int


class DashboardResponse(BaseModel):
    total_solved: int
    today: int
    this_week: int
    this_month: int
    this_year: int
    current_streak: int
    longest_streak: int
    platforms: dict[str, int]


class ProblemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    platform: str
    platform_problem_id: str
    title: str
    difficulty: str | None
    rating: int | None
    url: str


class SolvedProblemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_solved_at: datetime
    language: str | None
    problem: ProblemOut


class SyncResult(BaseModel):
    platform: str
    fetched_submissions: int
    unique_solved: int
    new_problems: int
    new_solves: int
