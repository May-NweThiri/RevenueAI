from fastapi import APIRouter

from app.api.v1 import upload, datasets, metrics, insights, chat

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(upload.router, tags=["Upload"])
api_router.include_router(datasets.router, tags=["Datasets"])
api_router.include_router(metrics.router, tags=["Metrics"])
api_router.include_router(insights.router, tags=["Insights"])
api_router.include_router(chat.router, tags=["Chat"])
