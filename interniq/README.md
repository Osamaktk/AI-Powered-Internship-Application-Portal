# InternIQ

AI-Powered Internship Application Portal built with React + Tailwind + FastAPI.

## Features

- Multi-section SPS-style internship application form
- Upload support for resume + transcript PDF and optional profile photo
- AI-based document verification (Claude Sonnet 4)
- Auto-rejection response with rejection email when document type is incorrect
- Valid application persistence in Supabase table + file upload to Supabase Storage
- Track manager notifications via Gmail SMTP
- Admin APIs for listing and viewing applications

## Project Structure

```
interniq/
├── backend/
│   ├── main.py
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── config/
│   ├── templates/
│   ├── .env
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   └── data/
│   ├── index.html
│   ├── tailwind.config.js
│   └── vite.config.js
└── README.md
```

## Environment Variables

Create `backend/.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_STORAGE_BUCKET=interniq-docs
LOCAL_DEV_MODE=true
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=anthropic/claude-sonnet-4
GMAIL_USER=yourgmail@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
MANAGER_NOTIFICATION_OVERRIDE_EMAIL=your-test-email@example.com
```

## Supabase Schema

```sql
create table applications (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz default now(),
  first_name text,
  last_name text,
  email text,
  phone text,
  location text,
  city text,
  university text,
  degree text,
  major text,
  cgpa text,
  semester text,
  class_ranking text,
  field text,
  selected_tracks text[],
  resume_url text,
  transcript_url text,
  photo_url text,
  video_link text,
  status text default 'pending'
);
```

If `LOCAL_DEV_MODE=true`, files and records are saved locally (no Supabase bucket/table required).
If `LOCAL_DEV_MODE=false`, create a public storage bucket named `interniq-docs` (or set `SUPABASE_STORAGE_BUCKET`).

## Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install fastapi uvicorn pdfplumber supabase python-dotenv python-multipart

# Run backend
uvicorn main:app --reload --port 8000

# Frontend
cd ../frontend
npm install
npm run dev
```

## API Endpoints

- `POST /apply` - submit application
- `GET /applications` - list all applications (latest first)
- `GET /applications/{id}` - fetch one application by UUID
- `GET /health` - health check

## Notes

- Keep `.env` out of version control.
- If AI verification fails or returns invalid classification, the application is rejected and not saved.
- Email failures are wrapped in `try/except` so submission flow is not crashed by SMTP errors.
