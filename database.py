"""SQLite 数据库连接与建表。"""
import sqlite3
from datetime import datetime, timezone

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS timeline (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    password_hash TEXT    NOT NULL,
    cover_image   TEXT,
    created_at    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS event (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timeline_id INTEGER NOT NULL REFERENCES timeline(id),
    title       TEXT    NOT NULL,
    event_date  TEXT    NOT NULL,
    location    TEXT    DEFAULT '',
    content     TEXT    DEFAULT '',
    created_at  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS photo (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id   INTEGER NOT NULL REFERENCES event(id),
    filename   TEXT    NOT NULL,
    thumbnail  TEXT    NOT NULL,
    original   TEXT    DEFAULT '',
    created_at TEXT    NOT NULL
);
"""


def get_db():
    """获取数据库连接（每请求一个）。"""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """初始化数据库表结构。"""
    conn = get_db()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def now() -> str:
    """当前 UTC ISO 时间字符串。"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def seed_default_timeline():
    """确保存在一个默认时间轴（单空间模式）。"""
    conn = get_db()
    try:
        row = conn.execute("SELECT id FROM timeline LIMIT 1").fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO timeline (name, password_hash, cover_image, created_at) VALUES (?, ?, ?, ?)",
                ("我们的故事", "", None, now()),
            )
            conn.commit()
    finally:
        conn.close()
