"""我们的故事 —— 私人共享回忆时间轴。

启动：
    python app.py            # 开发模式
    gunicorn -w 2 -b 127.0.0.1:8000 app:app   # 生产模式
"""
import os
from datetime import timedelta

from flask import Flask, redirect, render_template, request, url_for

import config
import database
from security import ensure_csrf_token, validate_csrf


def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=config.SECRET_KEY,
        MAX_CONTENT_LENGTH=config.MAX_UPLOAD_SIZE * config.MAX_UPLOAD_COUNT,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=config.COOKIE_SECURE,
        PERMANENT_SESSION_LIFETIME=timedelta(days=config.SESSION_DAYS),
    )

    @app.before_request
    def protect_state_changing_requests():
        validate_csrf()

    @app.context_processor
    def inject_security_context():
        return {"csrf_token": ensure_csrf_token()}

    # 初始化数据库
    database.init_db()
    database.seed_default_timeline()

    # 注册蓝图
    from routes import auth, event, photo, timeline
    app.register_blueprint(auth.bp)
    app.register_blueprint(timeline.bp)
    app.register_blueprint(event.bp)
    app.register_blueprint(photo.bp)

    @app.route("/")
    def index():
        return redirect(url_for("timeline.index"))

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(413)
    def too_large(e):
        return render_template("error.html", code=413, message="文件过大，单张不能超过 15MB"), 413

    @app.template_filter("date_cn")
    def date_cn(value):
        """格式化日期为「2026年8月24日」（跨平台，不依赖 %-m）。"""
        try:
            from datetime import datetime
            dt = datetime.strptime(str(value)[:10], "%Y-%m-%d")
            return f"{dt.year}年{dt.month}月{dt.day}日"
        except Exception:
            return value

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
