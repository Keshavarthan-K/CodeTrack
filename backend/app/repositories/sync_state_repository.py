from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.database.models import SyncState


def get_sync_state(db: Session, user_id: int, platform: str) -> SyncState | None:
    return (
        db.query(SyncState)
        .filter(SyncState.user_id == user_id, SyncState.platform == platform)
        .first()
    )


def upsert_sync_state(
    db: Session,
    user_id: int,
    platform: str,
    *,
    last_submission_id: str | None = None,
    status: str = "ok",
    error: str | None = None,
) -> SyncState:
    state = get_sync_state(db, user_id, platform)

    if state is None:
        state = SyncState(user_id=user_id, platform=platform)
        db.add(state)

    if last_submission_id is not None:
        state.last_submission_id = last_submission_id

    state.last_sync_at = datetime.now(UTC)
    state.last_sync_status = status
    state.last_error = error

    db.commit()
    db.refresh(state)
    return state
