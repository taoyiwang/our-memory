#!/bin/bash
# 一键启动 —— 我们的故事
# 用法: ./start.sh

set -e

cd "$(dirname "$0")"

# 检查 .env 是否存在
if [ ! -f deploy/.env ]; then
    echo "❌ 请先配置 deploy/.env（参考 deploy/.env.example）"
    exit 1
fi

# 加载环境变量
set -a
source deploy/.env
set +a

# 首次运行：创建虚拟环境 + 安装依赖
if [ ! -d venv ]; then
    echo "⏳ 创建虚拟环境..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

# 构建 CSS（每次启动都执行，确保样式最新）
if [ -f package.json ] && ! ./venv/bin/python -c "import os; exit(0 if os.path.exists('static/css/app.css') else 1)" 2>/dev/null; then
    echo "⏳ 构建 CSS..."
    npm install --silent
    npm run build:css
fi

echo "🚀 启动中..."
echo "   访问: https://doubledate.duckdns.org:8443"

exec ./venv/bin/gunicorn \
    -w 1 \
    --threads 4 \
    -b 127.0.0.1:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    app:app