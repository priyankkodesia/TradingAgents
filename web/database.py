"""SQLite persistence layer for the HillTrade web UI."""

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import bcrypt

DB_PATH = Path.home() / ".tradingagents" / "web.db"

_SEED_USERS = [
    ("Priyank", "HillTrade@2026"),
    ("Amit",    "HillTrade@2026"),
    ("Arsh",    "HillTrade@2026"),
    ("Vaibhav", "HillTrade@2026"),
]


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            created_at    TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS analyses (
            id             TEXT PRIMARY KEY,
            user_id        INTEGER NOT NULL,
            username       TEXT NOT NULL,
            ticker         TEXT NOT NULL,
            analysis_date  TEXT NOT NULL,
            settings       TEXT NOT NULL,
            status         TEXT NOT NULL DEFAULT 'pending',
            final_decision TEXT,
            rating         TEXT,
            error          TEXT,
            created_at     TEXT DEFAULT (datetime('now')),
            completed_at   TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS analysis_events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id TEXT NOT NULL,
            event_type  TEXT NOT NULL,
            data        TEXT NOT NULL,
            created_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (analysis_id) REFERENCES analyses(id)
        );

        CREATE TABLE IF NOT EXISTS news_analyses (
            id           TEXT PRIMARY KEY,
            user_id      INTEGER NOT NULL,
            username     TEXT NOT NULL,
            news_text    TEXT NOT NULL,
            status       TEXT NOT NULL DEFAULT 'pending',
            result_json  TEXT,
            error        TEXT,
            created_at   TEXT DEFAULT (datetime('now')),
            completed_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS news_events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id TEXT NOT NULL,
            event_type  TEXT NOT NULL,
            data        TEXT NOT NULL,
            created_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (analysis_id) REFERENCES news_analyses(id)
        );
    """)
    for username, password in _SEED_USERS:
        exists = conn.execute(
            "SELECT id FROM users WHERE username = ? COLLATE NOCASE", (username,)
        ).fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hash_password(password)),
            )
    conn.commit()
    conn.close()


@contextmanager
def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ── Users ────────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def get_user(username: str) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? COLLATE NOCASE", (username,)
        ).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def update_password(user_id: int, new_password: str) -> None:
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (hash_password(new_password), user_id),
        )


# ── Analyses ─────────────────────────────────────────────────────────────────

def new_analysis_id() -> str:
    return str(uuid.uuid4())


def create_analysis(
    analysis_id: str,
    user_id: int,
    username: str,
    ticker: str,
    analysis_date: str,
    settings: dict,
) -> None:
    with get_db() as conn:
        conn.execute(
            """INSERT INTO analyses
               (id, user_id, username, ticker, analysis_date, settings, status)
               VALUES (?, ?, ?, ?, ?, ?, 'pending')""",
            (analysis_id, user_id, username, ticker, analysis_date, json.dumps(settings)),
        )


def update_analysis_status(
    analysis_id: str,
    status: str,
    *,
    final_decision: str | None = None,
    rating: str | None = None,
    error: str | None = None,
) -> None:
    completed_at = (
        datetime.utcnow().isoformat() if status in ("completed", "failed") else None
    )
    with get_db() as conn:
        conn.execute(
            """UPDATE analyses
               SET status=?, final_decision=?, rating=?, error=?, completed_at=?
               WHERE id=?""",
            (status, final_decision, rating, error, completed_at, analysis_id),
        )


def get_analysis(analysis_id: str) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM analyses WHERE id=?", (analysis_id,)
        ).fetchone()
        if row:
            d = dict(row)
            d["settings"] = json.loads(d["settings"])
            return d
        return None


def get_all_analyses(limit: int = 200) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM analyses ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


# ── Events ────────────────────────────────────────────────────────────────────

def add_event(analysis_id: str, event_type: str, data: dict) -> None:
    with get_db() as conn:
        conn.execute(
            "INSERT INTO analysis_events (analysis_id, event_type, data) VALUES (?, ?, ?)",
            (analysis_id, event_type, json.dumps(data)),
        )


def get_events(analysis_id: str, since_id: int = 0) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM analysis_events
               WHERE analysis_id=? AND id>? ORDER BY id""",
            (analysis_id, since_id),
        ).fetchall()
        return [dict(r) for r in rows]


# ── News Analyses ─────────────────────────────────────────────────────────────

def create_news_analysis(analysis_id: str, user_id: int, username: str, news_text: str) -> None:
    with get_db() as conn:
        conn.execute(
            """INSERT INTO news_analyses (id, user_id, username, news_text, status)
               VALUES (?, ?, ?, ?, 'pending')""",
            (analysis_id, user_id, username, news_text),
        )


def update_news_analysis_status(
    analysis_id: str,
    status: str,
    *,
    result: dict | None = None,
    error: str | None = None,
) -> None:
    completed_at = (
        datetime.utcnow().isoformat() if status in ("completed", "failed") else None
    )
    with get_db() as conn:
        conn.execute(
            """UPDATE news_analyses
               SET status=?, result_json=?, error=?, completed_at=?
               WHERE id=?""",
            (status, json.dumps(result) if result else None, error, completed_at, analysis_id),
        )


def get_news_analysis(analysis_id: str) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM news_analyses WHERE id=?", (analysis_id,)
        ).fetchone()
        if row:
            d = dict(row)
            if d["result_json"]:
                d["result"] = json.loads(d["result_json"])
            else:
                d["result"] = None
            return d
        return None


def get_all_news_analyses(limit: int = 100) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM news_analyses ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def add_news_event(analysis_id: str, event_type: str, data: dict) -> None:
    with get_db() as conn:
        conn.execute(
            "INSERT INTO news_events (analysis_id, event_type, data) VALUES (?, ?, ?)",
            (analysis_id, event_type, json.dumps(data)),
        )


def get_news_events(analysis_id: str, since_id: int = 0) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM news_events
               WHERE analysis_id=? AND id>? ORDER BY id""",
            (analysis_id, since_id),
        ).fetchall()
        return [dict(r) for r in rows]
