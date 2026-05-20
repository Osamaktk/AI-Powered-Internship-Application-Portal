from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from supabase import Client, create_client


_SUPABASE: Optional[Client] = None
_BASE_DIR = Path(__file__).resolve().parent.parent
_LOCAL_STORAGE_DIR = _BASE_DIR / "local_storage"
_LOCAL_UPLOADS_DIR = _LOCAL_STORAGE_DIR / "uploads"
_LOCAL_DB_FILE = _LOCAL_STORAGE_DIR / "applications.json"


def _is_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _is_local_mode() -> bool:
    return _is_truthy(os.getenv("LOCAL_DEV_MODE")) or _is_truthy(
        os.getenv("USE_LOCAL_BACKEND")
    )


def is_local_mode() -> bool:
    return _is_local_mode()


def _ensure_local_storage() -> None:
    _LOCAL_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    _LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    if not _LOCAL_DB_FILE.exists():
        _LOCAL_DB_FILE.write_text("[]", encoding="utf-8")


def _read_local_rows() -> List[Dict[str, Any]]:
    _ensure_local_storage()
    try:
        rows = json.loads(_LOCAL_DB_FILE.read_text(encoding="utf-8"))
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    except json.JSONDecodeError:
        pass
    return []


def _write_local_rows(rows: List[Dict[str, Any]]) -> None:
    _ensure_local_storage()
    _LOCAL_DB_FILE.write_text(json.dumps(rows, ensure_ascii=True, indent=2), encoding="utf-8")


def get_supabase() -> Client:
    global _SUPABASE
    if _SUPABASE is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set.")
        _SUPABASE = create_client(url, key)
    return _SUPABASE


def upload_file(
    bucket_name: str,
    file_path: str,
    file_bytes: bytes,
    content_type: str,
) -> str:
    if _is_local_mode():
        _ensure_local_storage()
        destination = _LOCAL_UPLOADS_DIR / bucket_name / file_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(file_bytes)
        # Served by FastAPI StaticFiles in local mode.
        relative = "/".join(destination.relative_to(_LOCAL_UPLOADS_DIR).parts)
        return f"http://localhost:8000/local-files/{relative}"

    supabase = get_supabase()
    storage = supabase.storage.from_(bucket_name)

    storage.upload(
        path=file_path,
        file=file_bytes,
        file_options={
            "content-type": content_type,
            "upsert": "false",
        },
    )

    public_url = storage.get_public_url(file_path)
    if isinstance(public_url, dict):
        return public_url.get("publicURL") or public_url.get("public_url") or ""
    return str(public_url)


def insert_application(application_data: Dict[str, Any]) -> Dict[str, Any]:
    if _is_local_mode():
        rows = _read_local_rows()
        record = dict(application_data)
        record.setdefault("id", str(uuid4()))
        record.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        rows.append(record)
        _write_local_rows(rows)
        return record

    supabase = get_supabase()
    response = supabase.table("applications").insert(application_data).execute()
    data = response.data or []
    return data[0] if data else {}


def fetch_applications() -> List[Dict[str, Any]]:
    if _is_local_mode():
        rows = _read_local_rows()
        rows.sort(key=lambda row: str(row.get("created_at", "")), reverse=True)
        return rows

    supabase = get_supabase()
    response = (
        supabase.table("applications")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []


def fetch_application_by_id(application_id: str) -> Optional[Dict[str, Any]]:
    if _is_local_mode():
        for row in _read_local_rows():
            if str(row.get("id")) == str(application_id):
                return row
        return None

    supabase = get_supabase()
    response = (
        supabase.table("applications")
        .select("*")
        .eq("id", application_id)
        .limit(1)
        .execute()
    )
    data = response.data or []
    return data[0] if data else None
