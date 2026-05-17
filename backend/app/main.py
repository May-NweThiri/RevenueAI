import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api.router import api_router

logger = logging.getLogger(__name__)

db_available = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_available
    try:
        init_db()
        db_available = True
        logger.info("Database initialized successfully")
    except Exception as e:
        db_available = False
        logger.warning("Database unavailable: %s", e)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered revenue analytics platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://revenue-ai-delta.vercel.app",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy" if db_available else "degraded",
        "app": settings.APP_NAME,
        "version": "0.1.0",
        "database": "connected" if db_available else "unavailable",
    }
