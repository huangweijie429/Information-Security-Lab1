"""SQLite storage. Every query is parameterized (SQLi prevention demo)."""
import os
import sqlite3
from contextlib import contextmanager

from .security import hash_password

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS posts (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT NOT NULL,
    title  TEXT NOT NULL,
    body   TEXT NOT NULL
);
"""


def db_path() -> str:
    return os.getenv("DB_PATH", "app.db")


@contextmanager
def connect():
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db(seed: bool = True) -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
        if not seed:
            return
        cur = conn.execute("SELECT 1 FROM users WHERE username = ?", ("admin",))
        if cur.fetchone() is None:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                ("admin", hash_password(os.getenv("ADMIN_PASSWORD", "Admin123!"))),
            )
        cur = conn.execute("SELECT 1 FROM posts LIMIT 1")
        if cur.fetchone() is None:
            rows = [
                ("admin", "Welcome", "First post of the demo API."),
                ("alice", "Notes", "Hello <b>world</b>"),
                ("bob", "Shopping", "Milk, eggs, bread"),
            ]
            conn.executemany(
                "INSERT INTO posts (author, title, body) VALUES (?, ?, ?)", rows
            )
        conn.commit()
