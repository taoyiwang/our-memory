#!/bin/bash
# 一键启动 —— doubledate的冒险
# 用法: ./start.sh              # 后台启动
#       ./start.sh stop          # 停止
#       ./start.sh restart       # 重启
#       ./start.sh logs          # 查看日志

set -e

cd "$(dirname "$0")"

PID_FILE=".gunicorn.pid"

stop() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🛑 停止 gunicorn (PID: $pid)..."
            kill "$pid"
            sleep 1
            kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
    else
        # 兜底：杀掉所有 gunicorn 进程
        pkill -f "gunicorn.*app:app" 2>/dev/null && echo "🛑 已清理残留进程" || true
    fi
}

case "${1:-}" in
    stop)
        stop
        echo "✅ 已停止"
        exit 0
        ;;
    restart)
        stop
        ;;
    logs)
        if [ -f "$PID_FILE" ]; then
            tail -f /tmp/timeline.log
        else
            echo "❌ 服务未运行"
            exit 1
        fi
        ;;
esac

# 先停掉旧进程
stop

# 检查 .env
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

# 构建 CSS
if [ -f package.json ] && [ ! -f static/css/app.css ]; then
    echo "⏳ 构建 CSS..."
    npm install --silent
    npm run build:css
fi

echo "🚀 启动中..."
echo "   访问: https://doubledate.duckdns.org:8443"
echo "   日志: tail -f /tmp/timeline.log"

nohup ./venv/bin/gunicorn \
    -w 1 \
    --threads 4 \
    -b 127.0.0.1:8000 \
    --timeout 120 \
    --access-logfile /tmp/timeline.log \
    --error-logfile /tmp/timeline.log \
    --pid "$PID_FILE" \
    app:app > /dev/null 2>&1 &

# 用 shell 的 $! 记录 PID，比 gunicorn 写文件更快
echo $! > "$PID_FILE"
sleep 1

if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "✅ 已后台启动 (PID: $(cat "$PID_FILE"))"
else
    echo "❌ 启动失败，查看日志: tail -f /tmp/timeline.log"
    exit 1
fi