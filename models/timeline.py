"""时间轴空间模型（单空间模式）。"""
import os
from database import get_db


def get_timeline():
    """返回默认时间轴，无则返回 None。"""
    conn = get_db()
    try:
        return conn.execute("SELECT * FROM timeline LIMIT 1").fetchone()
    finally:
        conn.close()


def verify_password(password: str) -> bool:
    """校验访问密码，直接从环境变量读取。"""
    return password == os.environ.get("TIMELINE_PASSWORD", "123456")
