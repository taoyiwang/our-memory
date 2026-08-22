"""事件详情与新增/删除路由。"""
import shutil
from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

import config
from models.event import create_event, delete_event, get_event
from models.photo import create_photo, list_photos
from models.timeline import get_timeline
from routes.guard import login_required
from services import image_service

bp = Blueprint("event", __name__)


@bp.route("/event/<int:event_id>")
@login_required
def detail(event_id):
    timeline = get_timeline()
    event = get_event(event_id)
    if event is None:
        abort(404)
    photos = list_photos(event_id)
    return render_template("event.html", timeline=timeline, event=event, photos=photos,
                           today=date.today().isoformat())


@bp.route("/event/new", methods=["POST"])
@login_required
def new():
    title = request.form.get("title", "").strip()
    event_date = request.form.get("event_date", "").strip()
    location = request.form.get("location", "").strip()
    content = request.form.get("content", "").strip()

    if not title:
        flash("标题不能为空", "error")
        return redirect(url_for("timeline.index"))
    if not event_date:
        flash("请选择日期", "error")
        return redirect(url_for("timeline.index"))

    timeline = get_timeline()
    event_id = create_event(timeline["id"], title, event_date, location, content)

    # 随新建事件一并上传照片
    files = request.files.getlist("photos")
    saved = 0
    for f in files:
        if not f or not f.filename:
            continue
        try:
            filename, thumbnail, original = image_service.save_upload(f, event_id)
            create_photo(event_id, filename, thumbnail, original)
            saved += 1
        except ValueError as e:
            flash(str(e), "error")
        except Exception:
            flash("照片处理失败", "error")
    if saved:
        flash(f"已上传 {saved} 张照片", "success")

    return redirect(url_for("event.detail", event_id=event_id))


@bp.route("/event/<int:event_id>/delete", methods=["POST"])
@login_required
def delete(event_id):
    event = get_event(event_id)
    if event is None:
        abort(404)
    # 删除照片文件目录
    shutil.rmtree(f"{config.PHOTO_DIR}/event_{event_id}", ignore_errors=True)
    delete_event(event_id)
    return redirect(url_for("timeline.index"))
