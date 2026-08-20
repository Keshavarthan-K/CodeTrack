from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import RatingHistory


def get_rating_entry(db: Session, user_id: int, platform: str, contest_id: str):
    return (
        db.query(RatingHistory)
        .filter(
            RatingHistory.user_id == user_id,
            RatingHistory.platform == platform,
            RatingHistory.contest_id == contest_id,
        )
        .first()
    )


def create_rating_entry(db: Session, user_id: int, entry: dict):
    row = RatingHistory(
        user_id=user_id,
        platform=entry["platform"],
        contest_id=str(entry["contest_id"]),
        contest_name=entry.get("contest_name"),
        rating=entry["rating"],
        rank=entry.get("rank"),
        timestamp=entry["timestamp"],
    )
    db.add(row)
    db.flush()
    return row


def list_rating_history(db: Session, user_id: int, platform: str | None = None) -> list[RatingHistory]:
    query = db.query(RatingHistory).filter(RatingHistory.user_id == user_id)
    if platform:
        query = query.filter(RatingHistory.platform == platform)
    return query.order_by(RatingHistory.timestamp).all()
