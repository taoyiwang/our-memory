"""认证守卫工具。"""
from functools import wraps

from flask import redirect, session, url_for


def login_required(view):
    """要求登录的视图装饰器。"""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("authed"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped
