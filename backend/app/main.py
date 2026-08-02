from fastapi import FastAPI

from app.database.database import Base, engine
from app.database import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CodeTrack API")


@app.get("/")
def root():
    return {
        "message": "Welcome to CodeTrack 🚀"
    }