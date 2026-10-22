import os
import sqlite3

DB_PATH = DB_PATH = os.environ.get("DB_PATH", "urls.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # access columns by name
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                original_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                clicks INTEGER DEFAULT 0
            )
            """
        )


def save_url(code, original_url):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO urls (code, original_url) VALUES (?, ?)",
            (code, original_url),
        )


def get_url(code):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM urls WHERE code = ?", (code,)
        ).fetchone()
    return row


def code_exists(code):
    return get_url(code) is not None


def increment_clicks(code):
    with get_connection() as conn:
        conn.execute(
            "UPDATE urls SET clicks = clicks + 1 WHERE code = ?", (code,)
        )


def get_stats(code):
    row = get_url(code)
    if row is None:
        return None
    return {
        "code": row["code"],
        "original_url": row["original_url"],
        "created_at": row["created_at"],
        "clicks": row["clicks"],
    }