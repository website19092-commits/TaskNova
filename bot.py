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
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery, Message
from aiohttp import web

# ================= CONFIGURATION =================
BOT_TOKEN = "8715331593:AAEfoIGR79bdlR_x0k3Fo-8WEozphW_Z8KM"
WEB_APP_URL = "https://website19092-commits.github.io/TaskNova/"
ADMIN_ID = "8021210361"
PORT = int(os.environ.get("PORT", 8080))
RENDER_URL = "https://tasknova-6mjt.onrender.com"
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

# ================= KEYBOARDS =================
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💰 Balance"), KeyboardButton(text="📜 History")],
            [KeyboardButton(text="👥 Referrals"), KeyboardButton(text="💬 Help")]
        ], resize_keyboard=True, is_persistent=True
    )

def get_help_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📢 Telegram Support", url="https://t.me/SM_Shakib_Hasan"),
                InlineKeyboardButton(text="💬 WhatsApp Support", url="https://wa.me/880179136670")
            ]
        ]
    )

# ================= GLOBAL ERROR HANDLER =================
@dp.errors()
async def errors_handler(update: types.Update, exception: Exception):
    print(f"⚠️ Bot Error: {exception}")
    try:
        if update.message:
            await update.message.answer("⚠️ **An internal error occurred. Please try again.**\n**একটি সমস্যা হয়েছে। আবার চেষ্টা করুন।**")
    except: pass
    return True

# ================= TELEGRAM HANDLERS =================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    try:
        uid = str(message.from_user.id)
        ref = db.reference(f'users/{uid}')
        user_data = ref.get()
        
        if user_data and user_data.get('banned', False):
            return await message.answer("⛔ **Your account is permanently banned.**\n**আপনার অ্যাকাউন্ট স্থায়ীভাবে ব্যান করা হয়েছে।**")

        args = message.text.split()
        if len(args) > 1 and args[1].startswith("ref_") and not user_data:
            referrer_id = args[1].replace("ref_", "")
            if referrer_id != uid:
                ref_ref = db.reference(f'users/{referrer_id}')
                if ref_ref.get():
                    ref_ref.child('balance').transaction(lambda current: max(0, (current or 0)) + 0.05)
                    ref_ref.child('refs').transaction(lambda current: (current or 0) + 1)
                    try:
                        await bot.send_message(referrer_id, "🎉 **New Referral! / নতুন রেফারেল!**\nYou earned $0.05 for inviting a friend.")
                    except: pass

        if not user_data:
            ref.set({
                "name": message.from_user.first_name,
                "balance": 0.0,
                "hold_balance": 0.0,
                "is_premium": False,
                "refs": 0,
                "joined_at": datetime.datetime.now().isoformat(),
                "banned": False
            })
            
        welcome_text = (
            f"👑 **Welcome {message.from_user.first_name}**!\n"
            f"👑 **স্বাগতম {message.from_user.first_name}**!\n\n"
            "👇 Click the Menu Button (☰) to open App.\n"
            "👇 অ্যাপটি ওপেন করতে নিচের মেনু বাটনে (☰) ক্লিক করুন।"
        )
        
        await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")
    except Exception as e:
        print(f"Start Error: {e}")

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID: 
        return await message.answer("⛔ Access Denied. You are not the admin.\n**আপনি অ্যাডমিন নন।**")
    
    admin_link = f"{WEB_APP_URL}admin.html"
    text = (
        "👑 **𝗦𝗠. 𝗧𝗮𝘀𝗸𝗡𝗼𝘃𝗮 - 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗔𝗱𝗺𝗶𝗻**\n\n"
        "🛡️ Welcome to the master control panel.\n"
        "👇 Click the secure link below to open your dashboard:\n\n"
        f"🔗 **[Click Here to Open Admin Panel]({admin_link})**"
    )
    await message.answer(text, parse_mode="Markdown", disable_web_page_preview=True)

# এখানে F.text.contains ব্যবহার করা হয়েছে যাতে ইমোজির জন্য বাটন কাজ না করার সমস্যা না হয়।
@dp.message(Command("balance") | F.text.contains("Balance"))
async def btn_balance(message: types.Message):
    try:
        user = db.reference(f'users/{message.from_user.id}').get()
        bal = max(0, float(user.get('balance', 0.0))) if user else 0.0
        text = f"💰 **Total Balance / মোট ব্যালেন্স:** ${bal:.2f}"
        await message.answer(text, parse_mode="Markdown")
    except Exception as e:
        print(f"Balance Error: {e}")
        await message.answer("⚠️ **Error loading balance.**\n**ব্যালেন্স লোড করতে সমস্যা হচ্ছে।**")

