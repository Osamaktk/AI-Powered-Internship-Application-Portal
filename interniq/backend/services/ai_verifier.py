from __future__ import annotations

import asyncio
import json
import os
import re
from typing import Any
from urllib import error as url_error
from urllib import request as url_request

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "anthropic/claude-sonnet-4"
MIN_TEXT_LENGTH = 50
HEAD_CHARS = 8000
TAIL_CHARS = 4000

SYSTEM_PROMPT = """
You are a strict document type verifier.
Return JSON only. No markdown and no extra text.
Required JSON shape:
{
  "valid": true or false,
  "reason": "short reason",
  "confidence": "high" or "medium" or "low",
  "evidence": ["phrase 1", "phrase 2"]
}
"""

CHECKLISTS: dict[str, str] = {
    "resume": (
        "A resume should usually include experience, skills, education, "
        "projects/certifications, and contact details. It should not look like "
        "an academic transcript."
    ),
    "transcript": (
        "A transcript should usually include course names/codes, grades, semester "
        "records, GPA/CGPA, and institutional context. It should not look like a resume."
    ),
}

SIGNALS: dict[str, dict[str, list[str]]] = {
    "resume": {
        "positive": [
            "experience",
            "skills",
            "employment",
            "objective",
            "summary",
            "certification",
            "linkedin",
            "github",
            "project",
            "achievement",
        ],
        "negative": [
            "cgpa",
            "gpa",
            "credit hour",
            "course code",
            "semester",
            "grade",
            "registrar",
            "transcript",
        ],
    },
    "transcript": {
        "positive": [
            "gpa",
            "cgpa",
            "credit hour",
            "semester",
            "grade",
            "course code",
            "transcript",
            "registrar",
            "academic record",
        ],
        "negative": [
            "work experience",
            "skills",
            "objective",
            "linkedin",
            "github",
            "certifications",
        ],
    },
}

FILENAME_HINTS: dict[str, list[str]] = {
    "resume": ["resume", "cv", "curriculum vitae"],
    "transcript": ["transcript", "marksheet", "grade", "semester", "result"],
}


def _fallback_invalid(reason: str, needs_manual_review: bool = False) -> dict[str, Any]:
    return {
        "valid": False,
        "reason": reason,
        "confidence": "low",
        "evidence": [],
        "needs_manual_review": needs_manual_review,
    }


def _heuristic_prescreen(text: str, expected_type: str) -> dict[str, Any] | None:
    lower = text.lower()
    signals = SIGNALS.get(expected_type, {})
    positives = signals.get("positive", [])
    negatives = signals.get("negative", [])
    pos_hits = sum(1 for item in positives if item in lower)
    neg_hits = sum(1 for item in negatives if item in lower)

    if neg_hits >= 4 and pos_hits <= 1:
        other = "transcript" if expected_type == "resume" else "resume"
        return {
            "valid": False,
            "reason": (
                f"The document strongly resembles a {other} instead of a {expected_type}."
            ),
            "confidence": "high",
            "evidence": [
                f"Detected {neg_hits} {other}-like markers and only {pos_hits} {expected_type}-like markers."
            ],
        }
    return None


def _smart_sample(text: str) -> str:
    if len(text) <= HEAD_CHARS + TAIL_CHARS:
        return text
    head = text[:HEAD_CHARS]
    tail = text[-TAIL_CHARS:]
    return f"{head}\n\n[... middle omitted for length ...]\n\n{tail}"


def _build_user_prompt(sampled_text: str, expected_type: str, retry_hint: str = "") -> str:
    prompt = (
        f"Expected document type: {expected_type}\n\n"
        f"Checklist: {CHECKLISTS[expected_type]}\n\n"
        "Assess whether the document matches the expected type.\n"
        "Use structural evidence from the text.\n\n"
    )
    if retry_hint:
        prompt += (
            f"Previous pass had low confidence: {retry_hint}\n"
            "Run a second, stricter pass.\n\n"
        )
    prompt += f"Document text:\n---\n{sampled_text}\n---"
    return prompt


def _extract_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def _normalize_confidence(value: Any) -> str:
    conf = str(value or "").strip().lower()
    return conf if conf in {"high", "medium", "low"} else "low"


