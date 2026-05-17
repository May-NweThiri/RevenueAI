import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.types import JSON

from app.database import Base


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)
    metric_name = Column(String(255), nullable=False)
    value = Column(Float, nullable=True)
    currency = Column(String(3), default="USD")
    period = Column(String(50), nullable=True)
    extra_metadata = Column("metadata", JSON, default=dict)
    rank = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Metric {self.metric_name}: {self.value}>"
