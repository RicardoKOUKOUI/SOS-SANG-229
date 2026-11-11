from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck():
    """Process is up. Does not touch the database."""
    return {"status": "ok"}


@router.get("/health/ready")
def ready(db: Session = Depends(get_db)):
    """Database accepts a trivial query. 503 when DATABASE_URL is missing or down."""
    db.execute(text("SELECT 1"))
    return {"status": "ready", "database": "ok"}
