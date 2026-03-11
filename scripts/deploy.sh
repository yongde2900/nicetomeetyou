#!/bin/bash
set -e

echo "=== 拉取最新程式碼 ==="
git pull

echo "=== 啟動服務 ==="
docker compose up -d --build

echo "=== 收集 Static Files ==="
docker compose exec web python manage.py collectstatic --noinput

echo "=== 部署完成 ==="
docker compose ps
