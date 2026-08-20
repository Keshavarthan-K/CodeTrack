from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.fetchers.codeforces import fetch_rating_history
from app.repositories import rating_repository as repo


def _normalize_cf_rating_change(raw: dict) -> dict:
    return {
        "platform": "codeforces",
        "contest_id": raw["contestId"],
        "contest_name": raw.get("contestName"),
        "rating": raw["newRating"],
        "rank": raw.get("rank"),
        "timestamp": datetime.fromtimestamp(raw["ratingUpdateTimeSeconds"], UTC),
    }


def sync_codeforces_rating(db: Session, user) -> dict:
    """
    Idempotent, same pattern as sync_platform(): each contest is keyed
    by (user_id, platform, contest_id) via uq_user_platform_contest, so
    re-running this never creates duplicate rating points.
    """
    raw_changes = fetch_rating_history(user.codeforces_username)

    created = 0
    for raw in raw_changes:
        entry = _normalize_cf_rating_change(raw)

        existing = repo.get_rating_entry(db, user.id, "codeforces", str(entry["contest_id"]))
        if existing is None:
            repo.create_rating_entry(db, user.id, entry)
            created += 1

    db.commit()

    return {"fetched_contests": len(raw_changes), "new_rating_points": created}