@dp.message(Command("history") | F.text.contains("History"))
async def btn_history(message: types.Message):
    try:
        uid = str(message.from_user.id)
        withdrawals = db.reference('withdrawals').order_by_child('userId').equal_to(uid).get() or {}
        
        if not withdrawals:
            return await message.answer("📜 **No withdrawal history found.**\n**কোনো উইথড্র হিস্ট্রি পাওয়া যায়নি।**")
        
        if not isinstance(withdrawals, dict):
            return await message.answer("⚠️ **Invalid data format.**\n**ডাটা ফরম্যাটে সমস্যা আছে।**")

        sorted_wds = sorted(withdrawals.values(), key=lambda x: str(x.get('date', '')), reverse=True)
        
        text = "📜 **Your Recent Withdrawals / আপনার সাম্প্রতিক উইথড্র:**\n\n"
        
        for wd in sorted_wds[:5]:
            status_raw = str(wd.get('status', 'pending')).lower()
            if status_raw == 'pending':
                status = "🟡 Pending"
            elif status_raw == 'success':
                status = "🟢 Success"
            else:
                status = "🔴 Rejected"
                
            date_str = str(wd.get('date', ''))[:10] 
            amount = float(wd.get('amount', 0))
            method = str(wd.get('method', 'bKash')).capitalize()
            
            text += f"💵 **${amount:.2f}** | {method}\n"
            text += f"📌 Status: {status}\n"
            text += f"📅 Date: {date_str}\n"
            text += "───────────────\n"
            
        text += "\n👉 _To see all history, open the Web App._"
        await message.answer(text, parse_mode="Markdown")
    except Exception as e:
        print(f"History Error: {e}")
        await message.answer("⚠️ **Error loading history. Please try again later.**\n**হিস্ট্রি লোড করতে সমস্যা হচ্ছে। আবার চেষ্টা করুন।**")

@dp.message(Command("refer") | F.text.contains("Referrals"))
async def btn_referrals(message: types.Message):
    try:
        uid = str(message.from_user.id)
        ref_link = f"https://t.me/SMTaskNova_bot?start=ref_{uid}"
        text = (
            "👥 **Invite & Earn / ইনভাইট এবং আর্ন**\n\n"
            "Share your link with friends and earn $0.05 for every new user!\n"
            "আপনার বন্ধুদের সাথে লিংকটি শেয়ার করুন এবং প্রতিটি নতুন ইউজারের জন্য $0.05 আয় করুন!\n\n"
            f"🔗 **Your Link / আপনার লিংক:**\n`{ref_link}`\n\n"
            "_(Tap the link to copy / কপি করতে লিংকে ট্যাপ করুন)_"
        )
        await message.answer(text, parse_mode="Markdown")
    except Exception as e:
        await message.answer("⚠️ **Error loading referral link.**")

@dp.message(Command("help") | F.text.contains("Help"))
async def btn_help(message: types.Message):
    text = (
        "💬 **Help & Support / হেল্প এবং সাপোর্ট**\n\n"
        "If you face any issues, please contact our support team below.\n"
        "যদি কোনো সমস্যা হয়, তবে নিচের সাপোর্ট টিমের সাথে যোগাযোগ করুন।\n\n"
        "⚠️ **Warning / সতর্কতা:**\n"
        "Please do not disturb without any valid reason. Spamming will result in a ban.\n"
        "বিনা কারণে ডিসটার্ব করবেন না। স্প্যামিং করলে ব্যান করা হবে।\n\n"
        "👇 **Contact Options / যোগাযোগের মাধ্যম:**"
    )
    await message.answer(text, reply_markup=get_help_keyboard(), parse_mode="Markdown")

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
    await message.answer("🎉 **Premium Activated! / প্রিমিয়াম চালু হয়েছে!**\n\nThank you for your purchase.", parse_mode="Markdown")

# ================= API ENDPOINTS =================
async def get_user(request):
    user_id = request.query.get("userId")
    user = db.reference(f'users/{user_id}').get()
    if user:
        if user.get('banned', False):
            return web.json_response({"error": "banned", "message": "Account is banned"})
        return web.json_response({
            "balance": max(0, user.get('balance', 0.0)),
            "is_premium": user.get('is_premium', False)
        })
    return web.json_response({"balance": 0, "is_premium": False})

async def add_reward(request):
    data = await request.json()
    uid = str(data.get("userId"))
    amt = float(data.get("amount", 0))
    ref = db.reference(f'users/{uid}')
    if ref.get():
        ref.child('balance').transaction(lambda current: max(0, (current or 0)) + amt)
    return web.json_response({"status": "success"})

