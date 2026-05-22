import os
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime


GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
BRAND_NAME = "InternIQ"
BRAND_COLOR = "#1a56db"
SUPPORT_EMAIL = os.getenv("GMAIL_USER")
PORTAL_URL = os.getenv("PORTAL_URL", "http://localhost:5173")
MANAGER_NOTIFICATION_OVERRIDE_EMAIL = os.getenv("MANAGER_NOTIFICATION_OVERRIDE_EMAIL")


def _format_datetime(iso_string: str) -> str:
    """
    Convert "2026-05-20T14:32:00" -> "20 May 2026, 14:32 UTC"
    Returns the original string unchanged if parsing fails.
    """
    try:
        cleaned = str(iso_string or "").strip()
        if not cleaned:
            return ""
        normalized = cleaned.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        return parsed.strftime("%d %b %Y, %H:%M UTC")
    except Exception:
        return iso_string


def _format_tracks(selected_tracks_raw) -> str:
    """
    selected_tracks may arrive as a JSON string '["Track A","Track B"]'
    or already as a Python list.
    Always returns a comma-separated string: "Track A, Track B"
    """
    if isinstance(selected_tracks_raw, list):
        return ", ".join(str(item).strip() for item in selected_tracks_raw if str(item).strip())

    raw = str(selected_tracks_raw or "").strip()
    if not raw:
        return ""

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return ", ".join(str(item).strip() for item in parsed if str(item).strip())
    except Exception:
        pass

    return raw


def _normalized_password(password: str | None) -> str:
    return str(password or "").replace("-", "").replace(" ", "").strip()


def _resolve_manager_recipient(manager_email: str) -> str:
    override = str(MANAGER_NOTIFICATION_OVERRIDE_EMAIL or "").strip()
    if override:
        return override
    return str(manager_email or "").strip()


def _send_email(
    to: str,
    subject: str,
    html_body: str,
    attachment_path: str | None = None,
    attachment_filename: str | None = None,
) -> None:
    """
    Internal email sender.

    Parameters
    ----------
    to                  : recipient email address
    subject             : email subject line
    html_body           : full HTML string for the email body
    attachment_path     : absolute or relative path to a file to attach (optional)
    attachment_filename : the filename the recipient sees for the attachment (optional)

    Behaviour
    ---------
    - Always uses smtplib.SMTP("smtp.gmail.com", 587) with starttls()
    - Logs success and failure to stdout (print statements are fine for now)
    - Raises no exceptions to the caller - wraps everything in try/except and prints the error
    - If attachment_path is provided but the file does not exist on disk, log a warning
      and send the email WITHOUT the attachment rather than failing entirely
    - Uses MIMEMultipart("mixed") when an attachment is present,
      MIMEMultipart("alternative") when there is no attachment
    """
    try:
        sender = (GMAIL_USER or os.getenv("GMAIL_USER") or "").strip()
        app_password = _normalized_password(
            GMAIL_APP_PASSWORD or os.getenv("GMAIL_APP_PASSWORD")
        )
        if not sender or not app_password:
            raise RuntimeError("Missing GMAIL_USER or GMAIL_APP_PASSWORD.")

        has_attachment_requested = bool(attachment_path)
        has_attachment = has_attachment_requested and os.path.exists(str(attachment_path))

        if has_attachment_requested and not has_attachment:
            print(f"[EMAIL WARNING] Attachment not found at path: {attachment_path}")

        message = MIMEMultipart("mixed" if has_attachment else "alternative")
        message["From"] = sender
        message["To"] = to
        message["Subject"] = subject

        if has_attachment:
            body_part = MIMEMultipart("alternative")
            body_part.attach(MIMEText(html_body, "html"))
            message.attach(body_part)

            with open(str(attachment_path), "rb") as file_handle:
                attachment = MIMEBase("application", "octet-stream")
                attachment.set_payload(file_handle.read())
            encoders.encode_base64(attachment)

            visible_name = attachment_filename or os.path.basename(str(attachment_path))
            attachment.add_header(
                "Content-Disposition",
                f'attachment; filename="{visible_name}"',
            )
            message.attach(attachment)
        else:
            message.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, app_password)
            server.sendmail(sender, to, message.as_string())
        print(f"[EMAIL] Sent '{subject}' to {to}")
    except Exception as exc:
        print(f"[EMAIL ERROR] Failed to send to {to}: {exc}")


