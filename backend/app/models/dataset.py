import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.types import JSON

from app.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    upload_id = Column(String(36), nullable=False)
    name = Column(String(500), nullable=False)
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    columns_meta = Column(JSON, default=list)
    summary = Column(JSON, default=dict)
    file_path = Column(String(1000), nullable=True)
    status = Column(String(20), default="processing")
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Dataset {self.name} ({self.status})>"
