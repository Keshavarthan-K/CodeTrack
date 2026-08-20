from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

# Absolute path anchored to the backend/ folder, so the app works no
# matter which directory `uvicorn`/pytest is launched from.
DATABASE_URL = settings.DATABASE_URL

# Make sure the data/ directory exists before SQLite tries to create the file.
settings.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    echo=settings.SQL_ECHO,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()