import asyncio
import logging
import os
import json
import firebase_admin
from firebase_admin import credentials, db
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# ==========================================
BOT_TOKEN = "8715331593:AAGGhE0Ghj-5fX7B691WWxGLojWPsgbW6T8"
WEB_APP_URL = "https://website19092-commits.github.io/TaskNova/"
ADMIN_ID = "8021210361"
PORT = int(os.environ.get("PORT", 8080))
FIREBASE_URL = "https://tasknova-19cf2-default-rtdb.firebaseio.com/"
# ==========================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================= ফায়ারবেস কানেকশন =================
try:
    # Render-এর Environment Variable থেকে JSON চাবি লোড করা
    cred_json = os.environ.get("FIREBASE_CREDENTIALS")
    if cred_json:
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})
        print("Firebase Connected Successfully!")
    else:
        print("Warning: FIREBASE_CREDENTIALS not found in Environment Variables.")
except Exception as e:
    print(f"Firebase Error: {e}")

user_langs = {}
admin_states = {}

# ================= দ্বিভাষিক মেসেজ =================
TEXTS = {
    "welcome": "👑 **Welcome {name}**!\n👑 **স্বাগতম {name}**!\n\n🌟 Welcome to **𝗦𝗠. 𝗧𝗮𝘀𝗸𝗡𝗼𝘃𝗮**.\n🌟 **𝗦𝗠. 𝗧𝗮𝘀𝗸𝗡𝗼𝘃𝗮**-তে আপনাকে স্বাগতম।\n\n👇 Click the Menu Button to open App.\n👇 অ্যাপটি ওপেন করতে নিচের মেনু বাটনে ক্লিক করুন।",
    "balance": "💰 **Balance:** ${balance}\n💰 **ব্যালেন্স:** ${balance}\n\n⏳ **Hold Balance:** ${hold}\n⏳ **হোল্ড ব্যালেন্স:** ${hold}\n\n(Open App to see real balance / আসল ব্যালেন্স দেখতে অ্যাপে যান)",
    "refer": "👥 **Your Referral Link:**\n`{link}`\n\nShare with friends and earn.\nবন্ধুদের সাথে শেয়ার করুন এবং আয় করুন।",
    "help": "💬 **Help & Support**\n💬 **সাহায্য ও সাপোর্ট**\n\nContact us for any issue:\nযেকোনো সমস্যায় আমাদের সাথে যোগাযোগ করুন:",
    "settings": "⚙️ **Settings**\n⚙️ **সেটিংস**\n\nChange language using the /lang command.\nভাষা পরিবর্তন করতে /lang কমান্ডটি ব্যবহার করুন।",
    "lang_changed": "✅ Language changed to **English**.\n✅ ভাষা **ইংরেজি**-তে পরিবর্তন করা হয়েছে।",
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

# ================= ডাটাবেস ফাংশন =================
def create_user_if_not_exist(user_id, first_name):
    ref = db.reference(f'users/{user_id}')
    user = ref.get()
    if not user:
        new_user = {
            "name": first_name,
            "balance": 0.00,
            "hold_balance": 0.00,
            "refs": 0,
            "is_premium": False
        }
        ref.set(new_user)
        return new_user
    return user

def get_user(user_id):
    ref = db.reference(f'users/{user_id}')
    return ref.get()

# ================= কীবোর্ড ডিজাইন =================
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
        user_langs[uid] = "en"
    
    # ডাটাবেসে ইউজার সেভ করা
    create_user_if_not_exist(uid, message.from_user.first_name)
        
    await message.answer(
        get_text("welcome", name=message.from_user.first_name),
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

# ================= ভাষা পরিবর্তন (/lang) =================
@dp.message(Command("lang"))
async def cmd_lang(message: types.Message):
    await message.answer(get_text("lang_changed"), parse_mode="Markdown")

# ================= মেইন বাটন অ্যাকশন =================
@dp.message(F.text == "💰 Balance")
async def btn_balance(message: types.Message):
    uid = str(message.from_user.id)
    user_data = get_user(uid)
    
    if user_data:
        bal = f"{user_data.get('balance', 0.0):.2f}"
        hold = f"{user_data.get('hold_balance', 0.0):.2f}"
    else:
        bal, hold = "0.00", "0.00"
        
    await message.answer(get_text("balance", balance=bal, hold=hold), parse_mode="Markdown")

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
    admin_states[message.from_user.id] = None
    await message.answer(get_text("admin_panel"), reply_markup=get_admin_keyboard(), parse_mode="Markdown")

@dp.message(F.text == "⚙️ Back to Main Menu")
async def admin_back(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID: return
    admin_states[message.from_user.id] = None
    await message.answer("Returned to Main Menu.", reply_markup=get_main_keyboard())

@dp.message(F.text == "👤 Total Users")
async def admin_total_users(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID: return
    users_ref = db.reference('users')
    users = users_ref.get()
    count = len(users) if users else 0
    await message.answer(get_text("admin_total_users", count=count), parse_mode="Markdown")

@dp.message(F.text == "📢 Broadcast Message")
async def admin_broadcast_prompt(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID: return
    admin_states[message.from_user.id] = "broadcasting"
    await message.answer(get_text("admin_broadcast_prompt"), reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Cancel")]], resize_keyboard=True))

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
        users_ref = db.reference('users')
        users = users_ref.get()
        success = 0
        
        if users:
            for uid in users.keys():
                try:
                    await bot.send_message(chat_id=uid, text=message.text, parse_mode="Markdown")
                    success += 1
                    await asyncio.sleep(0.05) # স্প্যাম ব্লক এড়াতে
                except Exception:
                    pass
                    
        await message.answer(get_text("admin_broadcast_done", count=success), reply_markup=get_admin_keyboard(), parse_mode="Markdown")
        admin_states[message.from_user.id] = None

# ================= API সার্ভার (HTML থেকে ডেটা রিসিভ করার জন্য) =================
async def handle_get_user(request):
    user_id = request.query.get("userId")
    if not user_id:
        return web.json_response({"error": "Missing userId"}, status=400)
        
    user = get_user(user_id)
    if not user:
        user = {"balance": 0.00, "hold_balance": 0.00, "name": "User", "refs": 0}
    return web.json_response(user)

async def handle_add_reward(request):
    try:
        data = await request.json()
        user_id = str(data.get("userId"))
        amount = float(data.get("amount", 0))
        
        user_ref = db.reference(f'users/{user_id}')
        user = user_ref.get()
        
        if user:
            current_hold = user.get('hold_balance', 0.0)
            user_ref.update({'hold_balance': current_hold + amount})
            return web.json_response({"status": "success", "new_hold": current_hold + amount})
        return web.json_response({"status": "user_not_found"}, status=404)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

# রেন্ডারের পিং সার্ভার
async def handle_ping(request):
    return web.Response(text="Bot is running perfectly with Firebase!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    app.router.add_get('/api/user', handle_get_user)
    app.router.add_post('/api/reward', handle_add_reward)
    
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