def send_track_notification(
    manager_email: str,
    track_name: str,
    applicant: dict,
    cv_filepath: str | None = None,
) -> None:
    """
    Send a professional notification email to the designated track manager.
    """
    try:
        target_recipient = _resolve_manager_recipient(manager_email)
        first_name = str(applicant.get("first_name", "")).strip()
        last_name = str(applicant.get("last_name", "")).strip()
        subject = (
            f"[InternIQ] New Application — {track_name} | {first_name} {last_name}".strip()
        )

        tracks_display = _format_tracks(applicant.get("selected_tracks"))
        submitted_display = _format_datetime(str(applicant.get("submitted_at", "")))
        cv_verdict = str(applicant.get("cv_ai_verdict", "")).strip()
        transcript_verdict = str(applicant.get("transcript_ai_verdict", "")).strip()
        cv_confidence = str(applicant.get("cv_ai_confidence", "")).strip()
        transcript_confidence = str(applicant.get("transcript_ai_confidence", "")).strip()
        cv_reason = str(applicant.get("cv_ai_reason", "")).strip()
        transcript_reason = str(applicant.get("transcript_ai_reason", "")).strip()

        both_valid = cv_verdict.lower() == "valid" and transcript_verdict.lower() == "valid"
        status_banner = (
            '<div style="background: #f0fdf4; border-left: 4px solid #16a34a; padding: 12px 16px; border-radius: 4px; margin-top: 16px;">'
            '<div style="font-size: 14px; font-weight: 700; color: #166534;">✅ AI Verification Passed — Both documents verified</div>'
            "</div>"
            if both_valid
            else '<div style="background: #fffbeb; border-left: 4px solid #d97706; padding: 12px 16px; border-radius: 4px; margin-top: 16px;">'
            '<div style="font-size: 14px; font-weight: 700; color: #92400e;">⚠️ Manual Review Required — See verification details</div>'
            "</div>"
        )

        cv_status_color = "#15803d" if cv_verdict.lower() == "valid" else "#dc2626"
        transcript_status_color = (
            "#15803d" if transcript_verdict.lower() == "valid" else "#dc2626"
        )
        cv_status_icon = "✅" if cv_verdict.lower() == "valid" else "❌"
        transcript_status_icon = "✅" if transcript_verdict.lower() == "valid" else "❌"

        attachment_exists = bool(cv_filepath and os.path.exists(str(cv_filepath)))
        attachment_section = ""
        if cv_filepath:
            attachment_note = (
                "📎 The applicant's CV is attached to this email."
                if attachment_exists
                else "📎 CV file unavailable — please request directly."
            )
            attachment_section = f"""
              <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; padding: 14px 16px; margin: 16px 24px 0;">
                <div style="font-size: 13px; color: #1e3a8a;">{attachment_note}</div>
              </div>
            """

        html_body = f"""
<!doctype html>
<html lang="en">
  <body style="margin: 0; padding: 24px 12px; background: #f1f5f9;">
    <div style="max-width: 620px; margin: 0 auto; font-family: Arial, sans-serif;">
      <div style="background-color: {BRAND_COLOR}; padding: 24px 32px;">
        <div style="font-size: 22px; font-weight: 700; color: #ffffff;">{BRAND_NAME}</div>
        <div style="font-size: 13px; color: #dbeafe; margin-top: 4px;">Track Manager Notification</div>
      </div>

      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-top: none; padding: 20px 24px;">
        <div style="font-size: 22px; color: #1e293b; font-weight: 700;">📋 New Internship Application</div>
        <div style="font-size: 14px; color: #475569; margin-top: 6px;">A new application has been submitted for your track.</div>
        <div style="margin-top: 12px;">
          <span style="display: inline-block; background: #dbeafe; color: #1d4ed8; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600;">● {track_name}</span>
        </div>
        {status_banner}
      </div>

      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; margin: 16px 0;">
        <div style="padding: 14px 16px; font-size: 14px; font-weight: 700; color: #0f172a;">Applicant Details</div>
        <table style="width: 100%; border-collapse: collapse;">
          <tr><td style="width: 38%; padding: 10px 16px; color: #64748b; font-size: 13px; font-weight: 600; background: #f8fafc; border-bottom: 1px solid #e2e8f0;">Full Name</td><td style="padding: 10px 16px; color: #1e293b; font-size: 14px; border-bottom: 1px solid #e2e8f0;">{first_name} {last_name}</td></tr>
          <tr><td style="width: 38%; padding: 10px 16px; color: #64748b; font-size: 13px; font-weight: 600; background: #f1f5f9; border-bottom: 1px solid #e2e8f0;">Email Address</td><td style="padding: 10px 16px; color: #1e293b; font-size: 14px; border-bottom: 1px solid #e2e8f0;">{str(applicant.get("email", "")).strip()}</td></tr>
          <tr><td style="width: 38%; padding: 10px 16px; color: #64748b; font-size: 13px; font-weight: 600; background: #f8fafc; border-bottom: 1px solid #e2e8f0;">Phone</td><td style="padding: 10px 16px; color: #1e293b; font-size: 14px; border-bottom: 1px solid #e2e8f0;">{str(applicant.get("phone", "")).strip()}</td></tr>
          <tr><td style="width: 38%; padding: 10px 16px; color: #64748b; font-size: 13px; font-weight: 600; background: #f1f5f9; border-bottom: 1px solid #e2e8f0;">University</td><td style="padding: 10px 16px; color: #1e293b; font-size: 14px; border-bottom: 1px solid #e2e8f0;">{str(applicant.get("university", "")).strip()}</td></tr>
          <tr><td style="width: 38%; padding: 10px 16px; color: #64748b; font-size: 13px; font-weight: 600; background: #f8fafc; border-bottom: 1px solid #e2e8f0;">Degree</td><td style="padding: 10px 16px; color: #1e293b; font-size: 14px; border-bottom: 1px solid #e2e8f0;">{str(applicant.get("degree", "")).strip()}</td></tr>
          <tr><td style="width: 38%; padding: 10px 16px; color: #64748b; font-size: 13px; font-weight: 600; background: #f1f5f9; border-bottom: 1px solid #e2e8f0;">Major</td><td style="padding: 10px 16px; color: #1e293b; font-size: 14px; border-bottom: 1px solid #e2e8f0;">{str(applicant.get("major", "")).strip()}</td></tr>
          <tr><td style="width: 38%; padding: 10px 16px; color: #64748b; font-size: 13px; font-weight: 600; background: #f8fafc; border-bottom: 1px solid #e2e8f0;">CGPA</td><td style="padding: 10px 16px; color: #1e293b; font-size: 14px; border-bottom: 1px solid #e2e8f0;">{str(applicant.get("cgpa", "")).strip()}</td></tr>
          <tr><td style="width: 38%; padding: 10px 16px; color: #64748b; font-size: 13px; font-weight: 600; background: #f1f5f9; border-bottom: 1px solid #e2e8f0;">Current Semester</td><td style="padding: 10px 16px; color: #1e293b; font-size: 14px; border-bottom: 1px solid #e2e8f0;">{str(applicant.get("current_semester", "")).strip()}</td></tr>
          <tr><td style="width: 38%; padding: 10px 16px; color: #64748b; font-size: 13px; font-weight: 600; background: #f8fafc; border-bottom: 1px solid #e2e8f0;">Applied Field</td><td style="padding: 10px 16px; color: #1e293b; font-size: 14px; border-bottom: 1px solid #e2e8f0;">{str(applicant.get("field", "")).strip()}</td></tr>
          <tr><td style="width: 38%; padding: 10px 16px; color: #64748b; font-size: 13px; font-weight: 600; background: #f1f5f9; border-bottom: 1px solid #e2e8f0;">Applied Track(s)</td><td style="padding: 10px 16px; color: #1e293b; font-size: 14px; border-bottom: 1px solid #e2e8f0;">{tracks_display}</td></tr>
          <tr><td style="width: 38%; padding: 10px 16px; color: #64748b; font-size: 13px; font-weight: 600; background: #f8fafc; border-bottom: 1px solid #e2e8f0;">Application ID</td><td style="padding: 10px 16px; color: #1e293b; font-size: 14px; border-bottom: 1px solid #e2e8f0; font-family: monospace;">{str(applicant.get("id", "")).strip()}</td></tr>
          <tr><td style="width: 38%; padding: 10px 16px; color: #64748b; font-size: 13px; font-weight: 600; background: #f1f5f9; border-bottom: 1px solid #e2e8f0;">Submitted At</td><td style="padding: 10px 16px; color: #1e293b; font-size: 14px; border-bottom: 1px solid #e2e8f0;">{submitted_display}</td></tr>
        </table>
      </div>

      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; margin: 16px 0;">
        <div style="padding: 14px 16px; font-size: 14px; font-weight: 700; color: #0f172a;">Document Verification</div>
        <table style="width: 100%; border-collapse: collapse;">
          <tr>
            <th style="text-align: left; padding: 10px 16px; font-size: 12px; color: #64748b; background: #f8fafc; border-bottom: 1px solid #e2e8f0;">Document</th>
            <th style="text-align: left; padding: 10px 16px; font-size: 12px; color: #64748b; background: #f8fafc; border-bottom: 1px solid #e2e8f0;">AI Verdict</th>
            <th style="text-align: left; padding: 10px 16px; font-size: 12px; color: #64748b; background: #f8fafc; border-bottom: 1px solid #e2e8f0;">Confidence</th>
            <th style="text-align: left; padding: 10px 16px; font-size: 12px; color: #64748b; background: #f8fafc; border-bottom: 1px solid #e2e8f0;">Note</th>
          </tr>
          <tr>
            <td style="padding: 10px 16px; font-size: 13px; color: #1e293b; border-bottom: 1px solid #e2e8f0;">CV/Resume</td>
            <td style="padding: 10px 16px; font-size: 13px; color: {cv_status_color}; font-weight: 700; border-bottom: 1px solid #e2e8f0;">{cv_status_icon} {cv_verdict or "Unknown"}</td>
            <td style="padding: 10px 16px; font-size: 13px; color: #1e293b; border-bottom: 1px solid #e2e8f0;">{cv_confidence or "N/A"}</td>
            <td style="padding: 10px 16px; font-size: 13px; color: #1e293b; border-bottom: 1px solid #e2e8f0;">{cv_reason or "No additional note."}</td>
          </tr>
          <tr>
            <td style="padding: 10px 16px; font-size: 13px; color: #1e293b;">Transcript</td>
            <td style="padding: 10px 16px; font-size: 13px; color: {transcript_status_color}; font-weight: 700;">{transcript_status_icon} {transcript_verdict or "Unknown"}</td>
            <td style="padding: 10px 16px; font-size: 13px; color: #1e293b;">{transcript_confidence or "N/A"}</td>
            <td style="padding: 10px 16px; font-size: 13px; color: #1e293b;">{transcript_reason or "No additional note."}</td>
          </tr>
        </table>
        {attachment_section}
      </div>

        <div style="background: #1e293b; color: #94a3b8; padding: 20px 32px; font-size: 12px; text-align: center;">
        <div>This is an automated notification from {BRAND_NAME}.</div>
        <div style="margin-top: 4px;">Please do not reply to this email.</div>
        <div style="margin-top: 4px;">© 2026 {BRAND_NAME} · All rights reserved</div>
        <div style="margin-top: 4px;">Track Manager assigned: {manager_email}</div>
        <div style="margin-top: 4px;">Notification delivered to: {target_recipient}</div>
      </div>
    </div>
  </body>
</html>
"""

        attachment_name = f"CV_{first_name}_{last_name}.pdf".replace(" ", "_")
        _send_email(
            to=target_recipient,
            subject=subject,
            html_body=html_body,
            attachment_path=cv_filepath,
            attachment_filename=attachment_name,
        )
    except Exception as exc:
        print(f"[EMAIL ERROR] Track notification failed for {manager_email}: {exc}")


