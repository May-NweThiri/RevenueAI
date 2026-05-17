from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.insight import InsightResponse, InsightListResponse
from app.services.insight_service import get_insights, get_insights_count

router = APIRouter()


@router.get("/insights/{dataset_id}", response_model=InsightListResponse)
def list_insights(dataset_id: str, db: Session = Depends(get_db)):
    insights = get_insights(db, dataset_id)
    total = get_insights_count(db, dataset_id)
    return {"insights": insights, "total": total}


@router.get("/insights/{dataset_id}/latest", response_model=list[InsightResponse])
def latest_insights(dataset_id: str, limit: int = 5, db: Session = Depends(get_db)):
    insights = get_insights(db, dataset_id)
    return insights[:limit]
