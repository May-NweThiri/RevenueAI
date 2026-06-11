import logging
import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.ai.client import ai_provider_name
import app.database as db
from app.database import init_db, get_database_diagnostics
from app.api.router import api_router

logger = logging.getLogger(__name__)

# Vercel preview deployments use unique subdomains (e.g. revenue-abc123-team.vercel.app).
VERCEL_ORIGIN_PATTERN = re.compile(r"^https://.*\.vercel\.app$")


def _allowed_origins() -> list[str]:
    return [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]


def _is_origin_allowed(origin: str | None) -> bool:
    if not origin:
        return False
    if origin in _allowed_origins():
        return True
    return bool(VERCEL_ORIGIN_PATTERN.match(origin))


def _cors_headers(request: Request) -> dict[str, str]:
    origin = request.headers.get("origin")
    if origin and _is_origin_allowed(origin):
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        }
    return {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
    except Exception as e:
        logger.error("Database unavailable: %s", e)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered revenue analytics platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail},
        headers=_cors_headers(request),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers=_cors_headers(request),
    )


app.include_router(api_router)


@app.get("/health")
def health_check():
    payload = {
        "status": "healthy" if db.db_available else "degraded",
        "app": settings.APP_NAME,
        "version": "0.1.0",
        "database": "connected" if db.db_available else "unavailable",
        "ai": ai_provider_name(),
    }
    if not db.db_available:
        payload["database_config"] = get_database_diagnostics()
        if db.db_error:
            payload["database_error"] = db.db_error
    return payload
