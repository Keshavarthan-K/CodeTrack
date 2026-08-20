"""
Automatic synchronization (spec section 39/40).

Runs sync jobs on a schedule using APScheduler, and uses SyncState to
fetch/process incrementally rather than re-walking each platform's
full history every run. Wired into the app in app/main.py via
start_scheduler()/stop_scheduler() on FastAPI's startup/shutdown
events (or lifespan, on newer FastAPI).

Correctness note: incremental sync is an optimization only. Even if
SyncState is stale, empty, or wrong, the unique constraints on
Problem and SolvedProblem guarantee no duplicate is ever written -
see spec section 41 ("Data Integrity") and
tests/test_sync_idempotency.py.
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.database.database import SessionLocal
from app.database.models import User
from app.fetchers.codeforces import fetch_submissions_incremental
from app.repositories.sync_state_repository import get_sync_state, upsert_sync_state
from app.services.rating_service import sync_codeforces_rating
from app.services.submission_processor import extract_unique_solved_problems
from app.services.sync_service import sync_platform

logger = logging.getLogger("codetrack.scheduler")

_scheduler: BackgroundScheduler | None = None


def sync_codeforces_for_user(db, user: User) -> dict:
    if not user.codeforces_username:
        return {"skipped": True}

    state = get_sync_state(db, user.id, "codeforces")
    last_id = int(state.last_submission_id) if state and state.last_submission_id else None

    try:
        submissions = fetch_submissions_incremental(user.codeforces_username, last_submission_id=last_id)
    except Exception as exc:
        logger.exception("Codeforces incremental fetch failed for %s", user.codeforces_username)
        upsert_sync_state(db, user.id, "codeforces", status="error", error=str(exc))
        raise

    problems = extract_unique_solved_problems(submissions)
    stats = sync_platform(db, user, problems)

    newest_id = max((s["id"] for s in submissions), default=last_id)
    upsert_sync_state(
        db, user.id, "codeforces",
        last_submission_id=str(newest_id) if newest_id is not None else None,
        status="ok",
    )

    logger.info(
        "Codeforces sync for %s: %d fetched, %d unique, %d new problems, %d new solves",
        user.codeforces_username, len(submissions), len(problems),
        stats["new_problems"], stats["new_solves"],
    )
    return stats


def run_daily_sync():
    """Entry point the scheduler calls. Iterates every user in the DB."""
    db = SessionLocal()
    try:
        for user in db.query(User).all():
            try:
                sync_codeforces_for_user(db, user)
            except Exception:
                # One user's failure (e.g. bad handle, CF temporarily down)
                # should never block the rest of the run.
                logger.exception("Codeforces sync failed for user_id=%s", user.id)

            try:
                sync_codeforces_rating(db, user)
            except Exception:
                logger.exception("Rating sync failed for user_id=%s", user.id)

            # LeetCode/CodeChef are intentionally NOT auto-scheduled by
            # default - see their fetcher docstrings for why (LeetCode's
            # unauthenticated feed is capped at ~20 recent solves;
            # CodeChef has no stable API). Uncomment once you've
            # validated those fetchers against your own account:
            #
            # try:
            #     sync_leetcode_for_user(db, user)
            # except Exception:
            #     logger.exception("LeetCode sync failed for user_id=%s", user.id)
    finally:
        db.close()


def start_scheduler(hour: int = 3, minute: int = 0) -> BackgroundScheduler:
    """Starts a daily background job (default: 03:00 server time)."""
    global _scheduler

    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        run_daily_sync,
        trigger=CronTrigger(hour=hour, minute=minute),
        id="daily_sync",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Scheduler started: daily sync at %02d:%02d", hour, minute)
    return _scheduler


def stop_scheduler():
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
