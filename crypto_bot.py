import requests
import telebot
from apscheduler.schedulers.background import BackgroundScheduler

# STEP 1: Set up bot
BOT_TOKEN = '7607230985:AAFvcypQYDs3F090U-oEYJq-W89M6V6t3Ro'  # Replace with your actual token from BotFather
bot = telebot.TeleBot(BOT_TOKEN)

# STEP 2: Alert storage
alerts = {}  # {chat_id: {"coin": "bitcoin", "target": 30000}}

# STEP 3: Start command
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,
        "👋 Welcome to Crypto Alert Bot!\n"
        "Use /price BTC to get price\n"
        "Use /alert BTC 30000 to get notified when it hits $30,000")

# STEP 4: Get current price
@bot.message_handler(commands=['price'])
def get_price(message):
    try:
        coin = message.text.split()[1].lower()
        url = f'https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd'
        data = requests.get(url).json()
        price = data[coin]['usd']
        bot.send_message(message.chat.id, f"💰 {coin.upper()} Price: ${price}")
    except:
        bot.send_message(message.chat.id, "❌ Usage: /price BTC")

# STEP 5: Set alert
@bot.message_handler(commands=['alert'])
def set_alert(message):
    try:
        parts = message.text.split()
        coin = parts[1].lower()
        target = float(parts[2])
        alerts[message.chat.id] = {"coin": coin, "target": target}
        bot.send_message(message.chat.id, f"🔔 Alert set for {coin.upper()} at ${target}")
    except:
        bot.send_message(message.chat.id, "⚠ Usage: /alert BTC 30000")

# STEP 6: Check alerts every minute
def check_alerts():
    for chat_id, alert in list(alerts.items()):
        url = f'https://api.coingecko.com/api/v3/simple/price?ids={alert["coin"]}&vs_currencies=usd'
        price = requests.get(url).json()[alert["coin"]]['usd']
        if price >= alert["target"]:
            bot.send_message(chat_id, f"🚨 {alert['coin'].upper()} has reached ${price}!")
            del alerts[chat_id]

scheduler = BackgroundScheduler()
scheduler.add_job(check_alerts, 'interval', seconds=60)
scheduler.start()  # ✅ FIXED: You had a broken line here!

# STEP 7: Keep bot running
bot.polling()
