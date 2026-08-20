"""
Shared pytest fixtures.

Every test gets a fresh, isolated in-memory SQLite database - tests
never touch backend/data/codetrack.db. This is done by overriding the
app's `engine`/`SessionLocal` for the duration of each test, so the
production code under test doesn't need to know it's being tested.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.database import models  # noqa: F401 - registers models on Base


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def user(db_session):
    from app.database.models import User

    u = User(
        name="Test User",
        leetcode_username="",
        codeforces_username="testuser",
        codechef_username="",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u
