# InternIQ

InternIQ is an AI-powered internship application portal built with FastAPI + React.

## What Changed (Round 2)

- Replaced Supabase persistence with local SQLite (`backend/database/interniq.db`)
- Added live pre-verification API: `POST /api/verify-document`
- Reworked document upload UX with AI checking states + rejection modal
- Enforced server-side re-verification in `/apply` before saving
- Added local file storage under `backend/uploads/`

## Storage

- SQLite DB file (auto-created): `backend/database/interniq.db`
- Uploaded files:
  - `backend/uploads/cv/`
  - `backend/uploads/transcripts/`
  - `backend/uploads/photos/`

## Environment Variables

Create `backend/.env`:

```env
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=anthropic/claude-sonnet-4
GMAIL_USER=yourgmail@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
MANAGER_NOTIFICATION_OVERRIDE_EMAIL=your-test-email@example.com
```

## Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd ../frontend
npm install
npm run dev
```

## API Endpoints

- `POST /api/verify-document` - pre-verify CV/transcript before submission
- `POST /apply` - final submission (re-verifies server-side, then saves)
- `GET /applications` - list applications
- `GET /applications/{id}` - get single application
- `GET /health` - health check
