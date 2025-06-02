import requests
import telebot
from apscheduler.schedulers.background import BackgroundScheduler

# ✅ Replace with your real token
BOT_TOKEN = '7607230985:AAFvcypQYDs3F090U-oEYJq-W89M6V6t3Ro'
bot = telebot.TeleBot(BOT_TOKEN)

# ✅ Store multiple alerts per user and coin
alerts = {}  # Format: {chat_id: [{"coin": "bitcoin", "target": 30000}]}

# ✅ Command: /start
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,
        "👋 Welcome to Crypto Alert Bot!\n"
        "Use /price BTC to get current price.\n"
        "Use /alert BTC 30000 to get notified when BTC hits $30,000.\n"
        "Use /alert BTC BELOW 25000 to get alert if BTC falls below $25,000.")

# ✅ Command: /price BTC
@bot.message_handler(commands=['price'])
def get_price(message):
    try:
        coin = message.text.split()[1].lower()
        coin_id = get_coin_id(coin)
        url = f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd'
        data = requests.get(url).json()
        price = data[coin_id]['usd']
        bot.send_message(message.chat.id, f"💰 {coin.upper()} Price: ${price}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error! Use: /price BTC\nDetails: {e}")

# ✅ Command: /alert BTC 30000 or /alert BTC BELOW 25000
@bot.message_handler(commands=['alert'])
def set_alert(message):
    try:
        parts = message.text.split()
        coin = parts[1].lower()
        if parts[2].upper() == "BELOW":
            direction = "below"
            target = float(parts[3])
        else:
            direction = "above"
            target = float(parts[2])

        coin_id = get_coin_id(coin)

        alert = {"coin": coin_id, "target": target, "direction": direction}
        user_alerts = alerts.get(message.chat.id, [])
        user_alerts.append(alert)
        alerts[message.chat.id] = user_alerts

        bot.send_message(message.chat.id, f"🔔 Alert set for {coin.upper()} to go {direction.upper()} ${target}")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠ Usage: /alert BTC 30000 OR /alert BTC BELOW 25000\nError: {e}")

# ✅ Coin symbol to CoinGecko ID conversion (simplified)
def get_coin_id(symbol):
    symbol = symbol.lower()
    coins = {
        'btc': 'bitcoin',
        'eth': 'ethereum',
        'sol': 'solana',
        'xrp': 'ripple',
        'doge': 'dogecoin',
        'ada': 'cardano',
        'dot': 'polkadot'
    }
    return coins.get(symbol, symbol)

# ✅ Alert Checker (runs every minute)
def check_alerts():
    for chat_id, user_alerts in list(alerts.items()):
        updated_alerts = []
        for alert in user_alerts:
            try:
                url = f'https://api.coingecko.com/api/v3/simple/price?ids={alert["coin"]}&vs_currencies=usd'
                data = requests.get(url).json()
                price = data[alert["coin"]]['usd']
                direction = alert['direction']

                # Check condition
                if (direction == "above" and price >= alert['target']) or \
                   (direction == "below" and price <= alert['target']):
                    bot.send_message(chat_id,
                        f"🚨 {alert['coin'].capitalize()} price is now ${price}!\n(Target {direction} ${alert['target']})")
                else:
                    updated_alerts.append(alert)  # Keep this alert if not triggered
            except:
                continue
        alerts[chat_id] = updated_alerts  # Update only remaining alerts

# ✅ Run scheduler every 60 seconds
scheduler = BackgroundScheduler()
scheduler.add_job(check_alerts, 'interval', seconds=60)
scheduler.start()

# ✅ Keep the bot running
bot.polling(non_stop=True)
