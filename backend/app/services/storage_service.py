import io
import os
import tempfile
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

import httpx

from app.config import settings


class StorageService(ABC):
    @abstractmethod
    def save(self, filename: str, content: bytes) -> str:
        ...

    @abstractmethod
    def load(self, path: str) -> io.BytesIO:
        ...

    @abstractmethod
    def delete(self, path: str) -> None:
        ...

    @abstractmethod
    def get_public_url(self, path: str) -> str:
        ...


class LocalStorageService(StorageService):
    def __init__(self) -> None:
        self.base_dir = Path(settings.UPLOAD_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, filename: str, content: bytes) -> str:
        filepath = self.base_dir / filename
        filepath.write_bytes(content)
        return str(filepath)

    def _resolve(self, path: str) -> Path:
        p = Path(path)
        if p.is_absolute():
            return p
        return self.base_dir / p

    def load(self, path: str) -> io.BytesIO:
        return io.BytesIO(self._resolve(path).read_bytes())

    def delete(self, path: str) -> None:
        self._resolve(path).unlink(missing_ok=True)

    def get_public_url(self, path: str) -> str:
        return str(self.base_dir / path) if "/" not in path else path


class SupabaseStorageService(StorageService):
    def __init__(self) -> None:
        self.url = settings.SUPABASE_URL.rstrip("/")
        self.key = settings.SUPABASE_SERVICE_KEY
        self.bucket = settings.SUPABASE_STORAGE_BUCKET
        self._headers = {
            "Authorization": f"Bearer {self.key}",
            "apikey": self.key,
        }

    def save(self, filename: str, content: bytes) -> str:
        resp = httpx.post(
            f"{self.url}/storage/v1/object/{self.bucket}/{filename}",
            headers=self._headers,
            content=content,
        )
        resp.raise_for_status()
        return filename

    def load(self, path: str) -> io.BytesIO:
        resp = httpx.get(
            f"{self.url}/storage/v1/object/{self.bucket}/{path}",
            headers=self._headers,
        )
        resp.raise_for_status()
        return io.BytesIO(resp.content)

    def delete(self, path: str) -> None:
        httpx.delete(
            f"{self.url}/storage/v1/object/{self.bucket}/{path}",
            headers=self._headers,
        )

    def get_public_url(self, path: str) -> str:
        return f"{self.url}/storage/v1/object/public/{self.bucket}/{path}"


def get_storage_service() -> StorageService:
    if settings.STORAGE_BACKEND == "supabase":
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set "
                "when STORAGE_BACKEND=supabase"
            )
        return SupabaseStorageService()
    return LocalStorageService()
