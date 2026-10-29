
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
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

# ইউজারদের ভাষা মনে রাখার জন্য (ডিফল্ট: en)
user_langs = {}
# অ্যাডমিনের কাজের স্টেট (ব্রডকাস্ট ইত্যাদির জন্য)
admin_states = {}

# ================= দ্বিভাষিক মেসেজ (Bilingual Texts) =================
TEXTS = {
    "welcome": "👑 **Welcome {name}**!\n👑 **স্বাগতম {name}**!\n\n🌟 Welcome to **𝗦𝗠. 𝗧𝗮𝘀𝗸𝗡𝗼𝘃𝗮**.\n🌟 **𝗦𝗠. 𝗧𝗮𝘀𝗸𝗡𝗼𝘃𝗮**-তে আপনাকে স্বাগতম।\n\n👇 Click the Menu Button to open App.\n👇 অ্যাপটি ওপেন করতে নিচের মেনু বাটনে ক্লিক করুন।",
    
    "balance": "💰 **Balance:** ${balance}\n💰 **ব্যালেন্স:** ${balance}\n\n⏳ **Hold Balance:** ${hold}\n⏳ **হোল্ড ব্যালেন্স:** ${hold}\n\n(Open App to see real balance / আসল ব্যালেন্স দেখতে অ্যাপে যান)",
    
    "refer": "👥 **Your Referral Link:**\n`{link}`\n\nShare with friends and earn.\nবন্ধুদের সাথে শেয়ার করুন এবং আয় করুন।",
    
    "help": "💬 **Help & Support**\n💬 **সাহায্য ও সাপোর্ট**\n\nContact us for any issue:\nযেকোনো সমস্যায় আমাদের সাথে যোগাযোগ করুন:",
    
    "settings": "⚙️ **Settings**\n⚙️ **সেটিংস**\n\nChange language using the /lang command.\nভাষা পরিবর্তন করতে /lang কমান্ডটি ব্যবহার করুন।",
    
    "lang_changed": "✅ Language changed to **English**.\n✅ ভাষা **ইংরেজি**-তে পরিবর্তন করা হয়েছে।",
    
    # Admin Texts
    "admin_panel": "👑 **Premium Admin Panel**\n👑 **প্রিমিয়াম অ্যাডমিন প্যানেল**\n\nControl everything below:\nনিচ থেকে সবকিছু কন্ট্রোল করুন:",
    "admin_broadcast_prompt": "📢 Send the message you want to broadcast to all users:\n📢 যে মেসেজটি সব ইউজারকে পাঠাতে চান, সেটি লিখুন:",
    "admin_broadcast_done": "✅ Broadcast sent to {count} users.\n✅ {count} জন ইউজারকে মেসেজ পাঠানো হয়েছে।",
    "admin_total_users": "👤 **Total Registered Users:** {count}\n👤 **মোট রেজিস্টার্ড ইউজার:** {count}"
}

def get_text(key, **kwargs):
    text = TEXTS.get(key, "Message not found.")
    for k, v in kwargs.items():
        text = text.replace(f"{{{k}}}", str(v))
    return text

# ================= কীবোর্ড ডিজাইন (সবসময় ইংরেজি) =================
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💰 Balance"), KeyboardButton(text="👥 Referrals")],
            [KeyboardButton(text="⚙️ Settings"), KeyboardButton(text="💬 Help")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )

def get_admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 Broadcast Message"), KeyboardButton(text="👤 Total Users")],
            [KeyboardButton(text="⚙️ Back to Main Menu")]
        ],
        resize_keyboard=True
    )

# ================= স্টার্ট কমান্ড =================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    uid = str(message.from_user.id)
    if uid not in user_langs:
        user_langs[uid] = "en" # ডিফল্ট ইংরেজি
        
    await message.answer(
        get_text("welcome", name=message.from_user.first_name),
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

# ================= ভাষা পরিবর্তন (/lang) =================
@dp.message(Command("lang"))
async def cmd_lang(message: types.Message):
    uid = str(message.from_user.id)
    # মেসেজ দ্বিভাষিক হবে, তবে কনফার্মেশন দেখাবে
    await message.answer(get_text("lang_changed"), parse_mode="Markdown")

# ================= মেইন বাটন অ্যাকশন =================
@dp.message(F.text == "💰 Balance")
async def btn_balance(message: types.Message):
    await message.answer(get_text("balance", balance="0.00", hold="0.00"), parse_mode="Markdown")

@dp.message(F.text == "👥 Referrals")
async def btn_refer(message: types.Message):
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{message.from_user.id}"
    await message.answer(get_text("refer", link=ref_link), parse_mode="Markdown")

@dp.message(F.text == "⚙️ Settings")
async def btn_settings(message: types.Message):
    await message.answer(get_text("settings"), parse_mode="Markdown")

@dp.message(F.text == "💬 Help")
async def btn_help(message: types.Message):
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Telegram Support", url="https://t.me/SM_Shakib_Hasan")],
        [InlineKeyboardButton(text="📞 WhatsApp", url="https://wa.me/880179136670")]
    ])
    await message.answer(get_text("help"), reply_markup=inline_kb, parse_mode="Markdown")


# ================= প্রিমিয়াম অ্যাডমিন প্যানেল =================
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID: return
    admin_states[message.from_user.id] = None # রিসেট স্টেট
    await message.answer(get_text("admin_panel"), reply_markup=get_admin_keyboard(), parse_mode="Markdown")

@dp.message(F.text == "⚙️ Back to Main Menu")
async def admin_back(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID: return
    admin_states[message.from_user.id] = None
    await message.answer("Returned to Main Menu.", reply_markup=get_main_keyboard())

@dp.message(F.text == "👤 Total Users")
async def admin_total_users(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID: return
    # আপাতত ডেমো কাউন্ট, ডাটাবেস যুক্ত হলে আসল হবে
    await message.answer(get_text("admin_total_users", count=1), parse_mode="Markdown")

@dp.message(F.text == "📢 Broadcast Message")
async def admin_broadcast_prompt(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID: return
    admin_states[message.from_user.id] = "broadcasting"
    await message.answer(get_text("admin_broadcast_prompt"), reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Cancel")]], resize_keyboard=True))

# ================= অ্যাডমিন স্টেট হ্যান্ডলার (ব্রডকাস্ট) =================
@dp.message(F.text == "Cancel")
async def cancel_admin(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID: return
    admin_states[message.from_user.id] = None
    await message.answer("Cancelled.", reply_markup=get_admin_keyboard())

@dp.message()
async def handle_admin_input(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID: return
    
    state = admin_states.get(message.from_user.id)
    if state == "broadcasting":
        # এখানে ডাটাবেস থেকে ইউজার এনে পাঠাতে হবে, আপাতত ডেমো
        await message.answer(get_text("admin_broadcast_done", count=1), reply_markup=get_admin_keyboard(), parse_mode="Markdown")
        admin_states[message.from_user.id] = None


# ================= API সার্ভার (UptimeRobot-এর জন্য) =================
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
