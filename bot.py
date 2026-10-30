import asyncio
import logging
import os
import json
import firebase_admin
from firebase_admin import credentials, db
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiohttp import web

BOT_TOKEN = "8715331593:AAGGhE0Ghj-5fX7B691WWxGLojWPsgbW6T8"
WEB_APP_URL = "https://website19092-commits.github.io/TaskNova/"
ADMIN_ID = "8021210361"
PORT = int(os.environ.get("PORT", 8080))
FIREBASE_URL = "https://tasknova-19cf2-default-rtdb.firebaseio.com/"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

try:
    cred_json = os.environ.get("FIREBASE_CREDENTIALS")
    if cred_json:
        cred = credentials.Certificate(json.loads(cred_json))
        firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})
        print("Firebase Connected!")
except Exception as e:
    print(f"Firebase Error: {e}")

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💰 Balance"), KeyboardButton(text="👥 Referrals")],
            [KeyboardButton(text="⚙️ Settings"), KeyboardButton(text="💬 Help")]
        ], resize_keyboard=True, is_persistent=True
    )

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    uid = str(message.from_user.id)
    ref = db.reference(f'users/{uid}')
    if not ref.get():
        ref.set({"name": message.from_user.first_name, "balance": 0.0, "hold_balance": 0.0, "refs": 0})
        
    await message.answer(
        f"👑 **Welcome {message.from_user.first_name}**!\n👑 **স্বাগতম!**\n\n👇 Click the Menu Button (☰) to open App.",
        reply_markup=get_main_keyboard(), parse_mode="Markdown"
    )

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID: 
        return await message.answer("⛔ Access Denied. You are not the admin.")
    
    # এখানে অ্যাডমিন প্যানেলের সুন্দর লিংকটি তৈরি করা হলো
    admin_link = f"{WEB_APP_URL}?admin=1"
    
    text = (
        "👑 **𝗦𝗠. 𝗧𝗮𝘀𝗸𝗡𝗼𝘃𝗮 - 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗔𝗱𝗺𝗶𝗻**\n\n"
        "🛡️ Welcome to the master control panel.\n"
        "👇 Click the secure link below to open your dashboard:\n\n"
        f"🔗 **[Click Here to Open Admin Panel]({admin_link})**"
    )
    
    await message.answer(text, parse_mode="Markdown", disable_web_page_preview=True)

@dp.message(F.text == "💰 Balance")
async def btn_balance(message: types.Message):
    user = db.reference(f'users/{message.from_user.id}').get()
    bal = f"{user.get('balance', 0.0):.2f}" if user else "0.00"
    hold = f"{user.get('hold_balance', 0.0):.2f}" if user else "0.00"
    await message.answer(f"💰 **Balance:** ${bal}\n⏳ **Hold:** ${hold}", parse_mode="Markdown")

# ================= API =================
async def get_user(request):
    user_id = request.query.get("userId")
    user = db.reference(f'users/{user_id}').get()
    return web.json_response(user or {"balance": 0, "hold_balance": 0})

async def add_reward(request):
    data = await request.json()
    uid, amt = str(data.get("userId")), float(data.get("amount", 0))
    ref = db.reference(f'users/{uid}')
    if ref.get():
        ref.update({'hold_balance': db.ServerValue.increment(amt)})
    return web.json_response({"status": "success"})

# ================= ADMIN API =================
async def admin_get_users(request):
    users = db.reference('users').get() or {}
    user_list = []
    for uid, data in users.items():
        data['id'] = uid
        user_list.append(data)
    return web.json_response(user_list)

async def admin_update_balance(request):
    data = await request.json()
    uid = str(data.get("userId"))
    amount = float(data.get("amount"))
    action = data.get("action") # 'add' or 'subtract'
    
    ref = db.reference(f'users/{uid}')
    user = ref.get()
    if user:
        current_bal = user.get('balance', 0.0)
        new_bal = current_bal + amount if action == 'add' else max(0, current_bal - amount)
        ref.update({'balance': new_bal})
        return web.json_response({"status": "success", "new_balance": new_bal})
    return web.json_response({"status": "error", "message": "User not found"})

async def admin_broadcast(request):
    data = await request.json()
    text = data.get("text")
    users = db.reference('users').get() or {}
    success = 0
    for uid in users.keys():
        try:
            await bot.send_message(chat_id=uid, text=text, parse_mode="Markdown")
            success += 1
            await asyncio.sleep(0.05)
        except: pass
    return web.json_response({"status": "success", "sent": success})

async def ping(request): return web.Response(text="Bot is running!")

async def start_web():
    app = web.Application()
    app.router.add_get('/', ping)
    app.router.add_get('/api/user', get_user)
    app.router.add_post('/api/reward', add_reward)
    app.router.add_get('/api/admin/users', admin_get_users)
    app.router.add_post('/api/admin/update-balance', admin_update_balance)
    app.router.add_post('/api/admin/broadcast', admin_broadcast)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

async def main():
    await start_web()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
