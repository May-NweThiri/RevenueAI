from sqlalchemy import case
from sqlalchemy.orm import Session

from app.models.insight import Insight


def save_insights(db: Session, dataset_id: str, insights: list[dict]) -> None:
    for ins in insights:
        insight = Insight(
            dataset_id=dataset_id,
            type=ins.get("type", "general"),
            title=ins.get("title", ""),
            content=ins.get("content", ""),
            severity=ins.get("severity", "info"),
            extra_metadata=ins.get("metadata", {}),
        )
        db.add(insight)
    db.commit()


def get_insights(db: Session, dataset_id: str) -> list[Insight]:
    return (
        db.query(Insight)
        .filter(Insight.dataset_id == dataset_id)
        .order_by(
            case(
                (Insight.severity == "critical", 0),
                (Insight.severity == "warning", 1),
                else_=2,
            ),
            Insight.created_at.desc(),
        )
        .all()
    )


def get_insights_count(db: Session, dataset_id: str) -> int:
    return db.query(Insight).filter(Insight.dataset_id == dataset_id).count()


def delete_insights(db: Session, dataset_id: str) -> None:
    db.query(Insight).filter(Insight.dataset_id == dataset_id).delete()
    db.commit()
