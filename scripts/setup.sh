#!/bin/bash
set -e

echo "=== 安裝 Docker ==="
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

echo "=== 安裝 Nginx ==="
sudo apt update
sudo apt install -y nginx

echo "=== 設定 Nginx ==="
sudo cp nginx/nicetomeetyou.conf /etc/nginx/sites-available/nicetomeetyou
sudo ln -sf /etc/nginx/sites-available/nicetomeetyou /etc/nginx/sites-enabled/nicetomeetyou
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo "=== 設定 .env ==="
if [ ! -f .env ]; then
    cp .env.example .env
    echo "請編輯 .env 填入正式環境設定後再執行 deploy.sh"
    exit 1
fi

echo "=== 完成！請執行 bash scripts/deploy.sh 啟動服務 ==="
