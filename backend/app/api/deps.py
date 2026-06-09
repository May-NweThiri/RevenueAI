from typing import Generator

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal, db_available


def get_db() -> Generator[Session, None, None]:
    if not db_available:
        raise HTTPException(
            status_code=503,
            detail=(
                "Database unavailable. Set DATABASE_URL on Railway to your "
                "Supabase PostgreSQL connection string and redeploy."
            ),
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
