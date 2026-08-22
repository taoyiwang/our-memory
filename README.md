# doubledate的冒险 · 私人共享回忆时间轴

一个私密的多人共享回忆时间轴网站。几个朋友共同维护一条时间轴，记录一起经历的重要事件，每个事件关联照片与文字；输入访问密码即可进入，像翻阅一本数字相册。

> 打开网页 → 输入密码 → 滑动时间轴 → 回忆过去。

## 功能

- 🔐 **单密码访问**：一个私密空间、一个密码，Session 保持登录
- 🕰️ **优雅时间轴**：按日期倒序排列，卡片式大留白设计
- 📷 **照片记忆**：事件关联照片，瀑布流展示，全屏 Lightbox 浏览（支持滑动/方向键切换）
- ➕ **新增回忆**：Bottom Sheet 弹窗，日期/标题/地点/文字 + 多选照片一次保存
- ⬆️ **智能上传**：前端预览 → 后端 Pillow 压缩 → 转 WebP → 自动缩略图
- 📱 **移动优先**：iPhone 式安全区适配、大点击区域、底部操作栏
- 🛡️ **基础安全**：CSRF 防护、密码哈希、受保护的图片路由

## 技术栈

| 层 | 技术 |
| --- | --- |
| 后端 | Python Flask（Jinja2 SSR） |
| 数据库 | SQLite |
| 样式 | Tailwind CSS v4（`static/css/input.css` → 构建） |
| 交互 | Alpine.js + 原生 JS |
| 图片 | Pillow（压缩 / WebP / 缩略图） |
| 部署 | Gunicorn + Nginx（阿里云 ECS） |

## 本地开发

```bash
# 1. 创建虚拟环境
python -m venv venv
venv/Scripts/pip install -r requirements.txt   # Windows
# venv/bin/pip install -r requirements.txt      # macOS / Linux

# 2. 构建 CSS（Tailwind）
npm install
npm run build:css          # 开发时用 npm run watch:css 自动重建

# 3. 启动
venv/Scripts/python app.py  # Windows
# venv/bin/python app.py    # macOS / Linux
```

打开 http://localhost:5000 ，默认访问密码 `123456`（可通过环境变量 `TIMELINE_PASSWORD` 修改）。

> 注意：`app.py` 在启动时会自动建库并创建默认时间轴「doubledate的冒险」，数据落在 `data/timeline.db`，照片落在 `data/photos/event_<id>/`。

### 一键重启

改了代码想立刻生效？直接跑重启脚本（先停旧的、再起新的、自动等就绪，日志写到 `logs/dev.log`）：

```bash
# Git Bash / WSL
./restart.sh

# Windows：双击 restart.bat，或命令行执行
restart.bat
# （restart.bat 只是入口，核心逻辑在 restart.ps1，也可直接:
#  powershell -ExecutionPolicy Bypass -File restart.ps1）
```

重启后访问 `http://localhost:5000`。生产环境的重启是 `systemctl restart timeline`（见部署章节）。日志写到 `logs/dev.log`（stderr 在 `logs/dev.err.log`）。

## 配置（环境变量）

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `TIMELINE_PASSWORD` | `123456` | 访问密码 |
| `TIMELINE_SECRET` | dev 值 | Flask session 签名密钥，生产必改 |
| `TIMELINE_COOKIE_SECURE` | `0` | HTTPS 下设为 `1` |
| `TIMELINE_SESSION_DAYS` | `30` | 登录保持天数 |
| `PORT` | `5000` | 开发端口 |

## 测试

```bash
venv/Scripts/python -m unittest discover -s tests -v
```

覆盖：登录/登出 CSRF 流程、新增事件 + 照片上传、图片服务校验、日期格式化。

## 生产部署

详见 [`deploy/deploy.md`](deploy/deploy.md)，流程：

```
用户 → Nginx → Gunicorn → Flask → SQLite + 图片目录
```

要点：

- `gunicorn -c deploy/gunicorn.conf.py app:app` 启动
- systemd 服务文件见 `deploy/timeline.service`
- 通过环境变量注入真实密码与密钥（`deploy/.env.example`）
- 生产环境务必启用 HTTPS

## 目录结构

```text
├── app.py              # Flask 应用入口
├── config.py           # 配置
├── database.py         # SQLite 连接与建表
├── models/             # timeline / event / photo 数据模型
├── routes/             # auth / timeline / event / photo 路由
├── services/           # image_service 图片处理
├── templates/          # Jinja2 模板（含 Bottom Sheet partials）
├── static/             # css / js / img
├── data/               # timeline.db + photos/
├── tests/              # unittest 测试
└── deploy/             # Nginx / systemd / gunicorn 配置与部署文档
```

## License

私有项目。
