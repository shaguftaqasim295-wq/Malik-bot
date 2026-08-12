import requests

TELEGRAM_BOT_TOKEN = "8689746853:AAHgj8KPZ6jUcejQ7vKmv_jcAjhwUMAZ-3Q"
# Yahan hum channel username ke sath direct test message bhej rahe hain
CHANNEL_CHAT_ID = "@TradingMasterforex5099"

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
payload = {
    'chat_id': CHANNEL_CHAT_ID,
    'text': "🟢 *System is running perfectly!* \n\nZero se shuru kar diya hai, ab bataen agla step kya karna hai?",
    'parse_mode': 'Markdown'
}

response = requests.post(url, json=payload)
print("Response:", response.text)