def send_confirmation_to_applicant(applicant: dict) -> None:
    """
    Send a professional confirmation email to the applicant after successful submission.
    """
    try:
        first_name = str(applicant.get("first_name", "")).strip()
        last_name = str(applicant.get("last_name", "")).strip()
        subject = f"Your InternIQ Application Has Been Received — {first_name} {last_name}".strip()
        submitted_display = _format_datetime(str(applicant.get("submitted_at", "")))
        tracks_display = _format_tracks(applicant.get("selected_tracks"))
        application_id = str(applicant.get("id", "")).strip()
        to_email = str(applicant.get("email", "")).strip()

        html_body = f"""
<!doctype html>
<html lang="en">
  <body style="margin: 0; padding: 24px 12px; background: #f1f5f9;">
    <div style="max-width: 620px; margin: 0 auto; font-family: Arial, sans-serif;">
      <div style="background-color: {BRAND_COLOR}; padding: 24px 32px;">
        <div style="font-size: 22px; font-weight: 700; color: #ffffff;">{BRAND_NAME}</div>
        <div style="font-size: 13px; color: #dbeafe; margin-top: 4px;">Internship Application Portal</div>
      </div>

      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: none; padding: 20px 24px;">
        <div style="background: #f0fdf4; border-left: 4px solid #16a34a; padding: 14px 16px; border-radius: 4px;">
          <div style="font-size: 20px; color: #15803d; font-weight: 700;">✓ Application Successfully Submitted</div>
          <div style="font-size: 14px; color: #475569; margin-top: 6px;">Your application has been received and is under review by our team.</div>
        </div>

        <div style="margin-top: 18px; color: #1e293b; font-size: 14px; line-height: 1.7;">
          <p style="margin: 0 0 12px;">Dear {first_name} {last_name},</p>
          <p style="margin: 0 0 12px;">
            Thank you for applying to the SPS SpinnLabs Internship Programme through {BRAND_NAME}. We are pleased to confirm
            that your application has been successfully received and your documents have passed our verification process.
          </p>
          <p style="margin: 0;">
            Our team will carefully review your application and you will be contacted at this email address regarding the
            next steps. Please allow 5–7 business days for us to review your submission.
          </p>
        </div>
      </div>

      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; margin: 16px 0;">
        <div style="padding: 14px 16px; font-size: 14px; font-weight: 700; color: #0f172a;">Application Summary</div>
        <table style="width: 100%; border-collapse: collapse;">
          <tr><td style="width: 38%; padding: 10px 16px; color: #64748b; font-size: 13px; font-weight: 600; background: #f8fafc; border-bottom: 1px solid #e2e8f0;">Application ID</td><td style="padding: 10px 16px; border-bottom: 1px solid #e2e8f0;"><span style="font-family: monospace; font-size: 12px; color: #475569; background: #f1f5f9; padding: 2px 6px; border-radius: 3px;">{application_id}</span></td></tr>
          <tr><td style="width: 38%; padding: 10px 16px; color: #64748b; font-size: 13px; font-weight: 600; background: #f1f5f9; border-bottom: 1px solid #e2e8f0;">Submitted</td><td style="padding: 10px 16px; color: #1e293b; font-size: 14px; border-bottom: 1px solid #e2e8f0;">{submitted_display}</td></tr>
          <tr><td style="width: 38%; padding: 10px 16px; color: #64748b; font-size: 13px; font-weight: 600; background: #f8fafc; border-bottom: 1px solid #e2e8f0;">University</td><td style="padding: 10px 16px; color: #1e293b; font-size: 14px; border-bottom: 1px solid #e2e8f0;">{str(applicant.get("university", "")).strip()}</td></tr>
          <tr><td style="width: 38%; padding: 10px 16px; color: #64748b; font-size: 13px; font-weight: 600; background: #f1f5f9; border-bottom: 1px solid #e2e8f0;">Programme</td><td style="padding: 10px 16px; color: #1e293b; font-size: 14px; border-bottom: 1px solid #e2e8f0;">{str(applicant.get("degree", "")).strip()} in {str(applicant.get("major", "")).strip()}</td></tr>
          <tr><td style="width: 38%; padding: 10px 16px; color: #64748b; font-size: 13px; font-weight: 600; background: #f8fafc; border-bottom: 1px solid #e2e8f0;">Applied Track(s)</td><td style="padding: 10px 16px; color: #1e293b; font-size: 14px; border-bottom: 1px solid #e2e8f0;">{tracks_display}</td></tr>
          <tr><td style="width: 38%; padding: 10px 16px; color: #64748b; font-size: 13px; font-weight: 600; background: #f1f5f9;">Current Status</td><td style="padding: 10px 16px;"><span style="background: #fef9c3; color: #854d0e; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;">🟡 Under Review</span></td></tr>
        </table>
      </div>

      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; margin: 16px 0; padding: 16px 20px;">
        <div style="font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 12px;">What happens next</div>
        <div style="margin-bottom: 14px; overflow: hidden;">
          <div style="float: left; width: 28px; height: 28px; line-height: 28px; text-align: center; background: #dbeafe; color: #1d4ed8; border-radius: 50%; font-weight: 700; font-size: 13px;">1</div>
          <div style="margin-left: 40px;"><div style="font-size: 14px; font-weight: 700; color: #1e293b;">Application Review</div><div style="font-size: 13px; color: #475569; margin-top: 2px;">Our team reviews your submitted documents and application details.</div></div>
        </div>
        <div style="margin-bottom: 14px; overflow: hidden;">
          <div style="float: left; width: 28px; height: 28px; line-height: 28px; text-align: center; background: #dbeafe; color: #1d4ed8; border-radius: 50%; font-weight: 700; font-size: 13px;">2</div>
          <div style="margin-left: 40px;"><div style="font-size: 14px; font-weight: 700; color: #1e293b;">Shortlisting</div><div style="font-size: 13px; color: #475569; margin-top: 2px;">Shortlisted candidates will be contacted for an interview or further assessment.</div></div>
        </div>
        <div style="overflow: hidden;">
          <div style="float: left; width: 28px; height: 28px; line-height: 28px; text-align: center; background: #dbeafe; color: #1d4ed8; border-radius: 50%; font-weight: 700; font-size: 13px;">3</div>
          <div style="margin-left: 40px;"><div style="font-size: 14px; font-weight: 700; color: #1e293b;">Final Decision</div><div style="font-size: 13px; color: #475569; margin-top: 2px;">You will receive a final status update via email regardless of the outcome.</div></div>
        </div>
      </div>

      <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; padding: 16px 20px; margin: 16px 0;">
        <div style="font-size: 13px; color: #1e3a8a;">Have a question? Contact us at:</div>
        <div style="font-size: 14px; font-weight: 700; color: #1d4ed8; margin-top: 6px;">📧 {SUPPORT_EMAIL}</div>
        <div style="font-size: 12px; color: #1e3a8a; margin-top: 6px;">Please quote your Application ID in all correspondence.</div>
      </div>

      <div style="background: #1e293b; color: #94a3b8; padding: 20px 32px; font-size: 12px; text-align: center;">
        <div>This is an automated message. Please do not reply.</div>
        <div style="margin-top: 4px;">© 2026 {BRAND_NAME} · SPS SpinnLabs Internship Programme</div>
      </div>
    </div>
  </body>
</html>
"""

        _send_email(to=to_email, subject=subject, html_body=html_body)
    except Exception as exc:
        print(f"[EMAIL ERROR] Confirmation email failed for {applicant.get('email', '')}: {exc}")


