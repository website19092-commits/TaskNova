import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
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

# মেইন কীবোর্ড (এখানে WebApp বাটনটা বাদ দেওয়া হয়েছে)
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💰 Balance"), KeyboardButton(text="👥 Referrals")],
            [KeyboardButton(text="⚙️ Settings"), KeyboardButton(text="💬 Help")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # ইউজারকে পাশের মেনু বাটন ব্যবহার করতে বলা হচ্ছে
    await message.answer(
        f"Welcome **{message.from_user.first_name}** to SM. TaskNova!\n\n"
        "👇 **How to open the App?**\n"
        "Click the **Menu Button (☰)** next to the chat box at the bottom to open the Dashboard and earn money!",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@dp.message(F.text == "💰 Balance")
async def btn_balance(message: types.Message):
    await message.answer("💰 **Balance:** $0.00\n⏳ **Hold Balance:** $0.00\n\n(Open the Menu App to see real balance)", parse_mode="Markdown")

@dp.message(F.text == "👥 Referrals")
async def btn_referrals(message: types.Message):
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{message.from_user.id}"
    await message.answer(f"👥 Share this link:\n`{ref_link}`", parse_mode="Markdown")

@dp.message(F.text == "⚙️ Settings")
async def btn_settings(message: types.Message):
    await message.answer("⚙️ Settings coming soon.")

@dp.message(F.text == "💬 Help")
async def btn_help(message: types.Message):
    await message.answer("💬 Contact Support: @SM_Shakib_Hasan")

# ================= API সার্ভার (Render-এ ঘুম তাড়ানোর জন্য) =================
async def handle_ping(request):
    return web.Response(text="Bot is running perfectly!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

async def main():
    await start_web_server()
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
