from typing import Generator

from fastapi import HTTPException
from sqlalchemy.orm import Session

import app.database as database
from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    if not database.db_available:
        raise HTTPException(
            status_code=503,
            detail=(
                "Database unavailable. Set DATABASE_URL on Railway to your "
                "Supabase PostgreSQL connection string and redeploy."
            ),
        )
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
