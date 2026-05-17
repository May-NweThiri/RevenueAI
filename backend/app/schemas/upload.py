from datetime import datetime

from pydantic import BaseModel


class UploadResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    row_count: int | None = None
    column_count: int | None = None
    status: str
    error_msg: str | None = None
    dataset_id: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class UploadListResponse(BaseModel):
    uploads: list[UploadResponse]
    total: int
