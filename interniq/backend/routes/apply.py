import json
import re
from datetime import datetime
from pathlib import Path
from typing import List
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from config.track_managers import TRACK_MANAGERS
from database.db import insert_application
from services.ai_verifier import verify_document_async
from services.email_service import (
    send_received_email,
    send_rejection_email,
    send_track_notification,
)
from services.pdf_extractor import extract_text_from_pdf


router = APIRouter(tags=["applications"])

MAX_PDF_BYTES = 5 * 1024 * 1024
MAX_PHOTO_BYTES = 2 * 1024 * 1024
ALLOWED_PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
BACKEND_ROOT = Path(__file__).resolve().parent.parent
CV_UPLOAD_DIR = BACKEND_ROOT / "uploads" / "cv"
TRANSCRIPT_UPLOAD_DIR = BACKEND_ROOT / "uploads" / "transcripts"
PHOTO_UPLOAD_DIR = BACKEND_ROOT / "uploads" / "photos"


def _clean(value: str | None) -> str:
    return str(value or "").strip()


def _parse_selected_tracks(raw: str) -> List[str]:
    payload = _clean(raw)
    if not payload:
        return []
    try:
        parsed = json.loads(payload)
        if isinstance(parsed, list):
            return [_clean(item) for item in parsed if _clean(item)]
    except json.JSONDecodeError:
        pass
    return [_clean(item) for item in payload.split(",") if _clean(item)]


def _sanitize_filename(original_filename: str, force_extension: str | None = None) -> str:
    filename = Path(_clean(original_filename) or "file").name
    base_name = filename
    extension = ""
    if "." in filename:
        base_name = filename.rsplit(".", 1)[0]
        extension = f".{filename.rsplit('.', 1)[1].lower()}"
    if force_extension:
        extension = force_extension
    safe_base = re.sub(r"[^a-zA-Z0-9_-]", "", base_name)
    if not safe_base:
        safe_base = "file"
    return f"{safe_base}{extension}"


def _validate_pdf(file: UploadFile, file_bytes: bytes, label: str) -> None:
    filename = _clean(file.filename).lower()
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail=f"{label} must be a PDF file.")
    if len(file_bytes) > MAX_PDF_BYTES:
        raise HTTPException(status_code=400, detail=f"{label} exceeds 5MB size limit.")


def _save_file(file_bytes: bytes, target_dir: Path, sanitized_filename: str) -> str:
    target_dir.mkdir(parents=True, exist_ok=True)
    unique_name = f"{uuid4()}_{sanitized_filename}"
    full_path = target_dir / unique_name
    full_path.write_bytes(file_bytes)
    return full_path.relative_to(BACKEND_ROOT).as_posix()


def _normalize_ai_result(result: dict) -> dict:
    verdict = "Valid" if bool(result.get("valid")) else "Invalid"
    confidence_raw = _clean(result.get("confidence")).lower()
    if confidence_raw == "high":
        confidence = "High"
    elif confidence_raw == "medium":
        confidence = "Medium"
    else:
        confidence = "Low"
    return {
        "verdict": verdict,
        "confidence": confidence,
        "reason": _clean(result.get("reason")),
        "is_passed": verdict == "Valid" and confidence in {"High", "Medium"},
    }


