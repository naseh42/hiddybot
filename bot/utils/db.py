import os, aiosqlite
from pathlib import Path

DB_PATH = Path(os.getenv("DB_URL", "sqlite:///bot.db").replace("sqlite:///", ""))

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS config(key TEXT PRIMARY KEY, value TEXT)""")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS wallets(user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)""")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS plans(id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, days INTEGER, data_gb INTEGER, price INTEGER)""")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER, plan_id INTEGER, status TEXT, ref_code TEXT, created_at TEXT)""")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS referrals(
                user_id INTEGER PRIMARY KEY, inviter_id INTEGER, discount_percent INTEGER)""")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS resellers(
                user_id INTEGER PRIMARY KEY, credit INTEGER, commission_percent INTEGER)""")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS receipts(id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER, amount INTEGER, img_path TEXT, status TEXT, created_at TEXT)""")
        await db.commit()
