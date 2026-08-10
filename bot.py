import time
from datetime import datetime
import requests

# Aapki di gayi details
TOKEN = "8689746853:AAHgj8KPZ6jUcejQ7vKmv_jcAjhwUMAz-3Q"
CHAT_ID = "@TradingMasterforex5099"

def send_telegram_signal(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Signal successfully sent to channel!")
        else:
            print(f"Failed to send signal: {response.text}")
    except Exception as e:
        print(f"Error connecting to Telegram: {e}")

def analyze_and_send_signal():
    # 5 minute candle close hone par signal generate karne ka logic
    # Yahan aap apni broker ya data feed se candle ki values lenge
    candle_color = "GREEN"  # Ya "RED"
    is_strong_candle = True # True jab candle strong ho
    
    if is_strong_candle:
        direction = "UP" if candle_color == "GREEN" else "DOWN"
        
        signal_message = (
            f"📊 *VIP TRADING SIGNAL* 📊\n\n"
            f"⏰ Timeframe: *5 Minutes Candle*\n"
            f"🎯 Direction: *{direction}*\n"
            f"⏱️ Expiry: *2 Minutes*\n"
            f"🔄 Martingale: *1 Step MTG* (if loss)\n\n"
            f"⚠️ Trade at your own risk!"
        )
        
        send_telegram_signal(signal_message)

# Main Loop - Har 5 minute (300 seconds) baad chalega
if __name__ == "__main__":
    print("Bot is running and waiting for 5-minute intervals...")
    while True:
        analyze_and_send_signal()
        # 5 minute wait karega agle signal ke liye
        time.sleep(300)
