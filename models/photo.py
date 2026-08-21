"""照片模型。"""
import os

from database import get_db, now


def create_photo(event_id: int, filename: str, thumbnail: str) -> int:
    """保存一条照片记录，返回 photo id。"""
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO photo (event_id, filename, thumbnail, created_at) VALUES (?, ?, ?, ?)",
            (event_id, filename, thumbnail, now()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_photo(photo_id: int):
    """按 id 获取照片记录。"""
    conn = get_db()
    try:
        return conn.execute("SELECT * FROM photo WHERE id = ?", (photo_id,)).fetchone()
    finally:
        conn.close()


def list_photos(event_id: int):
    """列出某事件全部照片。"""
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM photo WHERE event_id = ? ORDER BY id ASC", (event_id,)
        ).fetchall()
    finally:
        conn.close()


def delete_photo(photo_id: int) -> None:
    """删除照片记录（文件由调用方负责删除）。"""
    conn = get_db()
    try:
        conn.execute("DELETE FROM photo WHERE id = ?", (photo_id,))
        conn.commit()
    finally:
        conn.close()


def count_photos(event_id: int) -> int:
    """返回某事件的照片数量。"""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM photo WHERE event_id = ?", (event_id,)
        ).fetchone()
        return int(row["n"])
    finally:
        conn.close()
