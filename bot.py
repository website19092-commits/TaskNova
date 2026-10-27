import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiohttp import web

# আপনার টোকেন ও লিংক
BOT_TOKEN = "8715331593:AAEX0JUAYn1P4Zpuy5s3jw58gqYua8Wz1zc"
WEB_APP_URL = "https://website19092-commits.github.io/TaskNova/"
PORT = int(os.environ.get("PORT", 8080))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌐 Open Dashboard App", web_app=WebAppInfo(url=WEB_APP_URL))],
            [KeyboardButton(text="➕ Register a new Gmail"), KeyboardButton(text="📧 My accounts")],
            [KeyboardButton(text="💰 Balance"), KeyboardButton(text="👥 My referrals")],
            [KeyboardButton(text="⚙️ Settings"), KeyboardButton(text="❓ Help")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    
    await message.answer(
        f"স্বাগতম {message.from_user.first_name}!\n\n"
        "**SM. TaskNova**-এ আপনাকে স্বাগতম।\n"
        "শুরু করতে নিচের '🌐 Open Dashboard App' বাটনে ক্লিক করুন।",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# রেন্ডারের জন্য ছোট একটি ডামি ওয়েবসাইট
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
