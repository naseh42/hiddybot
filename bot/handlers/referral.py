import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton as IKB
from telegram.ext import ContextTypes, CommandHandler
from bot.utils.db import DB_PATH
import aiosqlite

async def referral_link(update: Update, _):
    user_id = update.effective_user.id
    link = f"https://t.me/{os.getenv('BOT_USERNAME', 'mybot')}?start=ref{user_id}"
    await update.message.reply_text(f"لینک دعوت شما:\n{link}")

async def reseller_panel(update: Update, _):
    user_id = update.effective_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM resellers WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
    if not row:
        await update.message.reply_text("شما نماینده نیستید.")
        return
    await update.message.reply_text("پنل نماینده (به‌زودی)...")

def register(app):
    app.add_handler(CommandHandler("ref", referral_link))
    app.add_handler(CommandHandler("reseller", reseller_panel))
