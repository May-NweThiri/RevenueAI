from sqlalchemy.orm import Session

from app.models.metric import Metric


def save_metrics(db: Session, dataset_id: str, metrics_grouped: dict) -> None:
    for metric_type, metrics in metrics_grouped.items():
        for m in metrics:
            metric = Metric(
                dataset_id=dataset_id,
                metric_type=m.get("metric_type", metric_type),
                metric_name=m.get("metric_name", ""),
                value=m.get("value"),
                currency=m.get("currency", "USD"),
                period=m.get("period"),
                extra_metadata=m.get("metadata", {}),
                rank=m.get("rank", 0),
            )
            db.add(metric)
    db.commit()


def get_metrics(db: Session, dataset_id: str) -> list[Metric]:
    return (
        db.query(Metric)
        .filter(Metric.dataset_id == dataset_id)
        .order_by(Metric.rank.asc(), Metric.created_at.desc())
        .all()
    )


def get_metrics_grouped(db: Session, dataset_id: str) -> dict:
    metrics = get_metrics(db, dataset_id)
    grouped = {}
    for m in metrics:
        grouped.setdefault(m.metric_type, []).append(m)
    return grouped


def get_metrics_by_type(db: Session, dataset_id: str, metric_type: str) -> list[Metric]:
    return (
        db.query(Metric)
        .filter(Metric.dataset_id == dataset_id, Metric.metric_type == metric_type)
        .order_by(Metric.rank.asc())
        .all()
    )


def delete_metrics(db: Session, dataset_id: str) -> None:
    db.query(Metric).filter(Metric.dataset_id == dataset_id).delete()
    db.commit()
