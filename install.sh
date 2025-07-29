#!/usr/bin/env bash
set -e

INSTALL_DIR="/opt/hiddybot"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# --- 1) دریافت / بروزرسانی سورس ---
[[ ! -d .git ]] && git clone https://github.com/naseh42/hiddybot.git . || git pull origin main

# --- 2) نصب داکر از مخزن اوبونتو (در صورت نیاز) ---
if ! command -v docker &>/dev/null; then
    sudo apt-get update -y
    sudo apt-get install -y docker.io docker-compose
    sudo systemctl enable --now docker
fi

# --- 3) ساخت Dockerfile در صورت نبود ---
[[ ! -f Dockerfile ]] && cat > Dockerfile <<'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "-m", "bot.main"]
EOF

# --- 4) ساخت requirements.txt در صورت نبود ---
[[ ! -f requirements.txt ]] && cat > requirements.txt <<'REQ'
python-telegram-bot[job-queue]==20.8
requests==2.31.0
python-dotenv==1.0.0
pydantic==2.5.0
aiosqlite==0.19.0
qrcode[pil]==7.4.2
cryptography==41.0.7
REQ

# --- 5) ساخت docker-compose.yml در صورت نبود ---
[[ ! -f docker-compose.yml ]] && cat > docker-compose.yml <<'YML'
version: "3.9"
services:
  bot:
    build: .
    container_name: hiddify_bot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./data:/app/data
YML

# --- 6) wizard تعاملی ---
echo "------------------------------------------------"
read -rp "توکن ربات تلگرام: " BOT_TOKEN
read -rp "آیدی عددی ادمین: " ADMIN_ID
read -rp "لینک ادمین پنل Hiddify (https://.../admin/): " HIDDIY_ADMIN_URL
read -rp "Secret Code (UUID) پنل: " HIDDIY_UUID
read -rp "رمز عبور اضافی پنل: " HIDDIY_PASSWORD
echo "------------------------------------------------"

# --- 7) ساخت .env ---
cat > .env <<EOF
BOT_TOKEN=$BOT_TOKEN
ADMIN_ID=$ADMIN_ID
HIDDIY_ADMIN_URL=$HIDDIY_ADMIN_URL
HIDDIY_UUID=$HIDDIY_UUID
HIDDIY_PASSWORD=$HIDDIY_PASSWORD
DB_URL=sqlite:///bot.db
SETUP_DONE=false
EOF

# --- 8) پوشه‌های داده و اجرا ---
mkdir -p data data/receipts
docker-compose down 2>/dev/null || true
docker-compose up -d --build

echo "✅ ربات نصب و اجرا شد."
echo "در تلگرام /start را ارسال کنید."
