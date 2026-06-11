import io
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.models.upload import Upload
from app.utils.file_parser import validate_file, parse_file, get_summary_stats
from app.services.storage_service import get_storage_service


def process_upload(file, db: Session) -> Upload:
    filename = file.filename
    validate_file(filename)

    ext = Path(filename).suffix.lower()
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}{ext}"

    content = file.file.read()
    file_size = len(content)

    storage = get_storage_service()
    storage_path = storage.save(safe_filename, content)

    upload = Upload(
        id=file_id,
        filename=filename,
        file_type=ext.lstrip("."),
        file_size=file_size,
        status="uploaded",
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)

    return upload


def parse_upload_file(upload: Upload, db: Session) -> tuple:
    ext = Path(upload.filename).suffix.lower()
    safe_filename = f"{upload.id}{ext}"

    storage = get_storage_service()
    public_url = storage.get_public_url(safe_filename)

    try:
        buf = storage.load(safe_filename)
    except Exception as e:
        upload.status = "failed"
        upload.error_msg = f"File not found in storage: {e}"
        db.commit()
        raise FileNotFoundError(f"File not found in storage: {safe_filename}")

    df = parse_file(buf, file_ext=ext)

    summary = get_summary_stats(df)

    upload.row_count = summary["row_count"]
    upload.column_count = summary["column_count"]
    upload.status = "parsed"
    db.commit()

    return df, summary, public_url
