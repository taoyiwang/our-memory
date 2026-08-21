# gunicorn 生产配置
# 用法: gunicorn -c deploy/gunicorn.conf.py app:app

import multiprocessing
import os

# 绑定到本机回环地址，由 Nginx 反向代理
bind = "127.0.0.1:8000"

# worker 数 = CPU 核数 * 2 + 1（SQLite + 图片处理为 IO 密集，可用更多线程）
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
threads = 4
worker_class = "gthread"

# 超时与请求限制（图片上传大，放宽一些）
timeout = 120
graceful_timeout = 30

# 日志
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOGLEVEL", "info")

# 保护数据目录（上传的图片落在 data/photos，不受进程影响）
# 其余交给 Nginx 处理静态资源
