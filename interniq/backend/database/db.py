"""
Database module for SPS - Software Productivity Strategists.
Uses Python's built-in sqlite3.
The .db file is created automatically on first run.
All tables are created with IF NOT EXISTS so restarts are safe.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from uuid import uuid4

_DATABASE_DIR = os.path.dirname(__file__)
_PREFERRED_DB_PATH = os.path.join(_DATABASE_DIR, "sps_applications.db")
_EXISTING_DB_FILES = sorted(
    file_name
    for file_name in os.listdir(_DATABASE_DIR)
    if file_name.lower().endswith(".db")
)
DB_PATH = (
    _PREFERRED_DB_PATH
    if os.path.exists(_PREFERRED_DB_PATH) or not _EXISTING_DB_FILES
    else os.path.join(_DATABASE_DIR, _EXISTING_DB_FILES[0])
)


@contextmanager
def get_connection():
    """
    Yield a sqlite3 connection with row_factory = sqlite3.Row
    so rows can be accessed like dictionaries.
    Always commit on success, rollback on exception, close on exit.
    """
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db():
    """
    Called once on application startup (in main.py lifespan).
    Creates all tables if they do not exist.
    """
    backend_root = os.path.dirname(os.path.dirname(__file__))
    os.makedirs(os.path.join(backend_root, "uploads", "cv"), exist_ok=True)
    os.makedirs(os.path.join(backend_root, "uploads", "transcripts"), exist_ok=True)
    os.makedirs(os.path.join(backend_root, "uploads", "photos"), exist_ok=True)

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id                  TEXT PRIMARY KEY,
                submitted_at        TEXT NOT NULL,
                status              TEXT NOT NULL DEFAULT 'Pending',

                first_name          TEXT NOT NULL,
                last_name           TEXT NOT NULL,
                email               TEXT NOT NULL,
                phone               TEXT,
                location            TEXT,
                city                TEXT,

                university          TEXT,
                degree              TEXT,
                major               TEXT,
                cgpa                TEXT,
                current_semester    TEXT,
                class_ranking       TEXT,

                field               TEXT,
                selected_tracks     TEXT,

                cv_filename         TEXT,
                cv_filepath         TEXT,
                transcript_filename TEXT,
                transcript_filepath TEXT,
                photo_filename      TEXT,
                photo_filepath      TEXT,

                cv_ai_verdict       TEXT,
                cv_ai_confidence    TEXT,
                cv_ai_reason        TEXT,
                transcript_ai_verdict     TEXT,
                transcript_ai_confidence  TEXT,
                transcript_ai_reason      TEXT,

                video_link          TEXT,
                internship_year     TEXT
            );
            """
        )


def insert_application(data: dict) -> str:
    """
    Insert a new application row.
    data keys match the column names in the applications table.
    Returns the new row's id (TEXT uuid).
    """
    application_id = str(data.get("id") or uuid4())
    row = dict(data)
    row["id"] = application_id

    columns = [
        "id",
        "submitted_at",
        "status",
        "first_name",
        "last_name",
        "email",
        "phone",
        "location",
        "city",
        "university",
        "degree",
        "major",
        "cgpa",
        "current_semester",
        "class_ranking",
        "field",
        "selected_tracks",
        "cv_filename",
        "cv_filepath",
        "transcript_filename",
        "transcript_filepath",
        "photo_filename",
        "photo_filepath",
        "cv_ai_verdict",
        "cv_ai_confidence",
        "cv_ai_reason",
        "transcript_ai_verdict",
        "transcript_ai_confidence",
        "transcript_ai_reason",
        "video_link",
        "internship_year",
    ]
    values = [row.get(column) for column in columns]
    placeholders = ",".join("?" for _ in columns)

    with get_connection() as connection:
        connection.execute(
            f"INSERT INTO applications ({','.join(columns)}) VALUES ({placeholders})",
            values,
        )

    return application_id


def get_all_applications() -> list[dict]:
    """
    Return all rows from applications ordered by submitted_at DESC.
    Each row as a plain dict.
    """
    with get_connection() as connection:
        cursor = connection.execute(
            "SELECT * FROM applications ORDER BY submitted_at DESC"
        )
        rows = cursor.fetchall()
    return [dict(row) for row in rows]


def get_application_by_id(application_id: str) -> dict | None:
    """Return a single application row as a dict, or None if not found."""
    with get_connection() as connection:
        cursor = connection.execute(
            "SELECT * FROM applications WHERE id = ? LIMIT 1",
            (application_id,),
        )
        row = cursor.fetchone()
    return dict(row) if row else None


def update_application_status(application_id: str, status: str) -> None:
    """Update the status column of a single application row."""
    with get_connection() as connection:
        connection.execute(
            "UPDATE applications SET status = ? WHERE id = ?",
            (status, application_id),
        )
