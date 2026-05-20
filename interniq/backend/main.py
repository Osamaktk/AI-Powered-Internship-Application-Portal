import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from routes import admin, apply

load_dotenv()


app = FastAPI(
    title="InternIQ API",
    description="AI-powered internship application backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(apply.router)
app.include_router(admin.router)

if os.getenv("LOCAL_DEV_MODE", "").strip().lower() in {"1", "true", "yes", "on"}:
    uploads_dir = Path(__file__).resolve().parent / "local_storage" / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/local-files", StaticFiles(directory=str(uploads_dir)), name="local-files")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
