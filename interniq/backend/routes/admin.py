from fastapi import APIRouter, HTTPException

from services.supabase_client import fetch_application_by_id, fetch_applications


router = APIRouter(tags=["admin"])


@router.get("/applications")
def get_applications():
    return fetch_applications()


@router.get("/applications/{application_id}")
def get_application(application_id: str):
    application = fetch_application_by_id(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")
    return application
