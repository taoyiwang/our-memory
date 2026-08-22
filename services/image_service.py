"""图片处理服务：压缩、转 WebP、生成缩略图。"""
import io
import os
import uuid

from PIL import Image, UnidentifiedImageError

import config

# 支持的上传格式
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic", ".bmp"}


def allowed_file(filename: str) -> bool:
    """判断扩展名是否允许。"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def _ensure_event_dir(event_id: int) -> str:
    """创建事件照片目录，返回绝对路径。"""
    path = os.path.join(config.PHOTO_DIR, f"event_{event_id}")
    os.makedirs(path, exist_ok=True)
    return path


def _rotate_by_exif(img: Image.Image) -> Image.Image:
    """按 EXIF 方向信息旋转图片。"""
    try:
        exif = img.getexif()
        orientation = exif.get(0x0112)  # EXIF Orientation
        if orientation == 3:
            img = img.rotate(180, expand=True)
        elif orientation == 6:
            img = img.rotate(270, expand=True)
        elif orientation == 8:
            img = img.rotate(90, expand=True)
    except Exception:
        pass  # 忽略无法读取的 EXIF
    return img


def _convert(img: Image.Image, quality: int, max_side) -> io.BytesIO:
    """统一转换为 RGB 模式、等比缩放、编码为 WebP。"""
    img = img.convert("RGB")
    if isinstance(max_side, tuple):
        size = max_side
    else:
        size = (max_side, max_side)
    img.thumbnail(size, Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=quality, method=4)
    buf.seek(0)
    return buf


def save_upload(file_storage, event_id: int) -> tuple[str, str, str]:
    """处理一张上传照片。

    返回 (filename, thumbnail, original) —— 存储于 event 目录下的相对文件名。
    保存三个文件：原始文件、全尺寸 WebP、缩略图 WebP。
    """
    if not allowed_file(file_storage.filename or ""):
        raise ValueError("不支持的图片格式")

    try:
        img = Image.open(file_storage.stream)
        img.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("请上传有效图片") from exc

    img = _rotate_by_exif(img)

    event_dir = _ensure_event_dir(event_id)
    base_name = f"{uuid.uuid4().hex}"

    # 原始文件（保留原始格式，用于下载）
    orig_ext = os.path.splitext(file_storage.filename)[1].lower()
    orig_name = f"{base_name}_orig{orig_ext}"
    file_storage.stream.seek(0)
    img.save(os.path.join(event_dir, orig_name), format=img.format or "JPEG")

    # 全尺寸 WebP
    full = _convert(img, config.IMAGE_QUALITY, config.FULL_SIZE)
    full_name = f"{base_name}.webp"
    with open(os.path.join(event_dir, full_name), "wb") as f:
        f.write(full.getvalue())

    # 缩略图
    thumb = _convert(img, 72, config.THUMBNAIL_SIZE)
    thumb_name = f"{base_name}_thumb.webp"
    with open(os.path.join(event_dir, thumb_name), "wb") as f:
        f.write(thumb.getvalue())

    return full_name, thumb_name, orig_name


def delete_event_photos(event_id: int) -> None:
    """删除事件对应整个照片目录。"""
    path = os.path.join(config.PHOTO_DIR, f"event_{event_id}")
    if os.path.isdir(path):
        for name in os.listdir(path):
            try:
                os.remove(os.path.join(path, name))
            except OSError:
                pass
        try:
            os.rmdir(path)
        except OSError:
            pass