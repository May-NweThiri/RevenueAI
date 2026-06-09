import logging
from urllib.parse import urlparse

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

db_available = False
db_error: str | None = None


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if "supabase.com" in url and "sslmode=" not in url:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}sslmode=require"
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
    global db_available, db_error
    import app.models  # noqa: F401 — register all tables with Base.metadata

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        Base.metadata.create_all(bind=engine)
        db_available = True
        db_error = None
        logger.info("Database initialized successfully")
    except Exception as e:
        db_available = False
        db_error = str(e)
        raise


def get_database_diagnostics() -> dict[str, str]:
    url = _normalize_database_url(settings.DATABASE_URL)
    parsed = urlparse(url)
    if "sqlite" in url:
        source = "sqlite-default"
    elif parsed.hostname and "supabase.com" in parsed.hostname:
        source = "supabase"
    else:
        source = "postgresql"
    return {
        "source": source,
        "host": parsed.hostname or "unknown",
        "user": parsed.username or "unknown",
    }


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
