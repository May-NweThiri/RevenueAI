import pandas as pd
from fastapi import APIRouter, Depends, UploadFile as FastAPIUploadFile, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.database import SessionLocal
from app.models.upload import Upload
from app.schemas.upload import UploadResponse, UploadListResponse
from app.services.file_service import process_upload, parse_upload_file
from app.services.dataset_service import create_dataset, update_dataset_status
from app.services.metric_service import save_metrics
from app.services.insight_service import save_insights
from app.ai.column_detector import detect_columns
from app.ai.metric_calculator import calculate_all_metrics
from app.ai.insight_engine import generate_insights

router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_file(
    file: FastAPIUploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    upload = process_upload(file, db)

    background_tasks.add_task(process_dataset, upload.id)

    return upload


@router.get("/uploads", response_model=UploadListResponse)
def list_uploads(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    uploads = db.query(Upload).order_by(Upload.created_at.desc()).offset(skip).limit(limit).all()
    return {"uploads": [UploadResponse.model_validate(u) for u in uploads], "total": len(uploads)}


@router.get("/uploads/{upload_id}", response_model=UploadResponse)
def get_upload(upload_id: str, db: Session = Depends(get_db)):
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    return upload


def process_dataset(upload_id: str):
    db_local = SessionLocal()
    try:
        upload = db_local.query(Upload).filter(Upload.id == upload_id).first()
        if not upload:
            return

        upload.status = "processing"
        db_local.commit()

        df, summary, file_path = parse_upload_file(upload, db_local)

        columns_meta = detect_columns(df)

        dataset = create_dataset(
            db=db_local,
            upload_id=upload.id,
            name=upload.filename,
            row_count=len(df),
            column_count=len(df.columns),
            columns_meta=columns_meta,
            summary=summary,
            file_path=file_path,
        )

        upload.dataset_id = dataset.id
        db_local.commit()

        metrics_grouped = calculate_all_metrics(df, columns_meta)
        save_metrics(db_local, dataset.id, metrics_grouped)

        insights = generate_insights(
            dataset_name=dataset.name,
            row_count=dataset.row_count,
            column_count=dataset.column_count,
            columns_meta=columns_meta,
            metrics_grouped=metrics_grouped,
        )
        save_insights(db_local, dataset.id, insights)

        dataset.status = "ready"
        upload.status = "ready"
        db_local.commit()

    except Exception as e:
        update_dataset_status(db_local, upload_id, "failed", str(e))
        upload = db_local.query(Upload).filter(Upload.id == upload_id).first()
        if upload:
            upload.status = "failed"
            upload.error_msg = str(e)
            db_local.commit()
    finally:
        db_local.close()