def send_rejection_email(
    to_email: str,
    applicant_name: str,
    failed_document: str,
    reason: str,
    evidence: list[str] | None = None,
) -> None:
    """
    Send a professional rejection notice to the applicant when a document fails AI verification.
    """
    try:
        evidence = evidence or []
        evidence_items = "".join(
            f'<li style="margin: 4px 0;">{str(item)}</li>' for item in evidence
        ) or '<li style="margin: 4px 0;">No additional evidence provided.</li>'

        html_body = f"""
<!doctype html>
<html lang="en">
  <body style="margin: 0; padding: 24px 12px; background: #f1f5f9;">
    <div style="max-width: 620px; margin: 0 auto; font-family: Arial, sans-serif;">
      <div style="background-color: {BRAND_COLOR}; padding: 24px 32px;">
        <div style="font-size: 22px; font-weight: 700; color: #ffffff;">{BRAND_NAME}</div>
        <div style="font-size: 13px; color: #dbeafe; margin-top: 4px;">Internship Application Portal</div>
      </div>

      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: none; padding: 20px 24px;">
        <div style="background: #fffbeb; border-left: 4px solid #d97706; padding: 12px 16px; border-radius: 4px;">
          <div style="font-size: 15px; color: #92400e; font-weight: 700;">⚠️ Document Issue Detected</div>
        </div>
        <p style="margin: 16px 0 8px; font-size: 14px; color: #1e293b;">Dear {applicant_name},</p>
        <p style="margin: 0; font-size: 14px; color: #334155; line-height: 1.7;">
          Your {failed_document} upload could not be verified as the correct document type, and your application has not been submitted.
        </p>
      </div>

      <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 6px; padding: 16px 20px; margin: 16px 0;">
        <div style="font-size: 13px; color: #991b1b; margin-bottom: 6px;"><strong>Document Type Expected:</strong> {failed_document}</div>
        <div style="font-size: 13px; color: #991b1b; margin-bottom: 6px;"><strong>Issue Identified:</strong> {reason}</div>
        <div style="font-size: 13px; color: #991b1b;"><strong>Evidence:</strong></div>
        <ul style="font-size: 13px; color: #991b1b; margin: 8px 0 0 18px; padding: 0;">
          {evidence_items}
        </ul>
      </div>

      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; margin: 16px 0; padding: 16px 20px;">
        <div style="font-size: 14px; color: #1e293b; margin-bottom: 8px;">To complete your application, please:</div>
        <ol style="margin: 0 0 0 18px; padding: 0; font-size: 13px; color: #475569; line-height: 1.8;">
          <li>Ensure you are uploading your {failed_document} (not another document type)</li>
          <li>Make sure the PDF contains readable text (not a scanned image)</li>
          <li>Return to the application portal and resubmit</li>
        </ol>
        <div style="text-align: center; margin-top: 18px;">
          <a href="{PORTAL_URL}" style="display: inline-block; background: {BRAND_COLOR}; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 6px; font-size: 13px; font-weight: 700;">Return to Application</a>
        </div>
      </div>

      <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; padding: 16px 20px; margin: 16px 0;">
        <div style="font-size: 13px; color: #1e3a8a;">Have a question? Contact us at:</div>
        <div style="font-size: 14px; font-weight: 700; color: #1d4ed8; margin-top: 6px;">📧 {SUPPORT_EMAIL}</div>
      </div>

      <div style="background: #1e293b; color: #94a3b8; padding: 20px 32px; font-size: 12px; text-align: center;">
        <div>This is an automated message. Please do not reply.</div>
        <div style="margin-top: 4px;">© 2026 {BRAND_NAME} · SPS SpinnLabs Internship Programme</div>
      </div>
    </div>
  </body>
</html>
"""
        _send_email(
            to=to_email,
            subject="InternIQ Application — Document Upload Issue",
            html_body=html_body,
        )
    except Exception as exc:
        print(f"[EMAIL ERROR] Rejection email failed for {to_email}: {exc}")
