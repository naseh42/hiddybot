#!/usr/bin/env bash
set -e

INSTALL_DIR="/opt/hiddybot"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# pull یا clone
[[ ! -d .git ]] && git clone https://github.com/naseh42/hiddybot.git . || git pull origin main

# ساخت .env.example در صورت نبود
[[ ! -f .env.example ]] && cat > .env.example <<'EOF'
BOT_TOKEN=
ADMIN_ID=
HIDDIY_ADMIN_URL=
HIDDIY_UUID=
HIDDIY_PASSWORD=
DB_URL=sqlite:///bot.db
SETUP_DONE=false
EOF

# نصب داکر در صورت نیاز
if ! command -v docker &>/dev/null; then
    sudo apt-get update -y
    sudo apt-get install -y docker.io docker-compose
    sudo systemctl enable --now docker
fi

# wizard اطلاعات
read -rp "توکن ربات تلگرام: " BOT_TOKEN
read -rp "آیدی عددی ادمین: " ADMIN_ID
read -rp "لینک ادمین پنل Hiddify (https://.../admin/): " HIDDIY_ADMIN_URL
read -rp "Secret Code (UUID) پنل: " HIDDIY_UUID
read -rp "رمز عبور اضافی پنل: " HIDDIY_PASSWORD

# ساخت فایل .env
cat > .env <<EOF
BOT_TOKEN=$BOT_TOKEN
ADMIN_ID=$ADMIN_ID
HIDDIY_ADMIN_URL=$HIDDIY_ADMIN_URL
HIDDIY_UUID=$HIDDIY_UUID
HIDDIY_PASSWORD=$HIDDIY_PASSWORD
DB_URL=sqlite:///bot.db
SETUP_DONE=false
EOF

# دایرکتوری‌ها و اجرا
mkdir -p data data/receipts
docker compose down 2>/dev/null || true
docker compose up -d --build

echo "✅ ربات آماده است؛ در تلگرام /start بزنید."