def _normalize_result(raw: dict[str, Any]) -> dict[str, Any]:
    evidence = raw.get("evidence", [])
    if not isinstance(evidence, list):
        evidence = []
    confidence = _normalize_confidence(raw.get("confidence"))
    return {
        "valid": bool(raw.get("valid", False)),
        "reason": str(raw.get("reason", "")).strip() or "No reason provided.",
        "confidence": confidence,
        "evidence": [str(item) for item in evidence],
        "needs_manual_review": confidence == "low",
    }


def _has_filename_hint(source_name: str, expected_type: str) -> bool:
    lowered_name = (source_name or "").strip().lower()
    if not lowered_name:
        return False
    return any(
        hint in lowered_name for hint in FILENAME_HINTS.get(expected_type, [])
    )


def _short_text_result(source_name: str, expected_type: str) -> dict[str, Any]:
    if _has_filename_hint(source_name, expected_type):
        return {
            "valid": True,
            "reason": (
                "Document appears to be image-based or scanned. "
                "Auto-verification will continue via manual review."
            ),
            "confidence": "low",
            "evidence": [
                "Very little extractable text found in PDF.",
                f"Filename matches expected type ({expected_type}).",
            ],
            "needs_manual_review": True,
        }

    return _fallback_invalid(
        "Document text is empty or too short for reliable AI verification.",
        needs_manual_review=True,
    )


def _get_openrouter_key() -> str:
    return (
        os.getenv("OPENROUTER_API_KEY")
        or os.getenv("OPENROUTER_KEY")
        or os.getenv("OPEN_ROUTER_API_KEY")
        or ""
    ).strip()


def _call_openrouter(user_prompt: str) -> dict[str, Any]:
    api_key = _get_openrouter_key()
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set.")

    model = os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 600,
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    app_url = os.getenv("OPENROUTER_HTTP_REFERER")
    app_name = os.getenv("OPENROUTER_APP_NAME")
    if app_url:
        headers["HTTP-Referer"] = app_url
    if app_name:
        headers["X-Title"] = app_name

    request_obj = url_request.Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with url_request.urlopen(request_obj, timeout=75) as response:
            body = response.read().decode("utf-8")
    except url_error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(
            f"OpenRouter HTTP {exc.code}: {error_body[:500]}"
        ) from exc
    except url_error.URLError as exc:
        raise RuntimeError(f"OpenRouter request failed: {exc}") from exc

    parsed = json.loads(body)
    choices = parsed.get("choices") or []
    if not choices:
        raise RuntimeError("OpenRouter returned no choices.")

    message = choices[0].get("message", {})
    content = message.get("content", "")
    if isinstance(content, list):
        text = ""
        for item in content:
            if isinstance(item, dict):
                text += str(item.get("text", ""))
            else:
                text += str(item)
        content = text

    return _extract_json(str(content))


def verify_document(
    document_text: str,
    expected_type: str,
    source_name: str = "",
) -> dict[str, Any]:
    expected_type = (expected_type or "").strip().lower()
    if expected_type not in {"resume", "transcript"}:
        return _fallback_invalid("Unsupported document type requested for verification.")

    cleaned = (document_text or "").strip()
    if len(cleaned) < MIN_TEXT_LENGTH:
        return _short_text_result(source_name, expected_type)

    heuristic = _heuristic_prescreen(cleaned, expected_type)
    if heuristic is not None:
        return heuristic

    sampled = _smart_sample(cleaned)

    try:
        first_prompt = _build_user_prompt(sampled, expected_type)
        first_result = _normalize_result(_call_openrouter(first_prompt))

        if first_result["confidence"] == "low":
            retry_prompt = _build_user_prompt(
                sampled,
                expected_type,
                retry_hint=first_result["reason"],
            )
            retry_result = _normalize_result(_call_openrouter(retry_prompt))
            if retry_result["confidence"] != "low":
                retry_result["needs_manual_review"] = False
            return retry_result

        return first_result
    except Exception as exc:  # noqa: BLE001
        return _fallback_invalid(
            f"AI verification failed: {exc}",
            needs_manual_review=True,
        )


async def verify_document_async(
    document_text: str,
    expected_type: str,
    source_name: str = "",
) -> dict[str, Any]:
    return await asyncio.to_thread(verify_document, document_text, expected_type, source_name)
