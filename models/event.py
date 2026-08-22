"""时间节点（事件）模型。"""
from database import get_db, now
from datetime import date


def event_stats(timeline_id: int):
    """统计：事件总数，以及从最早事件到今天的累计天数。

    返回 (count, days)。无事件时 count=0、days=0。
    """
    conn = get_db()
    try:
        row = conn.execute(
            """
            SELECT COUNT(*) AS cnt, MIN(e.event_date) AS earliest
            FROM event e
            WHERE e.timeline_id = ?
            """,
            (timeline_id,),
        ).fetchone()
        if not row or not row["cnt"]:
            return 0, 0
        try:
            earliest = date.fromisoformat(row["earliest"][:10])
            days = (date.today() - earliest).days + 1  # 含当天
        except ValueError:
            return row["cnt"], 0
        return row["cnt"], max(days, 1)
    finally:
        conn.close()


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
    """按日期倒序列出全部事件，附带照片统计与前 3 张封面图 id。"""
    conn = get_db()
    try:
        rows = conn.execute(
            """
            SELECT e.*,
                   (SELECT COUNT(*) FROM photo p WHERE p.event_id = e.id)  AS photo_count
            FROM event e
            WHERE e.timeline_id = ?
            ORDER BY e.event_date DESC, e.id DESC
            """,
            (timeline_id,),
        ).fetchall()

        event_ids = [row["id"] for row in rows]
        if event_ids:
            placeholders = ",".join("?" * len(event_ids))
            photo_rows = conn.execute(
                f"""
                SELECT event_id, id FROM photo
                WHERE event_id IN ({placeholders})
                ORDER BY event_id, id
                """,
                event_ids,
            ).fetchall()
            photos_by_event = {}
            for pr in photo_rows:
                eid = pr["event_id"]
                if eid not in photos_by_event:
                    photos_by_event[eid] = []
                if len(photos_by_event[eid]) < 3:
                    photos_by_event[eid].append(pr["id"])
        else:
            photos_by_event = {}

        result = []
        for row in rows:
            d = dict(row)
            d["cover_photos"] = photos_by_event.get(row["id"], [])
            result.append(d)

        return result
    finally:
        conn.close()


def update_event(event_id: int, title: str, event_date: str, location: str, content: str) -> None:
    """更新事件信息。"""
    conn = get_db()
    try:
        conn.execute(
            "UPDATE event SET title = ?, event_date = ?, location = ?, content = ? WHERE id = ?",
            (title, event_date, location, content, event_id)
        )
        conn.commit()
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
