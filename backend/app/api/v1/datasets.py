from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetResponse, DatasetListResponse, PreviewResponse
from app.services.dataset_service import get_dataset, get_datasets, get_datasets_count, delete_dataset
from app.utils.file_parser import parse_file

router = APIRouter()


@router.get("/datasets", response_model=DatasetListResponse)
def list_datasets(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    datasets = get_datasets(db, skip=skip, limit=limit)
    total = get_datasets_count(db)
    return {"datasets": datasets, "total": total}


@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
def read_dataset(dataset_id: str, db: Session = Depends(get_db)):
    dataset = get_dataset(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.delete("/datasets/{dataset_id}", status_code=204)
def remove_dataset(dataset_id: str, db: Session = Depends(get_db)):
    deleted = delete_dataset(db, dataset_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return None


@router.get("/datasets/{dataset_id}/preview", response_model=PreviewResponse)
def preview_dataset(dataset_id: str, db: Session = Depends(get_db)):
    dataset = get_dataset(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if not dataset.file_path:
        raise HTTPException(status_code=400, detail="Dataset file not available")

    try:
        df = parse_file(dataset.file_path)
        preview_rows = df.head(50).to_dict(orient="records")
        return PreviewResponse(
            columns=list(df.columns),
            rows=preview_rows,
            total_rows=len(df),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {e}")
