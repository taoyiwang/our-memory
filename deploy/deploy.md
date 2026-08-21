# 部署指南（阿里云 ECS）

架构：`用户 → Nginx → Gunicorn → Flask → SQLite + 图片目录`

## 1. 服务器准备（一次性）

以 Ubuntu/Debian 为例（阿里云 ECS 默认镜像）。

```bash
# 系统更新 + 安装依赖
apt update
apt install -y python3 python3-venv python3-pip nginx git

# 创建应用目录与运行用户
mkdir -p /var/www/timeline
useradd -r -s /usr/sbin/nologin www-data 2>/dev/null || true
```

## 2. 部署代码

```bash
cd /var/www/timeline
# 方式一：git clone 项目到当前目录
# 方式二：本地打包上传（scp / rsync）

# 创建虚拟环境并安装依赖
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## 3. 配置环境变量

```bash
cp deploy/.env.example deploy/.env
nano deploy/.env
# 修改 TIMELINE_PASSWORD 与 TIMELINE_SECRET
# 启用 HTTPS 后把 TIMELINE_COOKIE_SECURE 设为 1
```

## 4. 配置 systemd 服务

```bash
cp deploy/timeline.service /etc/systemd/system/timeline.service
systemctl daemon-reload
systemctl enable --now timeline
systemctl status timeline    # 确认 active (running)
```

## 5. 配置 Nginx

```bash
# 修改域名
sed -i 's/your-domain.com/你的域名/g' deploy/nginx.conf
cp deploy/nginx.conf /etc/nginx/sites-available/timeline
ln -sf /etc/nginx/sites-available/timeline /etc/nginx/sites-enabled/timeline
rm -f /etc/nginx/sites-enabled/default    # 移除默认站点（可选）

nginx -t        # 检查配置
systemctl reload nginx
```

## 6. 数据与权限

```bash
# 首次启动时 Flask 会自动建库 + 建默认时间轴（data/timeline.db）
# 确保 www-data 可读写数据目录
chown -R www-data:www-data /var/www/timeline/data
chmod 750 /var/www/timeline/data
```

## 7. 验证

```bash
# 本地探活（Gunicorn 监听 127.0.0.1:8000）
curl -I http://127.0.0.1:8000/login

# 通过域名访问
curl -I http://你的域名/login
```

## 8. HTTPS（强烈建议）

```bash
# 方式一：Certbot（Let's Encrypt）
apt install -y certbot python3-certbot-nginx
certbot --nginx -d 你的域名

# 方式二：阿里云免费证书
# 下载证书 → 上传到 /etc/nginx/cert/ → 在 nginx.conf 增加 443 配置
# 证书申请后把 deploy/.env 的 TIMELINE_COOKIE_SECURE 设为 1 并重启
```

## 9. 备份（定期）

```bash
# 数据库 + 照片目录一键打包
tar czf /backup/timeline-$(date +%F).tar.gz /var/www/timeline/data
# 建议配合 crontab 定时执行，保留最近 7 份
```

## 10. 更新

```bash
cd /var/www/timeline
git pull                      # 或重新上传代码
./venv/bin/pip install -r requirements.txt   # 依赖有变化时
systemctl restart timeline    # 无需重启 Nginx（配置未变）
```
