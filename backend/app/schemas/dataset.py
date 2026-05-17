from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ColumnMeta(BaseModel):
    name: str
    dtype: str
    detected_role: str | None = None
    sample_values: list | None = None


class DatasetResponse(BaseModel):
    id: str
    upload_id: str
    name: str
    row_count: int
    column_count: int
    columns_meta: list[ColumnMeta] | None = None
    summary: dict | None = None
    status: str
    error_msg: str | None = None
    file_path: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class DatasetListResponse(BaseModel):
    datasets: list[DatasetResponse]
    total: int


class PreviewResponse(BaseModel):
    columns: list[str]
    rows: list[dict]
    total_rows: int
