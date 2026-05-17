from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.metric import MetricResponse, MetricsGroupedResponse
from app.services.metric_service import get_metrics, get_metrics_grouped, get_metrics_by_type

router = APIRouter()


@router.get("/metrics/{dataset_id}", response_model=list[MetricResponse])
def list_metrics(dataset_id: str, db: Session = Depends(get_db)):
    metrics = get_metrics(db, dataset_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="No metrics found for this dataset")
    return metrics


@router.get("/metrics/{dataset_id}/grouped", response_model=MetricsGroupedResponse)
def list_metrics_grouped(dataset_id: str, db: Session = Depends(get_db)):
    metrics = get_metrics(db, dataset_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="No metrics found for this dataset")

    grouped = {}
    for m in metrics:
        grouped.setdefault(m.metric_type, []).append(m)

    return MetricsGroupedResponse(
        dataset_id=dataset_id,
        total_revenue=grouped.get("total_revenue", []),
        monthly_revenue=grouped.get("monthly_revenue", []),
        growth_rate=grouped.get("growth_rate", []),
        top_products=grouped.get("top_products", []),
        category_breakdown=grouped.get("category_breakdown", []),
        aov=grouped.get("aov", []),
        trends=grouped.get("trends", []),
        other=[m for t, ms in grouped.items() if t not in (
            "total_revenue", "monthly_revenue", "growth_rate",
            "top_products", "category_breakdown", "aov", "trends"
        ) for m in ms],
    )


@router.get("/metrics/{dataset_id}/{metric_type}", response_model=list[MetricResponse])
def list_metrics_by_type(
    dataset_id: str,
    metric_type: str,
    db: Session = Depends(get_db),
):
    metrics = get_metrics_by_type(db, dataset_id, metric_type)
    return metrics
