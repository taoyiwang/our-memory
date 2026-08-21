"""时间轴空间模型（单空间模式）。"""
from database import get_db
from werkzeug.security import check_password_hash


def get_timeline():
    """返回默认时间轴，无则返回 None。"""
    conn = get_db()
    try:
        return conn.execute("SELECT * FROM timeline LIMIT 1").fetchone()
    finally:
        conn.close()


def verify_password(password: str) -> bool:
    """校验访问密码。"""
    timeline = get_timeline()
    if timeline is None or not timeline["password_hash"]:
        return False
    return check_password_hash(timeline["password_hash"], password)