@router.post("/apply")
async def submit_application(
    internship_year: str = Form("2026"),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    location: str = Form("PK"),
    city: str = Form(""),
    university: str = Form(""),
    degree: str = Form(""),
    major: str = Form(""),
    cgpa: str = Form(""),
    semester: str = Form(""),
    current_semester: str = Form(""),
    class_ranking: str = Form(""),
    field: str = Form(""),
    selected_tracks: str = Form(...),
    video_link: str = Form(""),
    cv: UploadFile = File(...),
    transcript: UploadFile = File(...),
    photo: UploadFile | None = File(default=None),
):
    tracks = _parse_selected_tracks(selected_tracks)
    if not tracks:
        raise HTTPException(status_code=400, detail="Please select at least one track.")
    if len(tracks) > 3:
        raise HTTPException(status_code=400, detail="You can select up to 3 tracks only.")

    cv_bytes = await cv.read()
    transcript_bytes = await transcript.read()
    _validate_pdf(cv, cv_bytes, "CV")
    _validate_pdf(transcript, transcript_bytes, "Transcript")

    photo_bytes = b""
    if photo and _clean(photo.filename):
        photo_bytes = await photo.read()
        if len(photo_bytes) > MAX_PHOTO_BYTES:
            raise HTTPException(status_code=400, detail="Photo exceeds 2MB size limit.")
        photo_extension = Path(_clean(photo.filename)).suffix.lower()
        if photo_extension not in ALLOWED_PHOTO_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Photo must be JPG, JPEG, PNG, or GIF.",
            )

    cv_text = extract_text_from_pdf(cv_bytes)
    transcript_text = extract_text_from_pdf(transcript_bytes)

    cv_verification_raw = await verify_document_async(
        document_text=cv_text,
        expected_type="resume",
        source_name=_clean(cv.filename),
    )
    transcript_verification_raw = await verify_document_async(
        document_text=transcript_text,
        expected_type="transcript",
        source_name=_clean(transcript.filename),
    )

    cv_verification = _normalize_ai_result(cv_verification_raw)
    transcript_verification = _normalize_ai_result(transcript_verification_raw)

    if not cv_verification["is_passed"] or not transcript_verification["is_passed"]:
        reason_parts = []
        if not cv_verification["is_passed"]:
            reason_parts.append(f"CV check failed: {cv_verification['reason']}")
        if not transcript_verification["is_passed"]:
            reason_parts.append(
                f"Transcript check failed: {transcript_verification['reason']}"
            )
        reason = " ".join(part for part in reason_parts if part).strip() or (
            "Document verification failed."
        )
        send_rejection_email(
            to_email=_clean(email),
            applicant_name=f"{_clean(first_name)} {_clean(last_name)}".strip(),
            reason=reason,
        )
        return {"status": "rejected", "reason": reason}

    cv_original_filename = _clean(cv.filename)
    transcript_original_filename = _clean(transcript.filename)
    photo_original_filename = _clean(photo.filename) if photo else ""

    cv_saved_path = _save_file(
        file_bytes=cv_bytes,
        target_dir=CV_UPLOAD_DIR,
        sanitized_filename=_sanitize_filename(cv_original_filename, force_extension=".pdf"),
    )
    transcript_saved_path = _save_file(
        file_bytes=transcript_bytes,
        target_dir=TRANSCRIPT_UPLOAD_DIR,
        sanitized_filename=_sanitize_filename(
            transcript_original_filename,
            force_extension=".pdf",
        ),
    )

    photo_saved_path = ""
    if photo and photo_original_filename and photo_bytes:
        photo_saved_path = _save_file(
            file_bytes=photo_bytes,
            target_dir=PHOTO_UPLOAD_DIR,
            sanitized_filename=_sanitize_filename(photo_original_filename),
        )

    application_id = str(uuid4())
    submitted_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    effective_semester = _clean(current_semester or semester)
    application_row = {
        "id": application_id,
        "submitted_at": submitted_at,
        "status": "Pending",
        "first_name": _clean(first_name),
        "last_name": _clean(last_name),
        "email": _clean(email),
        "phone": _clean(phone),
        "location": _clean(location),
        "city": _clean(city),
        "university": _clean(university),
        "degree": _clean(degree),
        "major": _clean(major),
        "cgpa": _clean(cgpa),
        "current_semester": effective_semester,
        "class_ranking": _clean(class_ranking),
        "field": _clean(field),
        "selected_tracks": json.dumps(tracks, separators=(",", ":")),
        "cv_filename": cv_original_filename,
        "cv_filepath": cv_saved_path,
        "transcript_filename": transcript_original_filename,
        "transcript_filepath": transcript_saved_path,
        "photo_filename": photo_original_filename,
        "photo_filepath": photo_saved_path,
        "cv_ai_verdict": cv_verification["verdict"],
        "cv_ai_confidence": cv_verification["confidence"],
        "cv_ai_reason": cv_verification["reason"],
        "transcript_ai_verdict": transcript_verification["verdict"],
        "transcript_ai_confidence": transcript_verification["confidence"],
        "transcript_ai_reason": transcript_verification["reason"],
        "video_link": _clean(video_link),
        "internship_year": _clean(internship_year),
    }

    insert_application(application_row)

    for track_name in tracks:
        manager_email = TRACK_MANAGERS.get(track_name)
        if manager_email:
            send_track_notification(
                manager_email=manager_email,
                track_name=track_name,
                applicant=application_row,
                review_status=application_row["status"],
            )
    send_received_email(
        to_email=application_row["email"],
        applicant_name=f"{application_row['first_name']} {application_row['last_name']}".strip(),
    )

    return {
        "status": "accepted",
        "message": "Application submitted successfully",
        "application_id": application_id,
    }
