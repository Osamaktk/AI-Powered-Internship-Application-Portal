import os
import json
import re
from typing import List
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from config.track_managers import TRACK_MANAGERS
from services.ai_verifier import verify_document
from services.email_service import (
    send_received_email,
    send_rejection_email,
    send_track_notification,
)
from services.pdf_extractor import extract_text_from_pdf
from services.supabase_client import insert_application, is_local_mode, upload_file


router = APIRouter(tags=["applications"])

MAX_PDF_BYTES = 5 * 1024 * 1024
MAX_PHOTO_BYTES = 2 * 1024 * 1024
RECEIVED_MESSAGE = "Your application has been received and we will be in touch very soon."
STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "interniq-docs")


def _parse_selected_tracks(raw: str) -> List[str]:
    if not raw:
        return []

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except json.JSONDecodeError:
        pass

    return [item.strip() for item in raw.split(",") if item.strip()]


def _safe_filename(filename: str) -> str:
    if not filename:
        return "file"
    return re.sub(r"[^a-zA-Z0-9._-]", "_", filename)


def _validate_pdf(file: UploadFile, file_bytes: bytes, label: str) -> None:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail=f"{label} must be a PDF file.")
    if len(file_bytes) > MAX_PDF_BYTES:
        raise HTTPException(status_code=400, detail=f"{label} exceeds 5MB size limit.")


@router.post("/apply")
async def submit_application(
    internship_year: str = Form("2026"),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    location: str = Form("PK"),
    city: str = Form(...),
    university: str = Form(...),
    degree: str = Form(...),
    major: str = Form(...),
    cgpa: str = Form(...),
    semester: str = Form(...),
    class_ranking: str = Form(""),
    field: str = Form(...),
    selected_tracks: str = Form(...),
    video_link: str = Form(""),
    resume: UploadFile = File(...),
    transcript: UploadFile = File(...),
    photo: UploadFile | None = File(default=None),
):
    tracks = _parse_selected_tracks(selected_tracks)
    if not tracks:
        raise HTTPException(status_code=400, detail="Please select at least one track.")
    if len(tracks) > 3:
        raise HTTPException(status_code=400, detail="You can select up to 3 tracks only.")

    resume_bytes = await resume.read()
    transcript_bytes = await transcript.read()
    _validate_pdf(resume, resume_bytes, "Resume")
    _validate_pdf(transcript, transcript_bytes, "Transcript")

    photo_bytes = b""
    if photo and photo.filename:
        photo_bytes = await photo.read()
        if len(photo_bytes) > MAX_PHOTO_BYTES:
            raise HTTPException(status_code=400, detail="Photo exceeds 2MB size limit.")
        if not photo.filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
            raise HTTPException(
                status_code=400,
                detail="Photo must be JPG, JPEG, PNG, or GIF.",
            )

    resume_text = extract_text_from_pdf(resume_bytes)
    transcript_text = extract_text_from_pdf(transcript_bytes)

    resume_verdict = verify_document(
        resume_text,
        "resume",
        source_name=resume.filename or "",
    )
    transcript_verdict = verify_document(
        transcript_text,
        "transcript",
        source_name=transcript.filename or "",
    )

    manual_review_flags = []
    hard_rejection_reasons = []

    for doc_name, verdict in (
        ("Resume", resume_verdict),
        ("Transcript", transcript_verdict),
    ):
        if verdict.get("needs_manual_review"):
            manual_review_flags.append(f"{doc_name} requires manual review.")
        if not verdict.get("valid") and not verdict.get("needs_manual_review"):
            hard_rejection_reasons.append(f"{doc_name} check failed: {verdict.get('reason')}")

    if hard_rejection_reasons:
        reason = " ".join(hard_rejection_reasons).strip()
        send_rejection_email(
            to_email=email,
            applicant_name=f"{first_name} {last_name}".strip(),
            reason=reason,
        )
        return {
            "status": "received",
            "message": RECEIVED_MESSAGE,
        }

    try:
        resume_path = f"{uuid4()}_{_safe_filename(resume.filename)}"
        transcript_path = f"{uuid4()}_{_safe_filename(transcript.filename)}"
        resume_url = upload_file(
            bucket_name=STORAGE_BUCKET,
            file_path=resume_path,
            file_bytes=resume_bytes,
            content_type="application/pdf",
        )
        transcript_url = upload_file(
            bucket_name=STORAGE_BUCKET,
            file_path=transcript_path,
            file_bytes=transcript_bytes,
            content_type="application/pdf",
        )

        photo_url = None
        if photo and photo.filename and photo_bytes:
            photo_path = f"{uuid4()}_{_safe_filename(photo.filename)}"
            photo_url = upload_file(
                bucket_name=STORAGE_BUCKET,
                file_path=photo_path,
                file_bytes=photo_bytes,
                content_type=photo.content_type or "image/jpeg",
            )

        application_record = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "location": location,
            "city": city,
            "university": university,
            "degree": degree,
            "major": major,
            "cgpa": cgpa,
            "semester": semester,
            "class_ranking": class_ranking,
            "field": field,
            "selected_tracks": tracks,
            "resume_url": resume_url,
            "transcript_url": transcript_url,
            "photo_url": photo_url,
            "video_link": video_link,
            "status": "manual_review" if manual_review_flags else "pending",
        }
        storage_record = dict(application_record)
        if is_local_mode():
            storage_record["ai_resume_verdict"] = resume_verdict
            storage_record["ai_transcript_verdict"] = transcript_verdict
            storage_record["ai_summary"] = {
                "manual_review_required": bool(manual_review_flags),
                "manual_review_reasons": manual_review_flags,
            }

        saved = insert_application(storage_record)

        for track_name in tracks:
            manager_email = TRACK_MANAGERS.get(track_name)
            if manager_email:
                send_track_notification(
                    manager_email=manager_email,
                    track_name=track_name,
                    applicant=application_record,
                    review_status=application_record["status"],
                )
        send_received_email(
            to_email=email,
            applicant_name=f"{first_name} {last_name}".strip(),
        )

        return {
            "status": "received",
            "message": RECEIVED_MESSAGE,
            "application_id": saved.get("id"),
            "review_status": application_record["status"],
        }
    except Exception as exc:  # noqa: BLE001
        if "Bucket not found" in str(exc):
            raise HTTPException(
                status_code=500,
                detail=(
                    "Submission failed: Supabase storage bucket not found. "
                    f"Create bucket '{STORAGE_BUCKET}' or set SUPABASE_STORAGE_BUCKET in backend/.env."
                ),
            ) from exc
        raise HTTPException(status_code=500, detail=f"Submission failed: {exc}") from exc
