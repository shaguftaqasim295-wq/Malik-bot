import time
from datetime import datetime, timezone, timedelta
import requests

TOKEN = "8689746853:AAHgj8KPZ6jUcejQ7vKmv_jcAjhwUMAZ-3Q"
CHAT_ID = "@TradingMasterforex5099"

# Quotex par available 30+ Forex Pairs & Assets
QUOTEX_ASSETS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "NZD/USD", "USD/CHF",
    "EUR/GBP", "EUR/JPY", "EUR/AUD", "EUR/CAD", "EUR/NZD", "GBP/JPY", "GBP/AUD",
    "GBP/CAD", "AUD/JPY", "AUD/CAD", "CAD/JPY", "CHF/JPY", "NZD/JPY",
    "EUR/CHF", "GBP/CHF", "AUD/NZD", "CAD/CHF", "NZD/CAD", "USD/NOK", "USD/SEK",
    "USD/SGD", "USD/ZAR", "USD/TRY", "USD/BRL"
]

def get_market_session_pakistan():
    # Pakistan time (PKT = UTC+5)
    pkt_time = datetime.now(timezone(timedelta(hours=5)))
    hour = pkt_time.hour
    
    sessions = []
    # Session timings in PKT (Approximate standard market hours)
    if 2 <= hour < 11:
        sessions.append("Sydney 🟢")
    if 5 <= hour < 14:
        sessions.append("Tokyo 🟢")
    if 12 <= hour < 21:
        sessions.append("London 🟢")
    if hour >= 17 or hour < 2:
        sessions.append("New York 🟢")
        
    active_sessions = ", ".join(sessions) if sessions else "Market is slow / Weekend"
    return f"Pakistan Time: {pkt_time.strftime('%H:%M:%S')}\nActive Sessions: {active_sessions}"

def send_telegram_signal_with_buttons(message, pair):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    tv_symbol = pair.replace('/', '')
    tradingview_url = f"https://www.tradingview.com/chart/?symbol={tv_symbol}"
    
    # 4 Buttons Layout as requested
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "📊 View Chart", "url": tradingview_url},
                {"text": "📅 Today Result", "callback_data": "today_result"}
            ],
            [
                {"text": "📈 Weekly Result", "callback_data": "weekly_result"},
                {"text": "🌐 Market & Session", "callback_data": "market_status"}
            ]
        ]
    }
    
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": keyboard
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"Signal sent successfully for {pair}!")
        else:
            print(f"Failed to send signal: {response.text}")
    except Exception as e:
        print(f"Error connecting to Telegram: {e}")

def analyze_and_send_signal():
    # Yahan aap apni strategy ke mutabiq pair scan karwate hain
    for pair in QUOTEX_ASSETS:
        entry_price = 1.09250
        candle_color = "GREEN"
        is_strong_candle = True  # Strategy condition check
        
        if is_strong_candle:
            direction = "UP" if candle_color == "GREEN" else "DOWN"
            mtg_direction = direction 
            
            signal_message = (
                f"📊 *VIP TRADING SIGNAL* 📊\n\n"
                f"💱 Asset: *{pair}*\n"
                f"⏰ Timeframe: *5 Minutes Candle*\n"
                f"📍 Entry Point: *{entry_price}*\n"
                f"🎯 Direction: *{direction}*\n"
                f"⏱️ Expiry: *2 Minutes*\n"
                f"🔄 Martingale: *1 Step MTG* ➔ Direction: *{mtg_direction}*\n\n"
                f"⚠️ Trade at your own risk!"
            )
            
            send_telegram_signal_with_buttons(signal_message, pair)
            
            # Jab ek signal mil jaye aur send ho jaye, toh mazeed continuous spam roknay ke liye break kar dein
            return True 
    return False

if __name__ == "__main__":
    print("Bot is running with 30+ assets, full buttons, and Pakistan session tracking (5M interval locked)...")
    while True:
        # Har dafe scan karne ke baad exact 5 minutes (300 seconds) ka waqfa rakhega
        signal_triggered = analyze_and_send_signal()
        
        # Agar signal mil gaya hai tab bhi ya na mile tab bhi agla scan 5 minutes baad hi hoga
        time.sleep(300)
