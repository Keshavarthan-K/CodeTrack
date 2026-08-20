import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.database import Base, engine
from app.database import models  # noqa: F401 - needed so Base sees all models before create_all
from app.routes import analytics, dashboard, sync
from app.services.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="CodeTrack API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(analytics.router)
app.include_router(sync.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to CodeTrack 🚀",
        "docs": "/docs",
    }
