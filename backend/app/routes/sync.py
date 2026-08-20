import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.dependencies import get_current_user
from app.fetchers.codeforces import fetch_submissions
from app.fetchers.leetcode import fetch_recent_accepted_submissions
from app.schemas import SyncResult
from app.services.rating_service import sync_codeforces_rating
from app.services.submission_processor import (
    extract_unique_solved_problems,
    extract_unique_solved_problems_leetcode,
)
from app.services.sync_service import sync_codeforces, sync_platform

logger = logging.getLogger("codetrack.sync")

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.post("/codeforces", response_model=SyncResult)
def sync_codeforces_route(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not user.codeforces_username:
        raise HTTPException(400, "No Codeforces username configured for this user.")

    try:
        submissions = fetch_submissions(user.codeforces_username)
    except Exception as exc:  # network errors, rate limits, bad handle, etc.
        logger.exception("Codeforces fetch failed")
        raise HTTPException(502, f"Failed to fetch Codeforces submissions: {exc}") from exc

    problems = extract_unique_solved_problems(submissions)
    stats = sync_codeforces(db, user, problems)

    return SyncResult(
        platform="codeforces",
        fetched_submissions=len(submissions),
        unique_solved=len(problems),
        new_problems=stats["new_problems"],
        new_solves=stats["new_solves"],
    )


@router.post("/codeforces/rating")
def sync_codeforces_rating_route(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not user.codeforces_username:
        raise HTTPException(400, "No Codeforces username configured for this user.")

    try:
        return sync_codeforces_rating(db, user)
    except Exception as exc:
        logger.exception("Codeforces rating sync failed")
        raise HTTPException(502, f"Failed to sync Codeforces rating: {exc}") from exc


@router.post("/leetcode", response_model=SyncResult)
def sync_leetcode_route(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Syncs recent LeetCode solves (last ~20 accepted submissions only -
    see app/fetchers/leetcode.py for why). Safe to call repeatedly /
    on a schedule; it will never duplicate a problem you've already
    recorded, it just won't backfill your full history on its own.
    """
    if not user.leetcode_username:
        raise HTTPException(400, "No LeetCode username configured for this user.")

    try:
        recent = fetch_recent_accepted_submissions(user.leetcode_username)
    except Exception as exc:
        logger.exception("LeetCode fetch failed")
        raise HTTPException(502, f"Failed to fetch LeetCode submissions: {exc}") from exc

    problems = extract_unique_solved_problems_leetcode(recent)
    stats = sync_platform(db, user, problems)

    return SyncResult(
        platform="leetcode",
        fetched_submissions=len(recent),
        unique_solved=len(problems),
        new_problems=stats["new_problems"],
        new_solves=stats["new_solves"],
    )
