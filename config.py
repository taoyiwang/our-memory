"""应用配置。"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 基础路径
DATA_DIR = os.path.join(BASE_DIR, "data")
PHOTO_DIR = os.path.join(DATA_DIR, "photos")
DB_PATH = os.path.join(DATA_DIR, "timeline.db")

# 确保数据目录存在
os.makedirs(PHOTO_DIR, exist_ok=True)

# 访问密码（部署时通过环境变量注入）
# 若未设置，使用开发默认值 123456
ACCESS_PASSWORD = os.environ.get("TIMELINE_PASSWORD", "123456")

# 数据库 URL
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Flask 密钥（用于 session 签名）
# 部署时务必通过环境变量设置
SECRET_KEY = os.environ.get("TIMELINE_SECRET", "dev-secret-change-me-in-production")
COOKIE_SECURE = os.environ.get("TIMELINE_COOKIE_SECURE", "0") == "1"
SESSION_DAYS = int(os.environ.get("TIMELINE_SESSION_DAYS", "30"))

# 图片处理
MAX_UPLOAD_SIZE = 15 * 1024 * 1024  # 15MB 单张
MAX_UPLOAD_COUNT = 20               # 单次最多 20 张
IMAGE_QUALITY = 82                  # WebP 质量
THUMBNAIL_SIZE = (600, 600)         # 缩略图最长边
FULL_SIZE = (1920, 1920)            # 全尺寸图最长边
