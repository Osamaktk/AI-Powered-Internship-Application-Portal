import io
import logging

import pdfplumber


logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Use pdfplumber to read all pages of the PDF and return
    combined text as a single string.
    Returns empty string if extraction fails.
    """
    if not file_bytes:
        return ""

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text_chunks = []
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_chunks.append(page_text.strip())
            return "\n\n".join(text_chunks).strip()
    except Exception as exc:  # noqa: BLE001
        logger.warning("PDF extraction failed: %s", exc)
        return ""
