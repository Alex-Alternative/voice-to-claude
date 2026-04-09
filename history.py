"""
Transcript history for Koda.
Stores transcriptions in a local SQLite database.
"""

import os
import sqlite3
from datetime import datetime

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "koda_history.db")


def _get_conn():
    """Get a database connection."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create the transcriptions table if it doesn't exist."""
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transcriptions (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            text TEXT,
            mode TEXT,
            duration_seconds REAL
        )
    """)
    conn.commit()
    conn.close()


def save_transcription(text, mode="dictation", duration=0.0):
    """Save a transcription to the database."""
    conn = _get_conn()
    conn.execute(
        "INSERT INTO transcriptions (timestamp, text, mode, duration_seconds) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), text, mode, duration),
    )
    conn.commit()
    conn.close()


def search_history(query, limit=50):
    """Search transcriptions by text content."""
    conn = _get_conn()
    cursor = conn.execute(
        "SELECT id, timestamp, text, mode, duration_seconds FROM transcriptions "
        "WHERE text LIKE ? ORDER BY id DESC LIMIT ?",
        (f"%{query}%", limit),
    )
    results = cursor.fetchall()
    conn.close()
    return results


def get_recent(limit=20):
    """Get the most recent transcriptions."""
    conn = _get_conn()
    cursor = conn.execute(
        "SELECT id, timestamp, text, mode, duration_seconds FROM transcriptions "
        "ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    results = cursor.fetchall()
    conn.close()
    return results


def export_history(filepath):
    """Export all transcriptions to a text file."""
    conn = _get_conn()
    cursor = conn.execute(
        "SELECT timestamp, text, mode, duration_seconds FROM transcriptions ORDER BY id ASC"
    )
    with open(filepath, "w", encoding="utf-8") as f:
        for row in cursor:
            timestamp, text, mode, duration = row
            f.write(f"[{timestamp}] ({mode}, {duration:.1f}s) {text}\n")
    conn.close()
