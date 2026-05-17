from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MetricResponse(BaseModel):
    id: str
    dataset_id: str
    metric_type: str
    metric_name: str
    value: float | None = None
    currency: str | None = "USD"
    period: str | None = None
    extra_metadata: dict | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class MetricsGroupedResponse(BaseModel):
    dataset_id: str
    total_revenue: list[MetricResponse] = []
    monthly_revenue: list[MetricResponse] = []
    growth_rate: list[MetricResponse] = []
    top_products: list[MetricResponse] = []
    category_breakdown: list[MetricResponse] = []
    aov: list[MetricResponse] = []
    trends: list[MetricResponse] = []
    other: list[MetricResponse] = []