async def create_invoice(request):
    data = await request.json()
    uid = data.get("userId")
    invoice_link = await bot.create_invoice_link(
        title="Premium Subscription", description="Unlock unlimited ads.",
        payload=f"premium_{uid}", provider_token="", currency="XTR",
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
    
    if user and max(0, user.get('balance', 0)) >= amount:
        ref.child('balance').transaction(lambda current: max(0, (current or 0) - amount))
        ref.child('hold_balance').transaction(lambda current: (current or 0) + amount)
        
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
        user_ref.child('hold_balance').transaction(lambda current: max(0, (current or 0) - amount))
    else:
        wd_ref.update({'status': 'rejected'})
        user_ref.child('hold_balance').transaction(lambda current: max(0, (current or 0) - amount))
        user_ref.child('balance').transaction(lambda current: max(0, (current or 0)) + amount)
    return web.json_response({"status": "success"})

async def admin_update_balance(request):
    data = await request.json()
    uid, amount, action = str(data.get("userId")), float(data.get("amount")), data.get("action") 
    ref = db.reference(f'users/{uid}')
    if ref.get():
        if action == 'add': 
            ref.child('balance').transaction(lambda current: max(0, (current or 0)) + amount)
        else: 
            ref.child('balance').transaction(lambda current: max(0, (current or 0) - amount))
        return web.json_response({"status": "success"})
    return web.json_response({"status": "error", "message": "User not found"})

async def admin_ban_user(request):
    data = await request.json()
    uid = str(data.get("userId"))
    action = data.get("action")
    ref = db.reference(f'users/{uid}')
    if ref.get():
        ref.update({'banned': (action == 'ban')})
        return web.json_response({"status": "success"})
    return web.json_response({"status": "error", "message": "User not found"})

async def admin_delete_user(request):
    data = await request.json()
    uid = str(data.get("userId"))
    try:
        db.reference(f'users/{uid}').delete()
        wds = db.reference('withdrawals').order_by_child('userId').equal_to(uid).get() or {}
        for wd_id in wds.keys():
            db.reference(f'withdrawals/{wd_id}').delete()
        return web.json_response({"status": "success"})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)})

async def admin_broadcast(request):
    data = await request.json()
    users = db.reference('users').get() or {}
    success = 0
    for uid, u_data in users.items():
        if u_data.get('banned', False): continue
        try:
            await bot.send_message(chat_id=uid, text=data.get("text"), parse_mode="Markdown")
            success += 1
            await asyncio.sleep(0.05)
        except: pass
    return web.json_response({"status": "success", "sent": success})

async def admin_send_message(request):
    data = await request.json()
    uid = str(data.get("userId"))
    text = data.get("text")
    if not uid or not text: return web.json_response({"status": "error", "message": "Missing data"})
    try:
        await bot.send_message(chat_id=uid, text=text, parse_mode="Markdown")
        return web.json_response({"status": "success"})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)})

# ================= POSTBACK (CPAGrip/Monetag) =================
async def cpa_postback(request):
    uid = request.query.get("user_id")
    amount_str = request.query.get("amount")
    secret = request.query.get("secret")
    
    if secret != POSTBACK_SECRET: return web.Response(text="❌ Error: Invalid Secret Key!", status=403)
    if not uid or not amount_str: return web.Response(text="❌ Error: Missing user_id or amount!", status=400)
        
    try:
        amount = float(amount_str)
        ref = db.reference(f'users/{uid}')
        user_data = ref.get()
        
        if user_data and not user_data.get('banned', False):
            ref.child('balance').transaction(lambda current: max(0, (current or 0)) + amount)
            return web.Response(text="OK", status=200)
        else:
            return web.Response(text=f"❌ Error: User not found or banned.", status=404)
    except Exception as e:
        return web.Response(text=f"❌ Firebase Error: {str(e)}", status=500)

async def ping(request): return web.Response(text="SM TaskNova Bot is running!")

# ================= CORS MIDDLEWARE =================
@web.middleware
async def cors_middleware(request, handler):
    if request.method == "OPTIONS":
        response = web.Response()
    else:
        response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# ================= WEBHOOK SETUP =================
async def on_startup(app):
    webhook_url = f"{RENDER_URL}/webhook"
    await bot.set_webhook(webhook_url, drop_pending_updates=True)
    print(f"✅ Webhook set to {webhook_url}")

async def on_shutdown(app):
    await bot.delete_webhook()
    print("❌ Webhook deleted")

async def handle_webhook(request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return web.Response(text="OK")

# ================= APP START =================
async def start_web():
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_post('/webhook', handle_webhook)
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
    app.router.add_post('/api/admin/ban-user', admin_ban_user)
    app.router.add_post('/api/admin/delete-user', admin_delete_user)
    app.router.add_post('/api/admin/broadcast', admin_broadcast)
    app.router.add_post('/api/admin/send-message', admin_send_message)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"✅ Web Server started on port {PORT}")

async def main():
    await start_web()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
