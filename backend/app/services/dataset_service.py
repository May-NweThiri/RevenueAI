from sqlalchemy.orm import Session

from app.models.dataset import Dataset


def create_dataset(
    db: Session,
    upload_id: str,
    name: str,
    row_count: int,
    column_count: int,
    columns_meta: list,
    summary: dict,
    file_path: str,
) -> Dataset:
    dataset = Dataset(
        upload_id=upload_id,
        name=name,
        row_count=row_count,
        column_count=column_count,
        columns_meta=columns_meta,
        summary=summary,
        file_path=file_path,
        status="ready",
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


def get_dataset(db: Session, dataset_id: str) -> Dataset | None:
    return db.query(Dataset).filter(Dataset.id == dataset_id).first()


def get_datasets(db: Session, skip: int = 0, limit: int = 50) -> list[Dataset]:
    return (
        db.query(Dataset)
        .order_by(Dataset.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_datasets_count(db: Session) -> int:
    return db.query(Dataset).count()


def delete_dataset(db: Session, dataset_id: str) -> bool:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        return False
    db.delete(dataset)
    db.commit()
    return True


def update_dataset_status(db: Session, dataset_id: str, status: str, error_msg: str | None = None) -> Dataset | None:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if dataset:
        dataset.status = status
        if error_msg:
            dataset.error_msg = error_msg
        db.commit()
        db.refresh(dataset)
    return dataset
