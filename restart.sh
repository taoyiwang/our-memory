#!/usr/bin/env bash
# 一键重启「doubledate的冒险」开发服务器
# 用法: ./restart.sh        （在 Git Bash / WSL 中直接执行）
#
# 做的事：
#   1. 停止旧的 app.py 进程（含 Flask reloader 父子进程）
#   2. 兜底清理仍占用 5000 端口的进程
#   3. 后台启动新服务，日志写入 logs/dev.log

set -euo pipefail
cd "$(dirname "$0")"

PORT="${PORT:-5000}"
LOG_DIR="logs"
LOG="$LOG_DIR/dev.log"
mkdir -p "$LOG_DIR"

echo "==> 停止旧进程…"
# 精确匹配本项目的 app.py 进程（父进程 + reloader 子进程一起清理）
powershell.exe -NoProfile -Command \
  "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -like '*app.py*' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force -ErrorAction SilentlyContinue }" \
  2>/dev/null || true

# 兜底：清理仍占用端口的进程
PIDS="$(netstat -ano | grep ":$PORT " | grep LISTENING | awk '{print $NF}' | sort -u || true)"
if [ -n "$PIDS" ]; then
  echo "   端口 $PORT 仍被占用，强制清理: $PIDS"
  for pid in $PIDS; do
    taskkill //F //PID "$pid" 2>/dev/null || kill "$pid" 2>/dev/null || true
  done
fi

sleep 1

echo "==> 启动服务（端口 $PORT，日志: $LOG）…"
nohup venv/Scripts/python.exe app.py >> "$LOG" 2>&1 &
SERVER_PID=$!
echo "   后台 PID: $SERVER_PID"

# 等待服务就绪
for _ in $(seq 1 20); do
  if curl -s -o /dev/null "http://127.0.0.1:$PORT/login"; then
    echo "==> ✅ 已启动: http://localhost:$PORT"
    echo "   （停止: taskkill //F //PID $SERVER_PID，或再次运行 ./restart.sh）"
    exit 0
  fi
  sleep 0.5
done

echo "==> ⚠️ 启动超时，最近日志如下："
tail -20 "$LOG" || true
exit 1
