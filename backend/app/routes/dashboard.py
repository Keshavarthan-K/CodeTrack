from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.dependencies import get_current_user
from app.schemas import DashboardResponse
from app.services import analytics_service

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return analytics_service.get_dashboard(db, user.id)
