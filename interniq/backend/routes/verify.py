from fastapi import APIRouter, File, Form, UploadFile

from services.ai_verifier import verify_document_async
from services.pdf_extractor import extract_text_from_pdf


router = APIRouter(tags=["verification"])


@router.post("/verify-document")
async def verify_document_endpoint(
    file: UploadFile = File(...),
    expected_type: str = Form(...),
):
    try:
        normalized_type = (expected_type or "").strip().lower()
        if normalized_type not in {"cv", "transcript"}:
            return {
                "verified": False,
                "confidence": "low",
                "reason": "Invalid expected_type. Use 'cv' or 'transcript'.",
                "evidence": [],
            }

        if not (file.filename or "").lower().endswith(".pdf"):
            return {
                "verified": False,
                "confidence": "low",
                "reason": "Only PDF files are supported for verification.",
                "evidence": [],
            }

        file_bytes = await file.read()
        document_text = extract_text_from_pdf(file_bytes)
        verifier_type = "resume" if normalized_type == "cv" else "transcript"
        result = await verify_document_async(
            document_text=document_text,
            expected_type=verifier_type,
            source_name=file.filename or "",
        )

        valid = bool(result.get("valid"))
        confidence = str(result.get("confidence", "low")).strip().lower()
        if confidence not in {"high", "medium", "low"}:
            confidence = "low"
        reason = str(result.get("reason", "No reason provided.")).strip()
        evidence = result.get("evidence", [])
        if not isinstance(evidence, list):
            evidence = []

        if valid and confidence == "low":
            return {
                "verified": False,
                "confidence": "low",
                "reason": (
                    "Document could not be confirmed with sufficient certainty. "
                    "Please upload a clearer file."
                ),
                "evidence": [str(item) for item in evidence],
            }

        verified = valid and confidence in {"high", "medium"}
        return {
            "verified": verified,
            "confidence": confidence,
            "reason": reason,
            "evidence": [str(item) for item in evidence],
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "verified": False,
            "confidence": "low",
            "reason": f"Verification failed: {exc}",
            "evidence": [],
        }
