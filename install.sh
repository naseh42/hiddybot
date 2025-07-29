#!/usr/bin/env bash
set -e
echo "▶️  نصب ربات تلگرام Hiddify VPN ..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
fi
mkdir -p /opt/hiddify-vpn-bot && cd /opt/hiddify-vpn-bot
# اگر فایل‌ها را دستی کپی کرده‌اید نیازی به git نیست
# git clone https://github.com/yourrepo/hiddify-vpn-bot.git .
cp .env.example .env
mkdir -p data data/receipts
docker compose up -d --build
echo "✅ ربات بالا آمد. حالا در تلگرام /start بزنید."
