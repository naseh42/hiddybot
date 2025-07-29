import os, uuid
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton as IKB
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from bot.utils.db import DB_PATH
import aiosqlite, requests

RECEIPT_AMOUNT, RECEIPT_PHOTO = range(2)

async def wallet(update: Update, _):
    user_id = update.effective_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT balance FROM wallets WHERE user_id=?", (user_id,)) as cur:
            bal = (await cur.fetchone() or [0])[0]
    await update.message.reply_text(f"موجودی شما: {bal} تومان")

async def charge(update: Update, _):
    kb = [
        [IKB("💳 کارت‌به‌کارت", callback_data="receipt_pay")],
        [IKb("زرین‌پال", callback_data="zarinpal_pay")],
        [IKb("ارزی (TRC20)", callback_data="crypto_pay")],
    ]
    await update.message.reply_text(
        "روش شارژ را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(kb))

# ---------- کارت‌به‌کارت ----------
async def ask_receipt_amount(update: Update, _):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("مبلغ شارژ را وارد کنید:")
    return RECEIPT_AMOUNT

async def ask_receipt_photo(update: Update, context):
    context.user_data["amount"] = int(update.message.text)
    await update.message.reply_text("عکس رسید را ارسال کنید:")
    return RECEIPT_PHOTO

async def save_receipt(update: Update, context):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    fname = f"data/receipts/{uuid.uuid4()}.jpg"
    os.makedirs("data/receipts", exist_ok=True)
    await file.download_to_drive(fname)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO receipts(user_id,amount,img_path,status) VALUES(?,?,?,'pending')",
            (update.effective_user.id, context.user_data["amount"], fname))
        await db.commit()
    await update.message.reply_text("✅ رسید برای ادمین ارسال شد.")
    return ConversationHandler.END

# ---------- زرین‌پال ----------
async def zarinpal_pay(update: Update, _):
    # در اینجا فقط Authority می‌گیریم (نیاز به merchant در env)
    await update.callback_query.answer("به زودی...", show_alert=True)

# ---------- ارزی ----------
async def crypto_pay(update: Update, _):
    addr = os.getenv("CRYPTO_WALLET_ADDRESS", "TXxxx")
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        f"لطفاً به آدرس زیر {addr} واریز کنید و ID تراکنش را ارسال کنید.")

def register(app):
    app.add_handler(CommandHandler("wallet", wallet))
    app.add_handler(CommandHandler("charge", charge))

    receipt_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(ask_receipt_amount, pattern="^receipt_pay$")],
        states={
            RECEIPT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_receipt_photo)],
            RECEIPT_PHOTO: [MessageHandler(filters.PHOTO, save_receipt)],
        },
        fallbacks=[]
    )
    app.add_handler(receipt_conv)
    app.add_handler(CallbackQueryHandler(zarinpal_pay, pattern="^zarinpal_pay$"))
    app.add_handler(CallbackQueryHandler(crypto_pay, pattern="^crypto_pay$"))
