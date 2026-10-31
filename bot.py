import asyncio
import logging
import os
import json
import datetime
import uuid
import firebase_admin
from firebase_admin import credentials, db
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, LabeledPrice, PreCheckoutQuery, Message
from aiohttp import web

# ================= CONFIGURATION =================
BOT_TOKEN = "8715331593:AAEfoIGR79bdlR_x0k3Fo-8WEozphW_Z8KM" # নতুন টোকেন
WEB_APP_URL = "https://website19092-commits.github.io/TaskNova/"
ADMIN_ID = "8021210361"
PORT = int(os.environ.get("PORT", 8080))
FIREBASE_URL = "https://tasknova-19cf2-default-rtdb.firebaseio.com/"

POSTBACK_SECRET = "TaskNovaSecret123" 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================= FIREBASE SETUP =================
try:
    cred_json = os.environ.get("FIREBASE_CREDENTIALS")
    if cred_json:
        cred = credentials.Certificate(json.loads(cred_json))
        firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})
        print("✅ Firebase Connected Successfully!")
    else:
        print("⚠️ Warning: FIREBASE_CREDENTIALS env variable not found.")
except Exception as e:
    print(f"❌ Firebase Setup Error: {e}")

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💰 Balance"), KeyboardButton(text="👥 Referrals")],
            [KeyboardButton(text="⚙️ Settings"), KeyboardButton(text="💬 Help")]
        ], resize_keyboard=True, is_persistent=True
    )

# ================= TELEGRAM HANDLERS =================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    uid = str(message.from_user.id)
    ref = db.reference(f'users/{uid}')
    if not ref.get():
        ref.set({
            "name": message.from_user.first_name,
            "balance": 0.0,
            "hold_balance": 0.0,
            "is_premium": False,
            "refs": 0,
            "joined_at": datetime.datetime.now().isoformat()
        })
        
    await message.answer(
        f"👑 **Welcome {message.from_user.first_name}**!\n👑 **স্বাগতম!**\n\n👇 Click the Menu Button (☰) to open App.",
        reply_markup=get_main_keyboard(), parse_mode="Markdown"
    )

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID: 
        return await message.answer("⛔ Access Denied. You are not the admin.")
    
    admin_link = f"{WEB_APP_URL}#admin"
    
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

# ================= PREMIUM (TELEGRAM STARS) =================
@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@dp.message(F.successful_payment)
async def success_payment_handler(message: Message):
    uid = str(message.from_user.id)
    ref = db.reference(f'users/{uid}')
    if ref.get():
        ref.update({'is_premium': True})
    await message.answer(
        "🎉 **Premium Activated!**\n\n"
        "Thank you for your purchase.",
        parse_mode="Markdown"
    )

# ================= API ENDPOINTS =================
async def get_user(request):
    user_id = request.query.get("userId")
    user = db.reference(f'users/{user_id}').get()
    if user:
        return web.json_response({
            "balance": user.get('balance', 0.0),
            "is_premium": user.get('is_premium', False)
        })
    return web.json_response({"balance": 0, "is_premium": False})

async def add_reward(request):
    data = await request.json()
    uid = str(data.get("userId"))
    amt = float(data.get("amount", 0))
    ref = db.reference(f'users/{uid}')
    if ref.get():
        ref.update({'balance': db.ServerValue.increment(amt)})
    return web.json_response({"status": "success"})

async def create_invoice(request):
    data = await request.json()
    uid = data.get("userId")
    invoice_link = await bot.create_invoice_link(
        title="Premium Subscription",
        description="Unlock unlimited ads.",
        payload=f"premium_{uid}",
        provider_token="", 
        currency="XTR",
        prices=[LabeledPrice(label="Premium", amount=50)] 
    )
    return web.json_response({"invoiceLink": invoice_link})

# ================= WITHDRAW SYSTEM =================
async def submit_withdraw(request):
    data = await request.json()
    uid = str(data.get("userId"))
    amount = float(data.get("amount"))
    method = data.get("method")
    number = data.get("number")
    ref = db.reference(f'users/{uid}')
    user = ref.get()
    
    if user and user.get('balance', 0) >= amount:
        ref.update({
            'balance': db.ServerValue.increment(-amount),
            'hold_balance': db.ServerValue.increment(amount)
        })
        wd_id = str(uuid.uuid4())[:8]
        db.reference(f'withdrawals/{wd_id}').set({
            "userId": uid, "name": user.get('name', 'User'),
            "amount": amount, "method": method, "number": number,
            "status": "pending", "date": datetime.datetime.now().isoformat()
        })
        return web.json_response({"status": "success"})
    return web.json_response({"status": "error", "message": "Insufficient balance"})

