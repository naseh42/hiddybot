import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton as IKB
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from bot.utils.db import DB_PATH
import aiosqlite

async def start(update: Update, _):
    await update.message.reply_text(
        "به ربات خوش‌آمدید، برای خرید اشتراک روی /shop بزنید.")

async def shop(update: Update, _):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id,name,days,data_gb,price FROM plans") as cur:
            plans = await cur.fetchall()
    kb = [[IKB(f"{p[1]} - {p[4]} تومان", callback_data=f"buy_{p[0]}")] for p in plans]
    await update.message.reply_text(
        "پلن‌ها:", reply_markup=InlineKeyboardMarkup(kb))

async def buy(update: Update, _):
    plan_id = int(update.callback_query.data.split("_")[1])
    user_id = update.effective_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT price FROM plans WHERE id=?", (plan_id,)) as cur:
            price = (await cur.fetchone())[0]
        async with db.execute("SELECT balance FROM wallets WHERE user_id=?", (user_id,)) as cur:
            bal = (await cur.fetchone() or [0])[0]
    if bal < price:
        await update.callback_query.answer("موجودی کافی نیست، لطفاً کیف‌پول را شارژ کنید.")
        return
    # کسر از کیف‌پول
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE wallets SET balance=balance-? WHERE user_id=?", (price, user_id))
        await db.execute("INSERT INTO orders(user_id,plan_id,status) VALUES(?,?,'paid')", (user_id, plan_id))
        await db.commit()
    await update.callback_query.answer("✅ خرید انجام شد.")
    # در فاز بعد لینک سابسکریپشن ارسال می‌شود.

def register(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("shop", shop))
    app.add_handler(CallbackQueryHandler(buy, pattern="^buy_"))
