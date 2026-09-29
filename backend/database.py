from pathlib import Path
import sqlite3
from datetime import datetime, timezone
import uuid


# =========================================================
# PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

DB_PATH = DATA_DIR / "smartguard.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    """
    Create and return a SQLite database connection.
    """

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DB_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def initialize_database():
    """
    Create the reports table if it does not already exist.
    """

    connection = get_connection()

    try:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (

                id TEXT PRIMARY KEY,

                created_at TEXT NOT NULL,

                email_text TEXT NOT NULL,

                prediction TEXT NOT NULL,

                risk_score INTEGER NOT NULL,

                risk_level TEXT NOT NULL,

                status TEXT NOT NULL DEFAULT 'PENDING'

            )
            """
        )

        connection.commit()

    finally:

        connection.close()


# =========================================================
# CREATE REPORT
# =========================================================

def create_report(
    email_text,
    prediction,
    risk_score,
    risk_level
):
    """
    Store a reported email in the database.
    """

    report_id = str(
        uuid.uuid4()
    )

    created_at = datetime.now(
        timezone.utc
    ).isoformat()

    connection = get_connection()

    try:

        connection.execute(
            """
            INSERT INTO reports (
                id,
                created_at,
                email_text,
                prediction,
                risk_score,
                risk_level,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report_id,
                created_at,
                email_text,
                prediction,
                int(risk_score),
                risk_level,
                "PENDING"
            )
        )

        connection.commit()

        return {
            "id": report_id,
            "created_at": created_at,
            "status": "PENDING"
        }

    finally:

        connection.close()


# =========================================================
# GET ALL REPORTS
# =========================================================

def get_reports():
    """
    Return all reports without exposing
    the full email text in the list.
    """

    connection = get_connection()

    try:

        rows = connection.execute(
            """
            SELECT
                id,
                created_at,
                prediction,
                risk_score,
                risk_level,
                status
            FROM reports
            ORDER BY created_at DESC
            """
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# =========================================================
# GET ONE REPORT
# =========================================================

def get_report(report_id):
    """
    Return one report including the full email content.
    """

    connection = get_connection()

    try:

        row = connection.execute(
            """
            SELECT
                id,
                created_at,
                email_text,
                prediction,
                risk_score,
                risk_level,
                status
            FROM reports
            WHERE id = ?
            """,
            (report_id,)
        ).fetchone()

        if row is None:
            return None

        return dict(row)

    finally:

        connection.close()