import io
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.models.upload import Upload
from app.services.storage_service import get_storage_service
from app.utils.file_parser import parse_file


def load_dataset_dataframe(dataset: Dataset, db: Session) -> pd.DataFrame:
    upload = db.query(Upload).filter(Upload.id == dataset.upload_id).first()
    if not upload:
        raise FileNotFoundError("Upload record not found for this dataset")

    ext = Path(upload.filename).suffix.lower()
    safe_filename = f"{upload.id}{ext}"
    storage = get_storage_service()

    try:
        buf = storage.load(safe_filename)
        return parse_file(buf, file_ext=ext)
    except Exception:
        if dataset.file_path:
            return parse_file(dataset.file_path, file_ext=ext)
        raise
