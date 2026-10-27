import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiohttp import web

# ==========================================
BOT_TOKEN = "8715331593:AAGGhE0Ghj-5fX7B691WWxGLojWPsgbW6T8"
WEB_APP_URL = "https://website19092-commits.github.io/TaskNova/"
ADMIN_ID = "8021210361"
PORT = int(os.environ.get("PORT", 8080))
# ==========================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_langs = {}

def get_text(key, lang="en", **kwargs):
    texts = {
        "welcome": {
            "en": "Welcome **{name}**!\n\nWelcome to **SM. TaskNova**.\nClick '🌐 Open Dashboard App' below to start.",
            "bn": "স্বাগতম **{name}**!\n\n**SM. TaskNova**-এ আপনাকে স্বাগতম।\nশুরু করতে নিচের '🌐 Open Dashboard App' বাটনে ক্লিক করুন।"
        },
        "btn_gmail": {"en": "➕ Register Gmail", "bn": "➕ জিমেইল রেজিস্টার"},
        "btn_accounts": {"en": "📧 My Accounts", "bn": "📧 আমার অ্যাকাউন্ট"},
        "btn_balance": {"en": "💰 Balance", "bn": "💰 ব্যালেন্স"},
        "btn_referrals": {"en": "👥 Referrals", "bn": "👥 রেফারেল"},
        "btn_settings": {"en": "⚙️ Settings", "bn": "⚙️ সেটিংস"},
        "btn_help": {"en": "💬 Help", "bn": "💬 সাহায্য"},
    }
    return texts.get(key, {}).get(lang, "")

def get_main_keyboard(lang="en"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌐 Open Dashboard App", web_app=WebAppInfo(url=WEB_APP_URL))],
            [KeyboardButton(text=get_text("btn_gmail", lang)), KeyboardButton(text=get_text("btn_accounts", lang))],
            [KeyboardButton(text=get_text("btn_balance", lang)), KeyboardButton(text=get_text("btn_referrals", lang))],
            [KeyboardButton(text=get_text("btn_settings", lang)), KeyboardButton(text=get_text("btn_help", lang))]
        ],
        resize_keyboard=True,
        is_persistent=True
    )

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    lang = user_langs.get(message.from_user.id, "en")
    await message.answer(
        get_text("welcome", lang, name=message.from_user.first_name),
        reply_markup=get_main_keyboard(lang),
        parse_mode="Markdown"
    )

@dp.message(Command("lang"))
async def cmd_lang(message: types.Message):
    current = user_langs.get(message.from_user.id, "en")
    new_lang = "bn" if current == "en" else "en"
    user_langs[message.from_user.id] = new_lang
    msg = "Language changed to **English**." if new_lang == "en" else "ভাষা **বাংলা**-তে পরিবর্তন করা হয়েছে।"
    await message.answer(msg, reply_markup=get_main_keyboard(new_lang), parse_mode="Markdown")

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID:
        await message.answer("⛔ দুঃখিত, আপনি এই কমান্ড ব্যবহার করার অনুমতি রাখেন না।")
        return
    admin_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Total Users"), KeyboardButton(text="📧 Add Gmail Data")],
            [KeyboardButton(text="📢 Broadcast Message"), KeyboardButton(text="⬅️ Back to Main Menu")]
        ],
        resize_keyboard=True
    )
    await message.answer("👑 **Admin Panel**-এ স্বাগতম।\nনিচের মেনু থেকে কাজ বেছে নিন:", reply_markup=admin_kb, parse_mode="Markdown")

@dp.message(F.text == "👤 Total Users")
async def admin_stats(message: types.Message):
    if str(message.from_user.id) == ADMIN_ID:
        await message.answer("📊 **User Stats**\n\nTotal Users: 1 (You)\nActive Today: 1\n(ডাটাবেস যুক্ত হলে আসল ডেটা দেখাবে)")

@dp.message(F.text == "📧 Add Gmail Data")
async def admin_add_gmail(message: types.Message):
    if str(message.from_user.id) == ADMIN_ID:
        await message.answer("📧 এখানে আপনি ফরম্যাটে জিমেইলের ডেটা পাঠাতে পারবেন:\n`email | password | name`")

@dp.message(F.text == "📢 Broadcast Message")
async def admin_broadcast(message: types.Message):
    if str(message.from_user.id) == ADMIN_ID:
        await message.answer("📢 এখানে মেসেজ লিখে পাঠালে সব ইউজার পাবে।")

@dp.message(F.text == "⬅️ Back to Main Menu")
async def admin_back(message: types.Message):
    lang = user_langs.get(message.from_user.id, "en")
    await message.answer("মেইন মেনুতে ফিরে আসা হলো।", reply_markup=get_main_keyboard(lang))

@dp.message(F.text.in_(["➕ Register Gmail", "➕ জিমেইল রেজিস্টার"]))
async def btn_gmail(message: types.Message):
    await message.answer("📧 Gmail registration system is coming soon!")

@dp.message(F.text.in_(["📧 My Accounts", "📧 আমার অ্যাকাউন্ট"]))
async def btn_accounts(message: types.Message):
    await message.answer("Your Gmail accounts list will appear here. (Under construction)")

@dp.message(F.text.in_(["💰 Balance", "💰 ব্যালেন্স"]))
async def btn_balance(message: types.Message):
    await message.answer("Your current balance: $0.00")

@dp.message(F.text.in_(["👥 Referrals", "👥 রেফারেল"]))
async def btn_referrals(message: types.Message):
    await message.answer("Invite friends and earn coins!")

@dp.message(F.text.in_(["⚙️ Settings", "⚙️ সেটিংস"]))
async def btn_settings(message: types.Message):
    await message.answer("⚙️ Settings\nUse /lang to change language.")

@dp.message(F.text.in_(["💬 Help", "💬 সাহায্য"]))
async def btn_help(message: types.Message):
    await message.answer("💬 Help & Support\nContact: @YourSupportUsername")

async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

async def main():
    await start_web_server()
    print("বট চালু হচ্ছে...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
