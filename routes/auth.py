"""认证路由：登录 / 登出。"""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.timeline import get_timeline, verify_password

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("authed"):
        return redirect(url_for("timeline.index"))

    if request.method == "POST":
        password = request.form.get("password", "")
        if verify_password(password):
            session["authed"] = True
            return redirect(url_for("timeline.index"))
        flash("密码不对，再想想？", "error")

    timeline = get_timeline()
    return render_template("login.html", timeline=timeline)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
