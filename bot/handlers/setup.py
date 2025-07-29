from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters

ASK_TOKEN, ASK_ADMIN, ASK_URL, ASK_UUID, ASK_PASSWORD = range(5)

async def start_setup(update, context):
    await update.message.reply_text("🚀 شروع راه‌اندازی ربات...\nلطفاً توکن ربات تلگرام را ارسال کنید:")
    return ASK_TOKEN

async def ask_admin(update, context):
    context.user_data["bot_token"] = update.message.text
    await update.message.reply_text("حالا آیدی عددی ادمین را وارد کنید:")
    return ASK_ADMIN

async def ask_url(update, context):
    context.user_data["admin_id"] = int(update.message.text)
    await update.message.reply_text("لینک ادمین پنل (مثلاً https://domain/path) را وارد کنید:")
    return ASK_URL

async def ask_uuid(update, context):
    context.user_data["admin_url"] = update.message.text.rstrip("/")
    await update.message.reply_text("Secret Code (UUID) پنل را وارد کنید:")
    return ASK_UUID

async def ask_password(update, context):
    context.user_data["admin_uuid"] = update.message.text
    await update.message.reply_text("رمز عبور اضافی پنل را وارد کنید:")
    return ASK_PASSWORD

async def finish_setup(update, context):
    context.user_data["admin_password"] = update.message.text
    env_lines = [
        f"BOT_TOKEN={context.user_data['bot_token']}",
        f"ADMIN_ID={context.user_data['admin_id']}",
        f"HIDDIY_ADMIN_URL={context.user_data['admin_url']}",
        f"HIDDIY_UUID={context.user_data['admin_uuid']}",
        f"HIDDIY_PASSWORD={context.user_data['admin_password']}",
        "DB_URL=sqlite:///bot.db",
        "SETUP_DONE=true",
    ]
    with open(".env", "w") as f:
        f.write("\n".join(env_lines))
    await update.message.reply_text("✅ تنظیمات ذخیره شد. لطفاً ربات را ری‌استارت کنید.")
    return ConversationHandler.END

def register(app):
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start_setup)],
        states={
            ASK_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_admin)],
            ASK_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_url)],
            ASK_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_uuid)],
            ASK_UUID: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_password)],
            ASK_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish_setup)],
        },
        fallbacks=[]
    )
    app.add_handler(conv)
