# SPS Internship Application Portal

AI-powered internship application portal for SPS - Software Productivity Strategists.

## Overview

This project provides an end-to-end internship intake workflow:

- Student submits profile, one internship program, and required documents.
- CV and transcript are AI-verified before final submission.
- Backend re-verifies documents server-side for security.
- Approved applications are saved in SQLite and files are stored locally.
- Notification email is sent to the selected program manager.
- Confirmation email is sent to the applicant.

## Key Features

- Single internship program selection (exactly one program per application).
- Real-time AI pre-verification endpoint for CV/transcript.
- Defensive server-side re-verification on `/apply`.
- Local SQLite database for easy inspection with DB Browser for SQLite.
- Local file storage for CV, transcript, and photo uploads.
- Professional HTML email notifications with CV attachment support.

## Tech Stack

- Frontend: React + Vite + Tailwind CSS
- Backend: FastAPI (Python)
- AI verification: OpenRouter (Claude model by default)
- Email: Gmail SMTP (`smtplib`)
- Database: SQLite (`sqlite3`)

## Repository Structure

```text
interniq/
  backend/
    main.py
    config/
    database/
      db.py
      sps_applications.db         # auto-created (default)
    routes/
    services/
    uploads/
      cv/
      transcripts/
      photos/
  frontend/
    src/
```

## Environment Variables

Create `backend/.env`:

```env
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=anthropic/claude-sonnet-4
GMAIL_USER=yourgmail@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
MANAGER_NOTIFICATION_OVERRIDE_EMAIL=your-test-email@example.com
PORTAL_URL=http://localhost:5173
```

Optional frontend env (`frontend/.env`):

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Local Setup

### Backend (Windows PowerShell)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173` and backend on `http://localhost:8000`.

## API Endpoints

- `POST /api/verify-document` - pre-verifies uploaded CV/transcript
- `POST /apply` - final submission (re-verifies, saves, sends emails)
- `GET /applications` - list all applications
- `GET /applications/{id}` - get one application by ID
- `GET /health` - service health check

## Data Storage

- SQLite database (default): `backend/database/sps_applications.db`
- File uploads:
  - `backend/uploads/cv/`
  - `backend/uploads/transcripts/`
  - `backend/uploads/photos/`

Notes:
- Filenames are stored with UUID prefixes to avoid collisions.
- Document file paths and AI verdict metadata are stored in the database.

## Program Routing Logic

- Applicant must select exactly one internship program.
- Backend validates that exactly one program was provided.
- Notification email is routed to the manager mapped for that specific program.
- `MANAGER_NOTIFICATION_OVERRIDE_EMAIL` can be used during testing to force all manager emails to one inbox.

## Troubleshooting

- No emails received:
  - Verify `GMAIL_USER` and app password are correct.
  - Check spam/promotions tabs.
  - Confirm backend was restarted after `.env` updates.
- Transcript rejected:
  - Ensure PDF text is extractable or filename clearly indicates transcript.
- 400 error on submit:
  - Confirm exactly one internship program is selected.
  - Confirm both CV and transcript are AI-verified before applying.
