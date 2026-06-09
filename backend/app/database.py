import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

db_available = False


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _create_engine():
    url = _normalize_database_url(settings.DATABASE_URL)
    kwargs: dict = {"echo": settings.DEBUG, "pool_pre_ping": True}

    if "sqlite" in url:
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        kwargs["pool_recycle"] = 300

    return create_engine(url, **kwargs)


engine = _create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    global db_available
    import app.models  # noqa: F401 — register all tables with Base.metadata

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    Base.metadata.create_all(bind=engine)
    db_available = True
    logger.info("Database initialized successfully")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
