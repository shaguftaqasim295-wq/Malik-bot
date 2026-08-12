import asyncio
import os
import json
import time
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

# ==========================================
# ⚙️ TRADING MASTER FOREX - REAL DATA BOT
# ==========================================
TELEGRAM_BOT_TOKEN = "8689746853:AAHgj8KPZ6jUcejQ7vKmv_jcAjhwUMAZ-3Q"
CHANNEL_CHAT_ID = "@TradingMasterforex5099"
HISTORY_FILE = "trading_history_real.json"

QUOTEX_ASSETS_MAP = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "USDJPY=X",
    "USD/CHF": "USDCHF=X", "USD/CAD": "USDCAD=X", "AUD/USD": "AUDUSD=X"
}

is_signal_running = False
last_signal_timestamp = 0

# --- DATABASE FUNCTIONS ---
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return []

def save_trade_to_db(result_type):
    history = load_history()
    trade_record = {
        "timestamp": time.time(),
        "datetime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "result": result_type
    }
    history.append(trade_record)
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f)
    except:
        pass

def get_inline_keyboard(pair="EURUSD"):
    tv_symbol = pair.replace('/', '')
    tradingview_url = f"https://www.tradingview.com/chart/?symbol={tv_symbol}"
    return {
        "inline_keyboard": [
            [
                {"text": "📊 View Chart", "url": tradingview_url},
                {"text": "🌐 Market Live", "url": "https://quotex.com"}
            ]
        ]
    }

def send_telegram_photo_with_buttons(photo_path, caption, pair):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    for _ in range(3):
        try:
            if os.path.exists(photo_path) and os.path.getsize(photo_path) > 0:
                with open(photo_path, 'rb') as photo:
                    payload = {
                        'chat_id': CHANNEL_CHAT_ID, 
                        'caption': caption, 
                        'parse_mode': 'Markdown',
                        'reply_markup': str(get_inline_keyboard(pair)).replace("'", '"')
                    }
                    files = {'photo': photo}
                    response = requests.post(url, data=payload, files=files, timeout=45)
                    if response.status_code == 200:
                        return True
        except:
            time.sleep(1)
    return False

def send_telegram_message(text, pair):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHANNEL_CHAT_ID, 
        'text': text, 
        'parse_mode': 'Markdown',
        'reply_markup': get_inline_keyboard(pair)
    }
    try:
        requests.post(url, json=payload, timeout=20)
    except:
        pass

# --- TRADINGVIEW SCREENSHOT CAPTURE ---
async def capture_chart(pair: str, output_path: str):
    tv_symbol = pair.replace('/', '')
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 750})
        url = f"https://s.tradingview.com/widgetembed/?symbol=FX:{tv_symbol}&interval=5&hidesidetoolbar=1&symboledit=0&saveimage=0&toolbarbg=000000&studies=[]&theme=dark&style=1&timezone=Asia/Karachi"
        
        for _ in range(3):
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(5)
                await page.screenshot(path=output_path, clip={"x": 0, "y": 0, "width": 1280, "height": 700})
                if os.path.exists(output_path) and os.path.getsize(output_path) > 15000:
                    break
            except:
                await asyncio.sleep(2)
        await browser.close()

# --- REAL MARKET DATA FETCHING ---
def get_real_market_data(yf_symbol):
    try:
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period="1d", interval="5m", auto_adjust=True)
        if df is not None and not df.empty and len(df) >= 2:
            prev_row = df.iloc[-2]
            curr_row = df.iloc[-1]
            return {
                'prev_open': float(prev_row['Open']),
                'prev_close': float(prev_row['Close']),
                'current_price': float(curr_row['Close'])
            }
    except Exception as e:
        print(f"Data error for {yf_symbol}: {e}")
    return None

# --- STRATEGY: REAL CANDLE COLOR CHECK ---
def analyze_real_strategy(data):
    if not data: return None
    
    # Strategy: Agar pichli 5m candle Green hai toh CALL, warna PUT
    is_green = data['prev_close'] > data['prev_open']
    is_red = data['prev_close'] < data['prev_open']
    
    entry_price = data['current_price']
    
    if is_green:
        return ("CALL 🟢", f"{entry_price:.5f}", entry_price)
    elif is_red:
        return ("PUT 🔻", f"{entry_price:.5f}", entry_price)
        
    return None

