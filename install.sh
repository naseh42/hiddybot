#!/usr/bin/env bash
set -e

echo "▶️  نصب ربات تلگرام Hiddify VPN ..."
echo "------------------------------------------------"

# تابع نصب داکر از مخزن اوبونتو
install_docker() {
    echo "📦 در حال نصب Docker از مخزن Ubuntu ..."
    sudo apt-get update -y
    sudo apt-get install -y docker.io docker-compose
    sudo systemctl enable --now docker
}

# بررسی وجود داکر
if ! command -v docker &> /dev/null; then
    install_docker
else
    echo "✅ Docker قبلاً نصب شده است."
fi

# مسیر نصب
INSTALL_DIR="/opt/hiddybot"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# clone یا update
if [[ ! -d .git ]]; then
    git clone https://github.com/naseh42/hiddybot.git .
else
    git pull origin main
fi

# wizard تعاملی
read -rp "توکن ربات تلگرام: " BOT_TOKEN
read -rp "آیدی عددی ادمین: " ADMIN_ID
read -rp "لینک ادمین پنل Hiddify (https://.../admin/): " HIDDIY_ADMIN_URL
read -rp "Secret Code (UUID) پنل: " HIDDIY_UUID
read -rp "رمز عبور اضافی پنل: " HIDDIY_PASSWORD

# ساخت .env
cat > .env <<EOF
BOT_TOKEN=$BOT_TOKEN
ADMIN_ID=$ADMIN_ID
HIDDIY_ADMIN_URL=$HIDDIY_ADMIN_URL
HIDDIY_UUID=$HIDDIY_UUID
HIDDIY_PASSWORD=$HIDDIY_PASSWORD
DB_URL=sqlite:///bot.db
SETUP_DONE=false
EOF

# پوشه‌های داده
mkdir -p data data/receipts

# build و run
docker compose down || true
docker compose up -d --build

echo "✅ ربات با موفقیت نصب و اجرا شد."
echo "در تلگرام /start را ارسال کنید تا wizard شروع شود."
