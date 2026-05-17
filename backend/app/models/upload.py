import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, BigInteger, DateTime, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.database import Base


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    status = Column(String(20), default="pending")
    error_msg = Column(Text, nullable=True)
    dataset_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Upload {self.filename} ({self.status})>"
