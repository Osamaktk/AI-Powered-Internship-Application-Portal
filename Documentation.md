
## AI-Powered Internship Application Portal
### Project Documentation — v1.0

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Key Features](#3-key-features)
4. [System Architecture](#4-system-architecture)
5. [Tech Stack](#5-tech-stack)
6. [Project Structure](#6-project-structure)
7. [Application Flow](#7-application-flow)
8. [AI Document Verification Mechanism](#8-ai-document-verification-mechanism)
9. [Email Notification Mechanism](#9-email-notification-mechanism)
10. [Database Schema](#10-database-schema)
11. [API Reference](#11-api-reference)
12. [Form Fields Reference](#12-form-fields-reference)
13. [Track Manager Mapping](#13-track-manager-mapping)
14. [Environment Variables](#14-environment-variables)
15. [Setup & Installation](#15-setup--installation)
16. [Security Considerations](#16-security-considerations)
17. [Known Limitations & Future Improvements](#17-known-limitations--future-improvements)

---

## 1. Project Overview

**InternIQ** is a full-stack web application that simulates a professional internship application portal, modelled after the SPS SpinnLabs Internship Program page. It mirrors the real portal's form fields, track selection structure, and document upload requirements — and layers an AI-powered verification engine on top to ensure applicants upload the correct documents.

The name **InternIQ** reflects the system's core value: an intelligent (IQ) internship (Intern) gateway that makes the screening process smarter and more automated.

> Built as a prototype for the SPS SpinnLabs internship task, 2026.

---

## 2. Problem Statement

Traditional internship portals accept any document uploaded by an applicant without checking whether it is actually what was requested. A student might upload their project essay when a transcript is required, or upload a random PDF as their resume. This wastes the time of reviewers who must manually check every document before assessing the application.

**InternIQ solves this by:**
- Automatically reading each uploaded PDF using text extraction
- Sending the extracted content to an AI model to assess document type
- Rejecting the application immediately if the wrong document is uploaded
- Notifying the applicant of the exact reason for rejection
- Only saving applications that pass document verification
- Alerting the relevant track manager the moment a valid application arrives

---

## 3. Key Features

| Feature | Description |
|---|---|
| Multi-section application form | Mirrors the SPS internship portal with all original fields |
| AI document verification | Claude API reads and classifies uploaded PDFs |
| Auto-rejection with reason | Wrong document = instant rejection email to applicant |
| Track manager notification | Email alert sent to the person responsible for the applied track |
| Supabase storage | Verified documents stored securely in cloud storage |
| Admin API | Endpoints to list and view all submitted applications |
| Up to 3 tracks | Students can apply to up to 3 tracks across Projects, Competencies, Specializations |

---

## 4. System Architecture

InternIQ is built on a three-tier architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      PRESENTATION TIER                       │
│                React + Tailwind CSS (Vite)                   │
│        Multi-section form · File uploads · Status UI         │
└─────────────────────┬───────────────────────────────────────┘
                      │  HTTP multipart/form-data (POST /apply)
┌─────────────────────▼───────────────────────────────────────┐
│                      APPLICATION TIER                         │
│                    Python FastAPI                             │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ PDF Extractor│  │ AI Verifier  │  │  Email Service   │   │
│  │ (pdfplumber) │  │ (Claude API) │  │ (Gmail SMTP)     │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │  REST API (supabase-py)
┌─────────────────────▼───────────────────────────────────────┐
│                        DATA TIER                              │
│                       Supabase                               │
│         PostgreSQL database · File storage buckets           │
└─────────────────────────────────────────────────────────────┘
```

### Component Roles

**Frontend (React + Vite)**
The student-facing UI. Renders the full application form, handles client-side validation, manages file selection, sends the form to the backend as `multipart/form-data`, and displays success or rejection feedback.

**Backend (FastAPI)**
The core processing engine. Receives submissions, orchestrates document verification, routes email notifications, and persists valid applications to the database. Exposes REST API endpoints consumed by both the frontend and the admin interface.

**AI Verifier (Claude API)**
A sub-service within the backend that receives extracted PDF text and a document type label, then returns a structured JSON verdict — `valid: true/false` with a human-readable reason. This is the intelligence layer that makes InternIQ different from a standard portal.

**Email Service (Gmail SMTP)**
Sends two categories of emails using Python's built-in `smtplib` library over TLS: rejection notices to applicants (with the AI's reason), and new-application alerts to the relevant track manager(s).

**Supabase**
Provides two services: a PostgreSQL database table (`applications`) for structured application data, and a storage bucket (`interniq-docs`) for the uploaded PDF files and photos. The backend communicates with Supabase using the official `supabase-py` client library.

---

## 5. Tech Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Frontend framework | React | 18+ | Component-based UI |
| Frontend build tool | Vite | 5+ | Fast dev server + bundler |
| CSS framework | Tailwind CSS | 3+ | Utility-first styling |
| Backend framework | FastAPI | 0.111+ | Async REST API |
| ASGI server | Uvicorn | 0.29+ | Run FastAPI in dev |
| PDF parsing | pdfplumber | 0.11+ | Extract text from PDF files |
| AI API | Anthropic Claude | claude-sonnet-4-20250514 | Document verification |
| Database | Supabase (PostgreSQL) | — | Persist applications |
| File storage | Supabase Storage | — | Store uploaded documents |
| Email | smtplib (stdlib) | built-in | Gmail SMTP over TLS |
| Config management | python-dotenv | 1.0+ | Load `.env` variables |
| HTTP client | httpx | 0.27+ | Async HTTP requests |
| Form parsing | python-multipart | 0.0.9+ | Handle file uploads in FastAPI |

---

## 6. Project Structure

```
interniq/
│
├── backend/
│   ├── main.py                      # FastAPI app, CORS, router registration
│   │
│   ├── routes/
│   │   ├── apply.py                 # POST /apply — main submission handler
│   │   └── admin.py                 # GET /applications, GET /applications/{id}
│   │
│   ├── services/
│   │   ├── pdf_extractor.py         # Read PDF bytes → plain text
│   │   ├── ai_verifier.py           # Send text to Claude → verdict JSON
│   │   ├── email_service.py         # Gmail SMTP sender (rejection + notification)
│   │   └── supabase_client.py       # DB insert + storage upload helpers
│   │
│   ├── models/
│   │   └── application.py           # Pydantic request/response schemas
│   │
│   ├── config/
│   │   └── track_managers.py        # Dict: track name → manager email
│   │
│   ├── templates/
│   │   ├── rejection_email.html     # HTML template for rejection email
│   │   └── notification_email.html  # HTML template for track manager alert
│   │
│   ├── .env                         # Secret keys (not committed to git)
│   ├── .gitignore
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                  # Root component, form state
│   │   ├── components/
│   │   │   ├── PersonalInfoSection.jsx
│   │   │   ├── TrackSelectionSection.jsx
│   │   │   ├── DocumentUploadSection.jsx
│   │   │   └── SubmitSection.jsx
│   │   ├── hooks/
│   │   │   └── useFormSubmit.js     # Handles FormData build + API call
│   │   └── api/
│   │       └── client.js            # Axios/fetch wrapper for backend
│   │
│   ├── index.html
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── package.json
│
└── README.md
```

---

## 7. Application Flow

The complete lifecycle of a student's submission:

```
Student fills form + uploads PDFs
            │
            ▼
Frontend builds FormData object and POSTs to /apply
            │
            ▼
FastAPI receives multipart/form-data
            │
            ▼
Basic file validation
(is it PDF? is it under 5MB?)
            │
       ┌────┴────┐
      Fail      Pass
       │         │
       ▼         ▼
   400 error   Extract text from resume PDF
               (pdfplumber)
                    │
                    ▼
               Send resume text to Claude API
               "Is this a resume?" → {valid, reason}
                    │
               ┌────┴────┐
              No         Yes
               │          │
               ▼          ▼
         Send rejection  Extract text from transcript PDF
         email to        (pdfplumber)
         applicant            │
               │              ▼
               │         Send transcript text to Claude API
               │         "Is this a transcript?" → {valid, reason}
               │              │
               │         ┌────┴────┐
               │        No         Yes
               │         │          │
               │         ▼          ▼
               │   Send rejection  Upload both PDFs to
               │   email to        Supabase Storage
               │   applicant            │
               │                       ▼
               │               Insert application record
               │               into Supabase DB
               │                       │
               │                       ▼
               │               Loop through selected tracks:
               │               Send notification email to
               │               each track manager
               │                       │
               └───────────────────────┤
                                       ▼
                              Return response to frontend
                         (status: accepted / rejected + reason)
                                       │
                                       ▼
                         Frontend shows success or rejection UI
```

---

## 8. AI Document Verification Mechanism

This is InternIQ's core innovation. Here is exactly how it works:

### Step 1 — PDF Text Extraction

When a PDF is uploaded, `pdfplumber` reads every page and extracts all text content. The result is a single string of raw text from the document. If the PDF is scanned (image-based) or encrypted, extraction may return an empty string — in which case the document is flagged as unverifiable and rejected.

```python
import pdfplumber
import io

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()
```

### Step 2 — AI Verification Prompt

The extracted text and the expected document type are sent to the Claude API. The system prompt enforces a strict JSON-only response. The user prompt explains what type of document is expected and asks the model to assess whether the provided text matches.

**System prompt:**
```
You are a document classification expert. You will receive the text content
of an uploaded document and the type of document that was expected.
Your task is to determine whether the uploaded document matches the expected type.
Respond ONLY with a JSON object. No markdown, no preamble, no explanation outside the JSON.
Format: {"valid": true/false, "reason": "short explanation", "confidence": "high/medium/low"}
```

**User prompt (for transcript verification):**
```
Expected document type: TRANSCRIPT

A transcript should contain: student name, university name, course/subject names,
credit hours, grades or marks, GPA or CGPA, semester or academic year records.

Document text:
---
{extracted_text[:3000]}
---

Is this document a valid academic transcript? Respond in JSON only.
```

### Step 3 — Verdict Processing

The backend parses the JSON response:
- `valid: true` → proceed to save
- `valid: false` → trigger rejection flow, include `reason` in the rejection email

```python
import anthropic, json

def verify_document(document_text: str, expected_type: str) -> dict:
    if len(document_text.strip()) < 50:
        return {"valid": False, "reason": "Document appears to be empty or unreadable.", "confidence": "high"}

    client = anthropic.Anthropic()
    prompts = {
        "resume": "A resume/CV should contain: applicant name, contact info, work experience, skills, education history, and optionally projects or certifications.",
        "transcript": "A transcript should contain: student name, university, course names, credit hours, grades, GPA/CGPA, semester or year records."
    }
    description = prompts.get(expected_type, "")

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system="You are a document classifier. Respond ONLY with JSON: {\"valid\": true/false, \"reason\": \"...\", \"confidence\": \"high/medium/low\"}",
        messages=[{
            "role": "user",
            "content": f"Expected type: {expected_type.upper()}\n{description}\n\nDocument text:\n---\n{document_text[:3000]}\n---\nIs this a valid {expected_type}?"
        }]
    )

    raw = message.content[0].text.strip()
    return json.loads(raw)
```

### Why This Works

The AI model has been trained on millions of documents and understands the structural and semantic patterns of different document types. A transcript contains patterns like "GPA: 3.8", "COSC 301 - Advanced Algorithms - A", "Semester 4". An essay does not. Even if a student renames their essay file as "transcript.pdf", the content analysis will catch it.

---

## 9. Email Notification Mechanism

InternIQ sends emails using Python's built-in `smtplib` library over TLS to Gmail's SMTP server. No external email library or paid service is required for testing.

### Gmail Configuration

1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account → Security → App Passwords
3. Generate a 16-character app password for "Mail"
4. Store it in `.env` as `GMAIL_APP_PASSWORD`

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

def _send_email(to: str, subject: str, html_body: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = to
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
```

### Email Type 1 — Rejection Notice (to applicant)

Triggered when AI returns `valid: false` for either document.

**Subject:** `SPS InternIQ — Application Update`

**Content includes:**
- Applicant's first name
- Which document failed (resume or transcript)
- The AI's reason for rejection
- Instructions to reapply with the correct document
- Contact email for questions

### Email Type 2 — Track Manager Notification

Triggered after a valid application is saved to the database, once per selected track.

**Subject:** `New InternIQ Application — {Track Name}`

**Content includes:**
- Applicant full name
- University and degree
- CGPA and current semester
- Major field of study
- Track applied to
- Note that documents have been AI-verified
- Date and time of application

### Multiple Track Handling

If a student selects 3 tracks (maximum allowed), 3 separate notification emails are sent — one to each corresponding track manager. The lookup is done via the `TRACK_MANAGERS` dictionary in `config/track_managers.py`.

---

## 10. Database Schema

### Table: `applications`

```sql
CREATE TABLE applications (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  
  -- Personal info
  first_name    TEXT NOT NULL,
  last_name     TEXT NOT NULL,
  email         TEXT NOT NULL,
  phone         TEXT,
  location      TEXT,
  city          TEXT,
  
  -- Academic info
  university    TEXT,
  degree        TEXT,
  major         TEXT,
  cgpa          TEXT,
  semester      TEXT,
  class_ranking TEXT,
  
  -- Application info
  field         TEXT,
  selected_tracks TEXT[],     -- Array of track names
  video_link    TEXT,
  
  -- Document URLs (Supabase Storage)
  resume_url    TEXT,
  transcript_url TEXT,
  photo_url     TEXT,
  
  -- Status
  status        TEXT DEFAULT 'pending'   -- pending | reviewed | accepted | rejected
);
```

### Supabase Storage Bucket

Bucket name: `interniq-docs`

File naming convention:
```
{uuid4()}_{original_filename}
```

Example:
```
3f2a7b1c-8d4e-4f9a-b2c1-123456789abc_john_doe_transcript.pdf
```

---

## 11. API Reference

### `POST /apply`

Accepts multipart/form-data.

**Form fields:**
| Field | Type | Required |
|---|---|---|
| first_name | string | Yes |
| last_name | string | Yes |
| email | string | Yes |
| phone | string | No |
| location | string | No |
| city | string | No |
| university | string | Yes |
| degree | string | Yes |
| major | string | Yes |
| cgpa | string | Yes |
| semester | string | Yes |
| class_ranking | string | No |
| field | string | Yes |
| selected_tracks | JSON array string | Yes (min 1) |
| video_link | string | No |
| resume | file (PDF) | Yes |
| transcript | file (PDF) | Yes |
| photo | file (JPG/PNG) | No |

**Response — Accepted:**
```json
{
  "status": "accepted",
  "message": "Your application has been submitted successfully. You will hear from us soon.",
  "application_id": "3f2a7b1c-8d4e-4f9a-b2c1-123456789abc"
}
```

**Response — Rejected:**
```json
{
  "status": "rejected",
  "failed_document": "transcript",
  "reason": "The uploaded document appears to be an essay, not an academic transcript. It does not contain course names, grades, or GPA information."
}
```

---

### `GET /applications`

Returns all applications ordered by most recent.

**Response:**
```json
[
  {
    "id": "...",
    "created_at": "2026-05-19T10:30:00Z",
    "first_name": "Muhammad",
    "last_name": "Ali",
    "email": "m.ali@example.com",
    "university": "NUST",
    "degree": "Bachelor's",
    "major": "Computer Science",
    "cgpa": "3.7",
    "selected_tracks": ["Frontend development", "AI"],
    "status": "pending"
  }
]
```

---

### `GET /applications/{id}`

Returns a single application by UUID including document URLs.

---

## 12. Form Fields Reference

The form mirrors the SPS SpinnLabs Internship 2026 page exactly. Key dropdowns:

**Location:** PK (Pakistan) — default

**Cities:** Grouped by province (Azad Kashmir, Balochistan, Gilgit-Baltistan, Islamabad, Khyber Pakhtunkhwa, Punjab, Sindh) — over 200 cities total

**Universities:** 150+ Pakistani universities listed, plus "Other" with a free-text field

**Degree:** Bachelor's / Master's / PhD

**Semester:** 1 through 8, plus "Recent Graduate"

**Class Ranking:** 1 through 10, plus "Others"

**Field:** Engineering / Business / Corporate

**Tracks — Projects:**
- IT Support & Helpdesk
- Business Management System (BMS)
- Security Management Automation Platform
- SPS Web Development

**Tracks — Competencies:**
- Endpoint Protection
- Helpdesk
- Frontend development
- Backend Development using NodeJS

**Tracks — Specializations:**
- Appian Developer
- IAM Developer
- Guardium Data Security
- Fundamentals (Fortinet)
- TrendAI Vision One Platform Foundation

**Micro-Internships:**
- Document Classifier
- Auto-Generate RFP Proposal Responses
- Leverage OpenClaw for Agentic Environments

---

## 13. Track Manager Mapping

For testing purposes, use Gmail addresses you control. In production, replace with real SPS staff emails.

```python
TRACK_MANAGERS = {
    "IT Support & Helpdesk":                        "manager1@gmail.com",
    "Business Management System (BMS)":             "manager2@gmail.com",
    "Security Management Automation Platform":      "manager3@gmail.com",
    "SPS Web Development":                          "manager4@gmail.com",
    "Endpoint Protection":                          "manager5@gmail.com",
    "Helpdesk":                                     "manager6@gmail.com",
    "Frontend development":                         "manager7@gmail.com",
    "Backend Development using NodeJS":             "manager8@gmail.com",
    "Appian Developer":                             "manager9@gmail.com",
    "IAM Developer":                                "manager10@gmail.com",
    "Guardium Data Security":                       "manager11@gmail.com",
    "TrendAI Vision One Platform Foundation":       "manager12@gmail.com",
    "Document Classifier":                          "manager13@gmail.com",
    "Auto-Generate RFP Proposal Responses":         "manager14@gmail.com",
}
```

---

## 14. Environment Variables

Create `backend/.env`:

```
# Supabase
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-role-key

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-api03-...

# Gmail SMTP
GMAIL_USER=youremail@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

**Never commit `.env` to Git.** Add it to `.gitignore`:
```
.env
__pycache__/
*.pyc
node_modules/
dist/
```

---

## 15. Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- A Supabase account (free tier works)
- A Gmail account with 2FA enabled + App Password generated
- An Anthropic API key

### Backend Setup

```bash
cd interniq/backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install fastapi uvicorn pdfplumber anthropic supabase python-dotenv python-multipart httpx
```

Copy `.env.example` to `.env` and fill in your keys.

In Supabase:
1. Create a new project
2. Run the SQL from Section 10 in the SQL editor to create the `applications` table
3. Create a storage bucket named `interniq-docs` (set to private)

```bash
uvicorn main:app --reload --port 8000
```

Backend is now live at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

### Frontend Setup

```bash
cd interniq/frontend
npm install
npm run dev
```

Frontend is now live at `http://localhost:5173`.

---

## 16. Security Considerations

| Risk | Mitigation |
|---|---|
| API keys exposed | All secrets in `.env`, never in source code |
| Unrestricted file uploads | Validate MIME type and file size before processing |
| PDF content injection | AI prompt uses clear delimiters around document text |
| CORS | FastAPI CORS middleware restricts to frontend origin only |
| Supabase key exposure | Use anon key on frontend (if needed); use service role key only on backend |
| Email spoofing | Gmail App Password is separate from account password; can be revoked anytime |
| Sensitive applicant data | Supabase RLS (Row Level Security) can be enabled to restrict table access |

---

## 17. Known Limitations & Future Improvements

### Current Limitations
- AI verification works best on text-based PDFs; scanned/image PDFs are flagged as unreadable
- Gmail SMTP has a sending limit (~500 emails/day for free accounts)
- No authentication on the admin endpoints (anyone can list all applications)
- No captcha implementation (the real SPS portal has one)
- Track manager emails are hardcoded in a config file rather than stored in the database

### Planned Improvements
- Add JWT authentication for the admin panel
- Implement Google reCAPTCHA v3 on the form
- Add support for OCR on scanned PDFs using Tesseract
- Replace Gmail SMTP with SendGrid or AWS SES for production scale
- Build a proper admin dashboard UI (React) with application review workflow
- Add Supabase Row Level Security policies
- Add webhook support so Supabase triggers events when a new row is inserted
- Implement status update emails (e.g. when reviewer changes status from "pending" to "accepted")

---

*InternIQ — Built with FastAPI · React · Claude AI · Supabase*
*Documentation version 1.0 — May 2026*
