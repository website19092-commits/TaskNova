import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiohttp import web

# আপনার নতুন টোকেন এখানে বসানো হয়েছে
BOT_TOKEN = "8715331593:AAGGhE0Ghj-5fX7B691WWxGLojWPsgbW6T8"
WEB_APP_URL = "https://website19092-commits.github.io/TaskNova/"
PORT = int(os.environ.get("PORT", 8080))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ইউজারদের ভাষা মনে রাখার জন্য মেমরি (ডিফল্ট: English)
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

# ভাষা পরিবর্তনের কমান্ড (/lang)
@dp.message(Command("lang"))
async def cmd_lang(message: types.Message):
    current = user_langs.get(message.from_user.id, "en")
    new_lang = "bn" if current == "en" else "en"
    user_langs[message.from_user.id] = new_lang
    
    msg = "Language changed to **English**." if new_lang == "en" else "ভাষা **বাংলা**-তে পরিবর্তন করা হয়েছে।"
    await message.answer(msg, reply_markup=get_main_keyboard(new_lang), parse_mode="Markdown")

# ==========================================
# বাটনগুলোর অ্যাকশন
# ==========================================

@dp.message(F.text.in_(["➕ Register Gmail", "➕ জিমেইল রেজিস্টার"]))
async def btn_gmail(message: types.Message):
    lang = user_langs.get(message.from_user.id, "en")
    msg = "📧 Gmail registration system is coming soon! Use the Dashboard App for now." if lang == "en" else "📧 জিমেইল রেজিস্ট্রেশন সিস্টেম শীঘ্রই চালু হবে। ড্যাশবোর্ড অ্যাপ ব্যবহার করুন।"
    await message.answer(msg)

@dp.message(F.text.in_(["📧 My Accounts", "📧 আমার অ্যাকাউন্ট"]))
async def btn_accounts(message: types.Message):
    lang = user_langs.get(message.from_user.id, "en")
    msg = "Your Gmail accounts list will appear here. (Under construction)" if lang == "en" else "আপনার অ্যাকাউন্টের তালিকা এখানে দেখা যাবে। (নির্মাণাধীন)"
    await message.answer(msg)

@dp.message(F.text.in_(["💰 Balance", "💰 ব্যালেন্স"]))
async def btn_balance(message: types.Message):
    lang = user_langs.get(message.from_user.id, "en")
    msg = "Your current balance: $0.00\n(Real balance is in the Dashboard App)" if lang == "en" else "আপনার বর্তমান ব্যালেন্স: $0.00\n(আসল ব্যালেন্স ড্যাশবোর্ডে দেখুন)"
    await message.answer(msg)

@dp.message(F.text.in_(["👥 Referrals", "👥 রেফারেল"]))
async def btn_referrals(message: types.Message):
    lang = user_langs.get(message.from_user.id, "en")
    msg = "Invite friends and earn coins!\nYour link: https://t.me/YourBotLink" if lang == "en" else "বন্ধুদের ইনভাইট করে কয়েন আর্ন করুন!\nআপনার লিংক: https://t.me/YourBotLink"
    await message.answer(msg)

@dp.message(F.text.in_(["⚙️ Settings", "⚙️ সেটিংস"]))
async def btn_settings(message: types.Message):
    lang = user_langs.get(message.from_user.id, "en")
    msg = "⚙️ **Settings**\n\nUse `/lang` command to switch language." if lang == "en" else "⚙️ **সেটিংস**\n\nভাষা পরিবর্তন করতে `/lang` কমান্ডটি ব্যবহার করুন।"
    await message.answer(msg, parse_mode="Markdown")

@dp.message(F.text.in_(["💬 Help", "💬 সাহায্য"]))
async def btn_help(message: types.Message):
    lang = user_langs.get(message.from_user.id, "en")
    msg = "💬 **Help & Support**\n\nNeed assistance? Contact us: @YourSupportUsername" if lang == "en" else "💬 **সাহায্য ও সাপোর্ট**\n\nসমস্যা হলে যোগাযোগ করুন: @YourSupportUsername"
    await message.answer(msg, parse_mode="Markdown")

# রেন্ডারের জন্য সার্ভার
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