# --- PROCESS REAL SIGNAL ---
async def process_real_signal(pair: str, yf_symbol: str, direction: str, entry_str: str, entry_num: float):
    global is_signal_running, last_signal_timestamp
    
    is_signal_running = True
    last_signal_timestamp = time.time()
    
    timestamp = int(time.time())
    live_img = f"live_{timestamp}.png"
    result_img = f"result_{timestamp}.png"
    
    await capture_chart(pair, live_img)
    
    signal_msg = (
        f"📊 *VIP REAL TRADING SIGNAL* 📊\n\n"
        f"💱 Asset: *{pair}*\n"
        f"⏰ Timeframe: *5 Minutes Candle*\n"
        f"📍 Entry Point: *{entry_str}*\n"
        f"🎯 Direction: *{direction}*\n"
        f"⏱️ Expiry: *2 Minutes*\n"
        f"🔄 Martingale: *1 Step MTG (Same Direction)* ➔ *{direction}*\n\n"
        f"⚠️ Trade at your own risk!"
    )
    
    if os.path.exists(live_img):
        send_telegram_photo_with_buttons(live_img, signal_msg, pair)
        try: os.remove(live_img)
        except: pass
    else:
        send_telegram_message(signal_msg, pair)

    # 2 Minutes Expiry Wait (120 seconds)
    await asyncio.sleep(120)
    
    # Check Result using Real Data
    data_after = get_real_market_data(yf_symbol)
    exit_num = data_after['current_price'] if data_after else entry_num
    
    is_first_win = (exit_num >= entry_num) if "CALL" in direction else (exit_num <= entry_num)

    if is_first_win:
        save_trade_to_db("DIRECT_WIN")
        result_status = "🎯 *DIRECT WIN / SHURESHOT ⭐*"
    else:
        mtg_entry_num = exit_num
        # 1 Step Martingale (2 Minutes Expiry in Same Direction)
        await asyncio.sleep(120)
        data_mtg = get_real_market_data(yf_symbol)
        mtg_exit_num = data_mtg['current_price'] if data_mtg else mtg_entry_num
        
        is_mtg_win = (mtg_exit_num >= mtg_entry_num) if "CALL" in direction else (mtg_exit_num <= mtg_entry_num)
        
        if is_mtg_win:
            save_trade_to_db("MTG_WIN")
            result_status = "✅ *MTG WIN / ITM 🎯*"
        else:
            save_trade_to_db("LOSS")
            result_status = "❌ *MTG LOSS / OTM 🛑*"

    await capture_chart(pair, result_img)
    result_msg = f"🏆 *TRADING MASTER FOREX - RESULT*\n\n💱 Asset: *{pair}*\n✨ Status: {result_status}"
    
    if os.path.exists(result_img):
        send_telegram_photo_with_buttons(result_img, result_msg, pair)
        try: os.remove(result_img)
        except: pass
    else:
        send_telegram_message(result_msg, pair)

    is_signal_running = False

# --- MAIN LOOP ---
async def main():
    global is_signal_running, last_signal_timestamp
    print("Trading Master Real Data Bot Initialized...")
    
    while True:
        if is_signal_running:
            await asyncio.sleep(10)
            continue

        # 3 Minutes gap between consecutive signals to avoid spam
        if last_signal_timestamp > 0 and (time.time() - last_signal_timestamp < 180):
            await asyncio.sleep(10)
            continue

        signal_sent = False
        for pair, yf_symbol in QUOTEX_ASSETS_MAP.items():
            print(f"Scanning Real Market -> {pair}                  ", end="\r")
            data = get_real_market_data(yf_symbol)
            
            if data:
                signal = analyze_real_strategy(data)
                if signal:
                    direction, entry_str, entry_num = signal
                    await process_real_signal(pair, yf_symbol, direction, entry_str, entry_num)
                    signal_sent = True
                    break
                    
        if not signal_sent:
            await asyncio.sleep(15)

if __name__ == "__main__":
    asyncio.run(main())
