"""基础 Web 安全工具：CSRF 防护与会话令牌。"""
import secrets
from hmac import compare_digest

from flask import abort, request, session

CSRF_SESSION_KEY = "_csrf_token"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


def ensure_csrf_token() -> str:
    """为当前 session 创建并返回 CSRF token。"""
    token = session.get(CSRF_SESSION_KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        session[CSRF_SESSION_KEY] = token
    return token


def validate_csrf() -> None:
    """校验所有非安全 HTTP 方法携带的 CSRF token。"""
    if request.method in SAFE_METHODS:
        return

    expected = session.get(CSRF_SESSION_KEY)
    supplied = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
    if not expected or not supplied or not compare_digest(expected, supplied):
        abort(400, description="CSRF token 无效或缺失")
