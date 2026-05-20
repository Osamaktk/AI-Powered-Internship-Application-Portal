import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict


logger = logging.getLogger(__name__)
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def _load_template(name: str) -> str:
    path = TEMPLATE_DIR / name
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _normalized_app_password(password: str) -> str:
    # Gmail app passwords are 16 chars; users often paste with separators.
    return password.replace("-", "").replace(" ", "").strip()


def _send_html_email(to_email: str, subject: str, html_body: str) -> None:
    gmail_user = (os.getenv("GMAIL_USER") or "").strip()
    gmail_password = _normalized_app_password(os.getenv("GMAIL_APP_PASSWORD") or "")

    if not gmail_user or not gmail_password:
        raise RuntimeError("Missing GMAIL_USER or GMAIL_APP_PASSWORD.")

    message = MIMEMultipart("alternative")
    message["From"] = gmail_user
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, to_email, message.as_string())


def _resolved_manager_email(manager_email: str) -> str:
    override = (os.getenv("MANAGER_NOTIFICATION_OVERRIDE_EMAIL") or "").strip()
    if override:
        return override
    return manager_email


def send_rejection_email(to_email: str, applicant_name: str, reason: str) -> None:
    """
    Send a polite rejection email to the applicant.
    """
    try:
        template = _load_template("rejection_email.html")
        html_body = template.format(
            applicant_name=applicant_name,
            reason=reason,
        )
        _send_html_email(
            to_email=to_email,
            subject="SPS InternIQ - Application Update",
            html_body=html_body,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to send rejection email: %s", exc)


def send_received_email(to_email: str, applicant_name: str) -> None:
    """
    Send applicant acknowledgement for received submission.
    """
    try:
        html_body = f"""
<!doctype html>
<html lang="en">
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #1f2937;">
    <h2 style="margin-bottom: 0.5rem;">Application Received</h2>
    <p>Dear {applicant_name},</p>
    <p>Your application has been received and we will be in touch very soon.</p>
    <p>Best regards,<br />InternIQ Team</p>
  </body>
</html>
"""
        _send_html_email(
            to_email=to_email,
            subject="SPS InternIQ - Application Received",
            html_body=html_body,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to send received email: %s", exc)


def send_track_notification(
    manager_email: str,
    track_name: str,
    applicant: Dict[str, str],
    review_status: str = "pending",
) -> None:
    """
    Send notification to the track manager.
    """
    try:
        final_recipient = _resolved_manager_email(manager_email)
        is_manual_review = review_status == "manual_review"
        status_label = "Manual Review Required" if is_manual_review else "AI Verified"
        status_note = (
            "Documents could not be fully auto-verified and need manual review."
            if is_manual_review
            else "Documents have been AI-verified as valid."
        )

        template = _load_template("notification_email.html")
        html_body = template.format(
            track_name=track_name,
            first_name=applicant.get("first_name", ""),
            last_name=applicant.get("last_name", ""),
            email=applicant.get("email", ""),
            university=applicant.get("university", ""),
            degree=applicant.get("degree", ""),
            major=applicant.get("major", ""),
            cgpa=applicant.get("cgpa", ""),
            semester=applicant.get("current_semester", "") or applicant.get("semester", ""),
            status_label=status_label,
            status_note=status_note,
            assigned_manager_email=manager_email,
            actual_recipient_email=final_recipient,
        )

        subject = (
            f"New InternIQ Application (Manual Review) - {track_name}"
            if is_manual_review
            else f"New InternIQ Application - {track_name}"
        )
        _send_html_email(
            to_email=final_recipient,
            subject=subject,
            html_body=html_body,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to send track notification: %s", exc)
