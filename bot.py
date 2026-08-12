import time
import requests

TELEGRAM_BOT_TOKEN = "8689746853:AAHgj8KPZ6jUcejQ7vKmv_jcAjhwUMAZ-3Q"
CHANNEL_CHAT_ID = "@TradingMasterforex5099"

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHANNEL_CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        print("Telegram Response:", response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Bot started successfully...")
    send_message("🟢 *System is running and connected!* \n\nBot successfully initialize ho gaya hai.")
