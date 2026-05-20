import json

from fastapi import APIRouter, HTTPException

from database.db import get_all_applications, get_application_by_id


router = APIRouter(tags=["admin"])


def _decode_tracks(row: dict) -> dict:
    row_dict = dict(row)
    try:
        row_dict["selected_tracks"] = json.loads(row_dict.get("selected_tracks") or "[]")
    except json.JSONDecodeError:
        row_dict["selected_tracks"] = []
    return row_dict


@router.get("/applications")
def list_applications():
    rows = get_all_applications()
    return [_decode_tracks(row) for row in rows]


@router.get("/applications/{application_id}")
def get_application(application_id: str):
    row = get_application_by_id(application_id)
    if not row:
        raise HTTPException(status_code=404, detail="Application not found.")
    return _decode_tracks(row)
