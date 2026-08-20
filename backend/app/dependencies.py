"""
Shared FastAPI dependencies.

CodeTrack is a personal tracker (one CodeTrack account = one person's
LeetCode/Codeforces/CodeChef handles), so "current user" simply means
"the User row for the person running this instance" rather than a full
multi-tenant auth system. get_current_user() finds or creates that row
from the usernames configured in .env.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database.database import get_db
from app.database.models import User


def get_or_create_default_user(db: Session) -> User:
    user = (
        db.query(User)
        .filter(User.codeforces_username == settings.CODEFORCES_USERNAME)
        .first()
    )

    if user is not None:
        return user

    user = User(
        name=settings.CODEFORCES_USERNAME or "CodeTrack User",
        leetcode_username=settings.LEETCODE_USERNAME,
        codeforces_username=settings.CODEFORCES_USERNAME,
        codechef_username=settings.CODECHEF_USERNAME,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_current_user(db: Session = Depends(get_db)) -> User:
    return get_or_create_default_user(db)
