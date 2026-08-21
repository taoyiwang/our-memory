"""时间节点（事件）模型。"""
from database import get_db, now


def create_event(timeline_id: int, title: str, event_date: str,
                 location: str = "", content: str = "") -> int:
    """创建时间节点，返回新事件 id。"""
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO event (timeline_id, title, event_date, location, content, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (timeline_id, title, event_date, location, content, now()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_event(event_id: int):
    """按 id 获取事件。"""
    conn = get_db()
    try:
        return conn.execute("SELECT * FROM event WHERE id = ?", (event_id,)).fetchone()
    finally:
        conn.close()


def list_events(timeline_id: int):
    """按日期倒序列出全部事件，附带照片统计与封面。"""
    conn = get_db()
    try:
        rows = conn.execute(
            """
            SELECT e.*,
                   (SELECT COUNT(*) FROM photo p WHERE p.event_id = e.id)  AS photo_count,
                   (SELECT p.id FROM photo p
                     WHERE p.event_id = e.id ORDER BY p.id LIMIT 1)        AS cover_photo
            FROM event e
            WHERE e.timeline_id = ?
            ORDER BY e.event_date DESC, e.id DESC
            """,
            (timeline_id,),
        ).fetchall()
        return rows
    finally:
        conn.close()


def delete_event(event_id: int) -> None:
    """删除事件（照片由调用方负责删除文件）。"""
    conn = get_db()
    try:
        conn.execute("DELETE FROM photo WHERE event_id = ?", (event_id,))
        conn.execute("DELETE FROM event WHERE id = ?", (event_id,))
        conn.commit()
    finally:
        conn.close()
