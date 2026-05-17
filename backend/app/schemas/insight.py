from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class InsightResponse(BaseModel):
    id: str
    dataset_id: str
    type: str
    title: str
    content: str
    severity: str
    extra_metadata: dict | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class InsightListResponse(BaseModel):
    insights: list[InsightResponse]
    total: int
