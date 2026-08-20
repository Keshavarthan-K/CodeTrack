from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.dependencies import get_current_user
from app.repositories import rating_repository
from app.services import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/daily")
def daily(
    days: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Daily new-solve counts, derived from first_solved_at.
    Pass ?days=30 to limit to the trailing 30 days; omit for all-time.
    """
    return analytics_service.get_daily_counts(db, user.id, days=days)


@router.get("/monthly")
def monthly(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return analytics_service.get_monthly_counts(db, user.id)


@router.get("/yearly")
def yearly(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return analytics_service.get_yearly_counts(db, user.id)


@router.get("/platforms")
def platforms(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return analytics_service.get_platform_counts(db, user.id)


@router.get("/difficulty")
def difficulty(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return analytics_service.get_difficulty_counts(db, user.id)


@router.get("/rating-distribution")
def rating_distribution(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return analytics_service.get_rating_distribution(db, user.id)


@router.get("/streak")
def streak(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return analytics_service.get_streaks(db, user.id)


@router.get("/heatmap")
def heatmap(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Date -> count for every day with at least one first-solve. Powers a GitHub-style heatmap."""
    return analytics_service.get_calendar_heatmap(db, user.id)


@router.get("/rating-history")
def rating_history(
    platform: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Time series of rating points, e.g. for a Codeforces rating graph. Optionally filter by platform."""
    rows = rating_repository.list_rating_history(db, user.id, platform=platform)
    return [
        {
            "platform": r.platform,
            "contest_id": r.contest_id,
            "contest_name": r.contest_name,
            "rating": r.rating,
            "rank": r.rank,
            "timestamp": r.timestamp.isoformat(),
        }
        for r in rows
    ]
