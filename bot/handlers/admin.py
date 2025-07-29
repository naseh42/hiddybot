import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton as IKB
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from bot.utils.db import DB_PATH
import aiosqlite, json

PLAN_NAME, PLAN_DAYS, PLAN_DATA, PLAN_PRICE = range(4)

async def admin_panel(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != int(os.getenv("ADMIN_ID", 0)):
        return
    kb = [
        [IKB("➕ تعریف پلن", callback_data="add_plan")],
        [IKB("📋 لیست پلن‌ها", callback_data="list_plans")],
        [IKB("📥 رسید‌های پرداخت", callback_data="receipts")],
        [IKB("🔖 تخفیف کاربر", callback_data="discount_user")],
        [IKB("👥 نمایندگان", callback_data="resellers")],
    ]
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "پنل ادمین", reply_markup=InlineKeyboardMarkup(kb))

# ---------- تعریف پلن ----------
async def add_plan(update: Update, _):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("نام پلن را وارد کنید:")
    return PLAN_NAME

async def plan_days(update: Update, context):
    context.user_data["plan_name"] = update.message.text
    await update.message.reply_text("مدت روزها را وارد کنید:")
    return PLAN_DAYS

async def plan_data(update: Update, context):
    context.user_data["plan_days"] = int(update.message.text)
    await update.message.reply_text("حجم (گیگ) را وارد کنید:")
    return PLAN_DATA

async def plan_price(update: Update, context):
    context.user_data["plan_data"] = int(update.message.text)
    await update.message.reply_text("قیمت (تومان) را وارد کنید:")
    return PLAN_PRICE

async def save_plan(update: Update, context):
    price = int(update.message.text)
    name, days, data = context.user_data["plan_name"], context.user_data["plan_days"], context.user_data["plan_data"]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO plans(name,days,data_gb,price) VALUES(?,?,?,?)",
                         (name, days, data, price))
        await db.commit()
    await update.message.reply_text("✅ پلن ذخیره شد.")
    return ConversationHandler.END

# ---------- لیست پلن‌ها ----------
async def list_plans(update: Update, _):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id,name,days,data_gb,price FROM plans") as cur:
            rows = await cur.fetchall()
    text = "\n".join(f"{r[0]} | {r[1]} | {r[2]} روز | {r[3]} GB | {r[4]} تومان" for r in rows)
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(text or "پلنی موجود نیست.")

# ---------- رسید‌ها ----------
async def receipts(update: Update, _):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id,user_id,amount,status FROM receipts WHERE status='pending'") as cur:
            rows = await cur.fetchall()
    kb = [[IKB(f"ردیف {r[0]} - {r[2]} تومان", callback_data=f"receipt_{r[0]}_{r[1]}_{r[2]}")] for r in rows]
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        "رسید‌های در انتظار:", reply_markup=InlineKeyboardMarkup(kb or []))

# ---------- تائید / رد رسید ----------
async def handle_receipt(update: Update, _):
    data = update.callback_query.data
    _, rid, uid, amount = data.split("_")
    uid, amount = int(uid), int(amount)
    action_kb = [
        [IKB("✅ تائید", callback_data=f"acc_{rid}_{uid}_{amount}")],
        [IKB("❌ رد", callback_data=f"rej_{rid}")]
    ]
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        f"رسید {amount} برای {uid}", reply_markup=InlineKeyboardMarkup(action_kb))

async def acc_receipt(update: Update, _):
    _, rid, uid, amount = update.callback_query.data.split("_")
    uid, amount = int(uid), int(amount)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE receipts SET status='approved' WHERE id=?", (rid,))
        await db.execute("INSERT OR IGNORE INTO wallets(user_id,balance) VALUES(?,0)", (uid,))
        await db.execute("UPDATE wallets SET balance=balance+? WHERE user_id=?", (amount, uid))
        await db.commit()
    await update.callback_query.answer("✅ رسید تائید و کیف‌پول شارژ شد.")

async def rej_receipt(update: Update, _):
    rid = update.callback_query.data.split("_")[1]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE receipts SET status='rejected' WHERE id=?", (rid,))
        await db.commit()
    await update.callback_query.answer("❌ رسید رد شد.")

# ---------- تخفیف ----------
async def discount_user(update: Update, _):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        "آیدی عددی کاربر + درصد تخفیف را بفرستید (مثال: 12345 20)")
    return 1

async def save_discount(update: Update, context):
    try:
        uid, pct = map(int, update.message.text.split())
    except:
        await update.message.reply_text("فرمت اشتباه است.")
        return
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO referrals(user_id, discount_percent) VALUES(?,?)",
                         (uid, pct))
        await db.commit()
    await update.message.reply_text("✅ تخفیف ثبت شد.")
    return ConversationHandler.END

def register(app):
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_home$"))
    app.add_handler(CallbackQueryHandler(list_plans, pattern="^list_plans$"))
    app.add_handler(CallbackQueryHandler(receipts, pattern="^receipts$"))
    app.add_handler(CallbackQueryHandler(handle_receipt, pattern="^receipt_"))
    app.add_handler(CallbackQueryHandler(acc_receipt, pattern="^acc_"))
    app.add_handler(CallbackQueryHandler(rej_receipt, pattern="^rej_"))

    plan_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_plan, pattern="^add_plan$")],
        states={
            PLAN_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, plan_days)],
            PLAN_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, plan_data)],
            PLAN_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, plan_price)],
            PLAN_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_plan)],
        },
        fallbacks=[]
    )
    app.add_handler(plan_conv)

    disc_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(discount_user, pattern="^discount_user$")],
        states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_discount)]},
        fallbacks=[]
    )
    app.add_handler(disc_conv)