async def get_user_withdrawals(request):
    uid = request.query.get("userId")
    withdrawals = db.reference('withdrawals').order_by_child('userId').equal_to(uid).get() or {}
    result = [dict(v, id=k) for k, v in withdrawals.items()]
    result.sort(key=lambda x: x.get('date', ''), reverse=True)
    return web.json_response(result)

# ================= ADMIN API =================
async def admin_get_users(request):
    users = db.reference('users').get() or {}
    return web.json_response([dict(v, id=k) for k, v in users.items()])

async def admin_get_withdrawals(request):
    wds = db.reference('withdrawals').order_by_child('status').equal_to('pending').get() or {}
    return web.json_response([dict(v, id=k) for k, v in wds.items()])

async def admin_process_withdraw(request):
    data = await request.json()
    wd_id, action = data.get("wdId"), data.get("action") 
    wd_ref = db.reference(f'withdrawals/{wd_id}')
    wd = wd_ref.get()
    if not wd or wd.get('status') != 'pending':
        return web.json_response({"status": "error", "message": "Invalid request"})
    uid, amount = wd['userId'], wd['amount']
    user_ref = db.reference(f'users/{uid}')
    
    if action == 'approve':
        wd_ref.update({'status': 'success'})
        user_ref.update({'hold_balance': db.ServerValue.increment(-amount)})
    else:
        wd_ref.update({'status': 'rejected'})
        user_ref.update({'hold_balance': db.ServerValue.increment(-amount), 'balance': db.ServerValue.increment(amount)})
    return web.json_response({"status": "success"})

async def admin_update_balance(request):
    data = await request.json()
    uid, amount, action = str(data.get("userId")), float(data.get("amount")), data.get("action") 
    ref = db.reference(f'users/{uid}')
    if ref.get():
        if action == 'add': ref.update({'balance': db.ServerValue.increment(amount)})
        else: ref.update({'balance': db.ServerValue.increment(-amount)})
        return web.json_response({"status": "success"})
    return web.json_response({"status": "error", "message": "User not found"})

async def admin_broadcast(request):
    data = await request.json()
    users = db.reference('users').get() or {}
    success = 0
    for uid in users.keys():
        try:
            await bot.send_message(chat_id=uid, text=data.get("text"), parse_mode="Markdown")
            success += 1
            await asyncio.sleep(0.05)
        except: pass
    return web.json_response({"status": "success", "sent": success})

# ================= POSTBACK (CPAGrip/Monetag) =================
async def cpa_postback(request):
    uid = request.query.get("user_id")
    amount_str = request.query.get("amount")
    secret = request.query.get("secret")
    
    if secret != POSTBACK_SECRET:
        return web.Response(text="❌ Error: Invalid Secret Key!", status=403)
        
    if not uid or not amount_str:
        return web.Response(text="❌ Error: Missing user_id or amount!", status=400)
        
    try:
        amount = float(amount_str)
        ref = db.reference(f'users/{uid}')
        user_data = ref.get()
        
        if user_data:
            ref.update({'balance': db.ServerValue.increment(amount)})
            return web.Response(text="OK", status=200)
        else:
            return web.Response(text=f"❌ Error: User ID {uid} not found in Firebase Database. Please press /start in bot first.", status=404)
            
    except Exception as e:
        return web.Response(text=f"❌ Firebase Error: {str(e)}", status=500)

async def ping(request): return web.Response(text="SM TaskNova Bot is running!")

# ================= APP START =================
async def start_web():
    app = web.Application()
    app.router.add_get('/', ping)
    app.router.add_get('/api/user', get_user)
    app.router.add_post('/api/reward', add_reward)
    app.router.add_post('/api/create-invoice', create_invoice)
    app.router.add_post('/api/withdraw', submit_withdraw)
    app.router.add_get('/api/user/withdrawals', get_user_withdrawals)
    app.router.add_get('/api/postback', cpa_postback)
    app.router.add_get('/api/admin/users', admin_get_users)
    app.router.add_get('/api/admin/withdrawals', admin_get_withdrawals)
    app.router.add_post('/api/admin/process-withdraw', admin_process_withdraw)
    app.router.add_post('/api/admin/update-balance', admin_update_balance)
    app.router.add_post('/api/admin/broadcast', admin_broadcast)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

async def main():
    await start_web()
    # ⚠️ এই লাইনটি নতুন যোগ করা হয়েছে: বট চালু হওয়ার আগেই পুরোনো কানেকশন মুছে ফেলবে
    await bot.delete_webhook(drop_pending_updates=True) 
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
