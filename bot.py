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

# ইউজারদের ভাষা মনে রাখার জন্য ডিকশনারি (ডিফল্ট বাংলা)
user_langs = {}

# ================= ভাষা ও ফ্যান্সি টেক্সট (Translations) =================
TEXTS = {
    "welcome": {
        "bn": "👑 স্বাগতম **{name}**!\n\n🌟 **𝗦𝗠. 𝗧𝗮𝘀𝗸𝗡𝗼𝘃𝗮**-তে আপনাকে স্বাগতম।\n\n👇 অ্যাপটি ওপেন করতে নিচের **☰ মেনু বাটনে** ক্লিক করুন।",
        "en": "👑 Welcome **{name}**!\n\n🌟 Welcome to **𝗦𝗠. 𝗧𝗮𝘀𝗸𝗡𝗼𝘃𝗮**.\n\n👇 Click the **☰ Menu Button** below to open the App."
    },
    "btn_balance": {"bn": "💰 ব্যালেন্স", "en": "💰 𝗕𝗮𝗹𝗮𝗻𝗰𝗲"},
    "btn_refer": {"bn": "👥 রেফারেল", "en": "👥 𝗥𝗲𝗳𝗲𝗿𝗿𝗮𝗹𝘀"},
    "btn_help": {"bn": "💬 সাহায্য", "en": "💬 𝗛𝗲𝗹𝗽"},
    "btn_admin": {"bn": "👑 অ্যাডমিন", "en": "👑 𝗔𝗱𝗺𝗶𝗻"},
    
    "balance_msg": {
        "bn": "💰 **আপনার ব্যালেন্স:** ${balance}\n⏳ **হোল্ড ব্যালেন্স:** ${hold}\n\n(অ্যাপে গিয়ে আসল ব্যালেন্স দেখুন)",
        "en": "💰 **𝗬𝗼𝘂𝗿 𝗕𝗮𝗹𝗮𝗻𝗰𝗲:** ${balance}\n⏳ **𝗛𝗼𝗹𝗱 𝗕𝗮𝗹𝗮𝗻𝗰𝗲:** ${hold}\n\n(Open App to see real balance)"
    },
    "refer_msg": {
        "bn": "👥 **আপনার রেফারেল লিংক:**\n`{link}`\n\nবন্ধুদের পাঠান, তারা জয়েন করলে আপনি কয়েন পাবেন!",
        "en": "👥 **𝗬𝗼𝘂𝗿 𝗥𝗲𝗳𝗲𝗿𝗿𝗮𝗹 𝗟𝗶𝗻𝗸:**\n`{link}`\n\nShare with friends and earn coins!"
    },
    "help_msg": {
        "bn": "💬 **সাহায্য ও সাপোর্ট**\n\nযেকোনো সমস্যায় আমাদের সাথে যোগাযোগ করুন:",
        "en": "💬 **𝗛𝗲𝗹𝗽 & 𝗦𝘂𝗽𝗽𝗼𝗿𝘁**\n\nContact us for any issue:"
    },
    "admin_panel": {
        "bn": "👑 **অ্যাডমিন প্যানেল**\n\nএখান থেকে সব কন্ট্রোল করুন:",
        "en": "👑 **𝗔𝗱𝗺𝗶𝗻 𝗣𝗮𝗻𝗲𝗹**\n\nControl everything here:"
    },
    "lang_changed": {
        "bn": "✅ ভাষা সফলভাবে **বাংলা** করা হয়েছে।",
        "en": "✅ Language successfully changed to **English**."
    }
}

def get_text(key, lang="bn"):
    return TEXTS.get(key, {}).get(lang, "Error")

# ================= কীবোর্ড ডিজাইন =================
def get_main_keyboard(lang="bn"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text("btn_balance", lang)), KeyboardButton(text=get_text("btn_refer", lang))],
            [KeyboardButton(text=get_text("btn_help", lang))]
        ],
        resize_keyboard=True,
        is_persistent=True
    )

# অ্যাডমিনদের জন্য আলাদা কীবোর্ড
def get_admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 Broadcast"), KeyboardButton(text="👤 Total Users")],
            [KeyboardButton(text="⚙️ Main Menu")]
        ],
        resize_keyboard=True
    )

# ================= স্টার্ট কমান্ড =================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    uid = str(message.from_user.id)
    lang = user_langs.get(uid, "bn") # ডিফল্ট বাংলা
    
    await message.answer(
        get_text("welcome", lang).format(name=message.from_user.first_name),
        reply_markup=get_main_keyboard(lang),
        parse_mode="Markdown"
    )

# ================= ভাষা পরিবর্তন (/lang) =================
@dp.message(Command("lang"))
async def cmd_lang(message: types.Message):
    uid = str(message.from_user.id)
    current_lang = user_langs.get(uid, "bn")
    new_lang = "en" if current_lang == "bn" else "bn"
    user_langs[uid] = new_lang
    
    await message.answer(
        get_text("lang_changed", new_lang),
        reply_markup=get_main_keyboard(new_lang),
        parse_mode="Markdown"
    )

# ================= মেইন বাটন অ্যাকশন =================
@dp.message(F.text.in_(["💰 ব্যালেন্স", "💰 𝗕𝗮𝗹𝗮𝗻𝗰𝗲"]))
async def btn_balance(message: types.Message):
    uid = str(message.from_user.id)
    lang = user_langs.get(uid, "bn")
    # আপাতত ডামি ডেটা, ডাটাবেস যুক্ত হলে আসল হবে
    await message.answer(get_text("balance_msg", lang).format(balance="0.00", hold="0.00"), parse_mode="Markdown")

@dp.message(F.text.in_(["👥 রেফারেল", "👥 𝗥𝗲𝗳𝗲𝗿𝗿𝗮𝗹𝘀"]))
async def btn_refer(message: types.Message):
    uid = str(message.from_user.id)
    lang = user_langs.get(uid, "bn")
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{message.from_user.id}"
    await message.answer(get_text("refer_msg", lang).format(link=ref_link), parse_mode="Markdown")

# ================= হেল্প ও সাপোর্ট =================
@dp.message(F.text.in_(["💬 সাহায্য", "💬 𝗛𝗲𝗹𝗽"]))
async def btn_help(message: types.Message):
    uid = str(message.from_user.id)
    lang = user_langs.get(uid, "bn")
    
    # প্রিমিয়াম সাপোর্ট বাটন
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 𝗧𝗲𝗹𝗲𝗴𝗿𝗮𝗺 𝗦𝘂𝗽𝗽𝗼𝗿𝘁", url="https://t.me/SM_Shakib_Hasan")],
        [InlineKeyboardButton(text="📞 𝗪𝗵𝗮𝘁𝘀𝗔𝗽𝗽", url="https://wa.me/880179136670")]
    ])
    
    await message.answer(get_text("help_msg", lang), reply_markup=inline_kb, parse_mode="Markdown")

# ================= অ্যাডমিন প্যানেল =================
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID: return
    await message.answer(get_text("admin_panel", "bn"), reply_markup=get_admin_keyboard(), parse_mode="Markdown")

@dp.message(F.text == "⚙️ Main Menu")
async def back_to_main(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID: return
    await message.answer("Main Menu", reply_markup=get_main_keyboard("bn"))

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
