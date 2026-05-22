# AI-Powered Internship Application Portal

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?logo=react&logoColor=20232A)
![Vite](https://img.shields.io/badge/Vite-Build_Tool-646CFF?logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-UI-06B6D4?logo=tailwindcss&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)

## Hero Description

This project is a full-stack internship application portal built for **SPS - Software Productivity Strategists**. It helps students submit applications through a structured form while automatically validating CV and transcript uploads using AI before final submission. It is designed for internship teams that want a cleaner intake process, faster screening, and department-specific notification workflows.

## Features

- 🧾 **Multi-section application form** with personal, academic, and internship details
- 🤖 **AI document verification** for CV and transcript using OpenRouter (Claude model)
- ⚡ **Real-time pre-verification API** (`/api/verify-document`) before final submission
- 🔒 **Server-side re-verification** on `/apply` (frontend validation is never trusted alone)
- 📌 **Single internship program selection** (exactly 1 program per application)
- 📨 **Professional HTML emails**:
  - confirmation email to applicant
  - manager notification email with CV attachment
  - rejection email with reason/evidence
- 🗂️ **SQLite persistence** for easy local inspection in DB Browser for SQLite
- 📁 **Local file storage** for CV, transcript, and photo uploads
- 🧭 **Admin endpoints** to list applications and fetch by ID

## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React 18, Vite 5, Tailwind CSS 3 |
| Backend | FastAPI, Uvicorn |
| AI Verification | OpenRouter Chat Completions API (`anthropic/claude-sonnet-4`) |
| Data Storage | SQLite (`sqlite3`) |
| File Handling | Local filesystem uploads + `pdfplumber` text extraction |
| Email | Python `smtplib`, `email.mime` (Gmail SMTP + App Password) |
| Config | `python-dotenv` |
| Validation / Parsing | `python-multipart`, `email-validator` |

## Project Structure

```text
interniq/
├── backend/
│   ├── main.py                         # FastAPI entrypoint, lifespan init, CORS, router mounting
│   ├── requirements.txt                # Python dependencies
│   ├── config/
│   │   └── track_managers.py           # Internship program -> manager email map
│   ├── database/
│   │   ├── db.py                       # SQLite init + CRUD helpers
│   │   └── sps_applications.db         # Auto-created default SQLite DB
│   ├── routes/
│   │   ├── apply.py                    # POST /apply (validation, AI checks, save, email)
│   │   ├── verify.py                   # POST /api/verify-document (live pre-verification)
│   │   └── admin.py                    # GET /applications, GET /applications/{id}
│   ├── services/
│   │   ├── ai_verifier.py              # OpenRouter verification logic + heuristics
│   │   ├── pdf_extractor.py            # PDF text extraction with pdfplumber
│   │   └── email_service.py            # HTML email templates + SMTP sender
│   ├── templates/                      # Legacy HTML templates (reference)
│   └── uploads/                        # Auto-created storage folders
│       ├── cv/
│       ├── transcripts/
│       └── photos/
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── App.jsx
│       ├── api/client.js
│       ├── hooks/useFormSubmit.js
│       ├── data/formOptions.js
│       └── components/
│           ├── PersonalInfoSection.jsx
│           ├── TrackSelectionSection.jsx
│           ├── DocumentUploadSection.jsx
│           ├── VerificationModal.jsx
│           ├── SubmitSection.jsx
│           └── SpsProgramInfoSection.jsx
└── README.md                            # App-level README inside interniq/
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm
- OpenRouter API key
- Gmail account with App Password enabled (for SMTP)

### 1. Clone Repository

```bash
git clone https://github.com/Osamaktk/AI-Powered-Internship-Application-Portal.git
cd AI-Powered-Internship-Application-Portal
```

### 2. Backend Setup

```bash
cd interniq/backend
python -m venv venv
```

Activate environment:

- Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

- macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `backend/.env`:

```env
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=anthropic/claude-sonnet-4
OPENROUTER_HTTP_REFERER=http://localhost:5173
OPENROUTER_APP_NAME=SPS Internship Portal

GMAIL_USER=yourgmail@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

# Optional test override: route all manager notifications to one inbox
MANAGER_NOTIFICATION_OVERRIDE_EMAIL=your-test-email@example.com

# Link used in rejection email button
PORTAL_URL=http://localhost:5173
```

Run backend:

```bash
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup

In a new terminal:

```bash
cd interniq/frontend
npm install
npm run dev
```

Optional `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 4. Open App

- Frontend: `http://localhost:5173`
- Backend docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## Usage

1. Open the portal and review the SPS internship overview section.
2. Fill Section 1 (personal and academic details).
3. In Section 2, select **one** internship program.
4. Upload CV and transcript in Section 3; each file is AI-verified in real time.
5. Click `APPLY` only after both required documents are verified.
6. Backend re-verifies documents, stores records/files locally, and sends notification emails.
7. Use admin endpoints to inspect submitted applications:
   - `GET /applications`
   - `GET /applications/{application_id}`

## Screenshots / Demo

Add screenshots or demo GIFs in your repository, for example:

```text
docs/images/home.png
docs/images/verification-modal.png
docs/images/success-state.png
docs/images/admin-response.png
```

Then reference them in this section:

```md
![Home Screen](docs/images/home.png)
![Verification Modal](docs/images/verification-modal.png)
```

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

Please keep PRs focused, add clear commit messages, and include testing notes.

## License

This project is licensed under the **MIT License**.  
See [LICENSE](./LICENSE) for details.

## Author

Built by **Osamaktk**  
GitHub: [https://github.com/Osamaktk](https://github.com/Osamaktk)

