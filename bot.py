import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# আপনার দেওয়া টোকেনটি এখানে বসানো হয়েছে
BOT_TOKEN = "8715331593:AAEX0JUAYn1P4Zpuy5s3jw58gqYua8Wz1zc"

# আপনার ওয়েবসাইটের লিংক
WEB_APP_URL = "https://website19092-commits.github.io/TaskNova/" 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌐 Open Dashboard App", web_app=WebAppInfo(url=WEB_APP_URL))],
            [
                KeyboardButton(text="➕ Register a new Gmail"),
                KeyboardButton(text="📧 My accounts")
            ],
            [
                KeyboardButton(text="💰 Balance"),
                KeyboardButton(text="👥 My referrals")
            ],
            [
                KeyboardButton(text="⚙️ Settings"),
                KeyboardButton(text="❓ Help")
            ]
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

async def main():
    print("বট চালু হচ্ছে...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
