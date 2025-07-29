#!/usr/bin/env bash
set -e

echo "▶️  نصب ربات تلگرام Hiddify VPN ..."
echo "------------------------------------------------"

# 1) نصب داکر (در صورت نیاز)
if ! command -v docker &> /dev/null; then
    echo "در حال نصب Docker ..."
    sudo apt-get update -y
    sudo apt-get install -y docker.io docker-compose
    sudo systemctl enable --now docker
fi

# 2) ساخت پوشه پروژه
INSTALL_DIR="/opt/hiddybot"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# 3) clone یا update از گیت
if [[ ! -d .git ]]; then
    git clone https://github.com/naseh42/hiddybot.git .
else
    git pull origin main
fi

# 4) wizard دریافت اطلاعات
read -rp "لطفاً توکن ربات تلگرام را وارد کنید: " BOT_TOKEN
read -rp "آیدی عددی ادمین تلگرام: " ADMIN_ID
read -rp "لینک کامل ادمین پنل Hiddify (مثلاً https://.../admin/): " HIDDIY_ADMIN_URL
read -rp "Secret Code (UUID) پنل: " HIDDIY_UUID
read -rp "رمز عبور اضافی پنل: " HIDDIY_PASSWORD

# 5) ساخت فایل .env
cat > .env <<EOF
BOT_TOKEN=$BOT_TOKEN
ADMIN_ID=$ADMIN_ID
HIDDIY_ADMIN_URL=$HIDDIY_ADMIN_URL
HIDDIY_UUID=$HIDDIY_UUID
HIDDIY_PASSWORD=$HIDDIY_PASSWORD
DB_URL=sqlite:///bot.db
SETUP_DONE=false
EOF

# 6) ساخت دایرکتوری‌های داده
mkdir -p data data/receipts

# 7) build & run
docker compose down || true
docker compose up -d --build

echo "✅ ربات با موفقیت نصب و اجرا شد."
echo "برای تنظیمات اولیه در تلگرام /start را ارسال کنید."
