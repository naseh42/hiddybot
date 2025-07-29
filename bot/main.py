import os, logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from bot.handlers import setup, admin, user, payment, referral
from bot.utils.db import init_db

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

async def post_init(app: Application) -> None:
    await init_db()
    logging.info("Bot started")

if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")
    if not token:
        logging.error("BOT_TOKEN not set!"); exit(1)

    app = Application.builder().token(token).post_init(post_init).build()
    setup.register(app)
    admin.register(app)
    user.register(app)
    payment.register(app)
    referral.register(app)
    app.run_polling()
