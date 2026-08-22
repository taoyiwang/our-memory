# 部署指南（一键启动）

## 1. 拉取代码

```bash
cd /home/wty
git clone https://github.com/taoyiwang/our-memory.git timeline
cd timeline
```

## 2. 配置密钥

```bash
cp deploy/.env.example deploy/.env
nano deploy/.env
```

修改：

```
TIMELINE_PASSWORD=你自己设的登录密码
TIMELINE_SECRET=你自己设的一段长文本最少20字符
TIMELINE_COOKIE_SECURE=1
```

## 3. 配置 Nginx

```bash
cat > /etc/nginx/conf.d/duckdns.conf << 'EOF'
server {
    listen 8443 ssl;
    server_name doubledate.duckdns.org;

    ssl_certificate /etc/letsencrypt/live/doubledate.duckdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/doubledate.duckdns.org/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 300m;
    client_body_timeout 120s;

    location /static/ {
        alias /home/wty/timeline/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
EOF

nginx -t && systemctl reload nginx
```

## 4. 启动

```bash
chmod +x start.sh
./start.sh
```

## 5. 验证

浏览器访问 `https://doubledate.duckdns.org:8443`

## 更新代码

```bash
cd /home/wty/timeline
git pull
# 停掉旧进程，重新启动
pkill -f "gunicorn.*app:app"
./start.sh
```

## 后台运行

```bash
nohup ./start.sh > /dev/null 2>&1 &
```

## 备份

```bash
tar czf /backup/timeline-$(date +%F).tar.gz /home/wty/timeline/data
```