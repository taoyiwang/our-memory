"""照片上传 / 访问 / 删除 / 下载路由。"""
import os

from flask import Blueprint, abort, flash, redirect, request, send_file, url_for

import config
from models.event import get_event
from models.photo import create_photo, delete_photo, get_photo
from routes.guard import login_required
from services import image_service

bp = Blueprint("photo", __name__)

# 照片文件内容不可变（文件名是 uuid），可安全长缓存
CACHE_MAX_AGE = 60 * 60 * 24 * 365  # 1 年


@bp.route("/photo/<int:photo_id>")
@login_required
def serve(photo_id):
    """受保护的图片访问，不直接暴露文件系统。"""
    photo = get_photo(photo_id)
    if photo is None:
        abort(404)
    path = os.path.join(config.PHOTO_DIR, f"event_{photo['event_id']}", photo["filename"])
    if not os.path.isfile(path):
        abort(404)
    return send_file(path, mimetype="image/webp",
                     max_age=CACHE_MAX_AGE,
                     conditional=True)


@bp.route("/photo/<int:photo_id>/thumb")
@login_required
def serve_thumb(photo_id):
    """缩略图访问。"""
    photo = get_photo(photo_id)
    if photo is None:
        abort(404)
    path = os.path.join(config.PHOTO_DIR, f"event_{photo['event_id']}", photo["thumbnail"])
    if not os.path.isfile(path):
        path = os.path.join(config.PHOTO_DIR, f"event_{photo['event_id']}", photo["filename"])
    return send_file(path, mimetype="image/webp",
                     max_age=CACHE_MAX_AGE,
                     conditional=True)


@bp.route("/photo/<int:photo_id>/download")
@login_required
def download(photo_id):
    """下载原始文件（保留原始格式）。"""
    photo = get_photo(photo_id)
    if photo is None:
        abort(404)
    event_dir = os.path.join(config.PHOTO_DIR, f"event_{photo['event_id']}")
    orig_name = photo["original"] or photo["filename"]
    path = os.path.join(event_dir, orig_name)
    if not os.path.isfile(path):
        abort(404)
    ext = os.path.splitext(orig_name)[1].lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
                ".webp": "image/webp", ".gif": "image/gif", ".bmp": "image/bmp"}
    return send_file(path, mimetype=mime_map.get(ext, "image/jpeg"),
                     as_attachment=True, download_name=orig_name)


@bp.route("/event/<int:event_id>/upload", methods=["POST"])
@login_required
def upload(event_id):
    event = get_event(event_id)
    if event is None:
        abort(404)

    files = request.files.getlist("photos")
    if not files:
        flash("没有选择照片", "error")
        return redirect(url_for("event.detail", event_id=event_id))

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

    flash(f"已上传 {saved} 张照片", "success" if saved else "error")
    return redirect(url_for("event.detail", event_id=event_id))


@bp.route("/photo/<int:photo_id>/delete", methods=["POST"])
@login_required
def delete(photo_id):
    photo = get_photo(photo_id)
    if photo is None:
        abort(404)

    event_id = photo["event_id"]
    # 删除文件
    event_dir = os.path.join(config.PHOTO_DIR, f"event_{event_id}")
    for name in (photo["filename"], photo["thumbnail"], photo["original"] or ""):
        if not name:
            continue
        path = os.path.join(event_dir, name)
        if os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass
    delete_photo(photo_id)

    next_url = request.referrer or url_for("event.detail", event_id=event_id)
    return redirect(next_url)