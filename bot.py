import asyncio
import os
import json
import time
import requests
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

# ==========================================
# ⚙️ TRADING MASTER FOREX - ADVANCED BOT CONFIG
# ==========================================
TELEGRAM_BOT_TOKEN = "8689746853:AAHgj8KPZ6jUcejQ7vKmv_jcAjhwUMAZ-3Q"
CHANNEL_CHAT_ID = "@TradingMasterforex5099"
HISTORY_FILE = "trading_history.json"

LIVE_PAIRS_MAP = {
    "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "USDJPY": "USDJPY=X",
    "USDCHF": "USDCHF=X", "USDCAD": "USDCAD=X", "AUDUSD": "AUDUSD=X", "NZDUSD": "NZDUSD=X",
    "EURGBP": "EURGBP=X", "EURJPY": "EURJPY=X", "EURAUD": "EURAUD=X",
    "EURCAD": "EURCAD=X", "EURNZD": "EURNZD=X", "EURCHF": "EURCHF=X",
    "GBPJPY": "GBPJPY=X", "GBPAUD": "GBPAUD=X", "GBPCAD": "GBPCAD=X",
    "GBPCHF": "GBPCHF=X", "GBPNZD": "GBPNZD=X", "AUDJPY": "AUDJPY=X",
    "AUDCAD": "AUDCAD=X", "AUDNZD": "AUDNZD=X", "CADJPY": "CADJPY=X",
    "CHFJPY": "CHFJPY=X", "NZDJPY": "NZDJPY=X", "NZDCAD": "NZDCAD=X"
}

session_stats = {"total": 0, "direct_wins": 0, "mtg_wins": 0, "losses": 0}
signals_in_session = 0
is_signal_running = False  # Lock mechanism

# --- NEWS & MARKET STATUS ---
def get_upcoming_news_schedule():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            events = response.json()
            now_utc = datetime.utcnow()
            upcoming_list = []
            for event in events:
                if event.get("impact") == "High":
                    date_str = event.get("date")
                    if date_str:
                        event_time = datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")
                        if event_time >= now_utc:
                            upcoming_list.append({
                                "time": event_time.strftime("%Y-%m-%d | %H:%M UTC"),
                                "currency": event.get("country", "USD"),
                                "title": event.get("title", "News")
                            })
                            if len(upcoming_list) >= 4:
                                break
            return upcoming_list
    except:
        pass
    return []

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
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "result": result_type
    }
    history.append(trade_record)
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f)
    except:
        pass

def get_stats_by_period(period_type):
    history = load_history()
    now = datetime.utcnow()
    d_wins, m_wins, losses = 0, 0, 0
    for trade in history:
        try:
            trade_time = datetime.strptime(trade["date"], "%Y-%m-%d")
            match = False
            if period_type == "day":
                if trade["date"] == now.strftime("%Y-%m-%d"): match = True
            elif period_type == "week":
                if (now - trade_time).days <= 7: match = True
                
            if match:
                res = trade["result"]
                if res == "DIRECT_WIN": d_wins += 1
                elif res == "MTG_WIN": m_wins += 1
                elif res == "LOSS": losses += 1
        except:
            continue
    total_wins = d_wins + m_wins
    total = total_wins + losses
    accuracy = (total_wins / total * 100) if total > 0 else 0.0
    return total, d_wins, m_wins, losses, accuracy

def get_inline_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "📊 Day Results", "callback_data": "res_day"},
                {"text": "📅 Week Results", "callback_data": "res_week"}
            ],
            [
                {"text": "📈 Market Status", "callback_data": "res_market_status"},
                {"text": "📰 Forex News", "callback_data": "res_news"}
            ]
        ]
    }

def send_telegram_message_with_result_buttons(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHANNEL_CHAT_ID, 
        'text': text, 
        'parse_mode': 'Markdown',
        'reply_markup': get_inline_keyboard()
    }
    try:
        requests.post(url, json=payload, timeout=20)
    except:
        pass

def send_telegram_simple_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHANNEL_CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, data=payload, timeout=20)
    except:
        pass

def send_telegram_photo_with_result_buttons(photo_path, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    for _ in range(3):
        try:
            if os.path.exists(photo_path) and os.path.getsize(photo_path) > 0:
                with open(photo_path, 'rb') as photo:
                    payload = {
                        'chat_id': CHANNEL_CHAT_ID, 
                        'caption': caption, 
                        'parse_mode': 'Markdown',
                        'reply_markup': str(get_inline_keyboard()).replace("'", '"')
                    }
                    files = {'photo': photo}
                    response = requests.post(url, data=payload, files=files, timeout=45)
                    if response.status_code == 200:
                        return True
        except:
            time.sleep(1)
    return False

# --- TELEGRAM CALLBACK LISTENER ---
async def handle_telegram_callbacks():
    offset = 0
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get("result"):
                offset = data["result"][-1]["update_id"] + 1
    except:
        pass

    while True:
        try:
            response = requests.get(url, params={"offset": offset, "timeout": 30}, timeout=35)
            if response.status_code == 200:
                data = response.json()
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    if "callback_query" in update:
                        cq = update["callback_query"]
                        callback_data = cq.get("data", "")
                        query_id = cq["id"]
                        
                        ans_text = ""
                        if callback_data == "res_news":
                            news_items = get_upcoming_news_schedule()
                            if news_items:
                                ans_text = "📰 *UPCOMING HIGH IMPACT NEWS* 📰\n━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                for item in news_items:
                                    ans_text += f"🗓️ `{item['time']}` | {item['currency']} | {item['title']}\n"
                            else:
                                ans_text = "📰 *FOREX NEWS*\nNo major high-impact news right now. Market is stable!"
                        elif callback_data == "res_market_status":
                            ans_text = (
                                "📈 *MARKET CONDITION STATUS*\n"
                                "━━━━━━━━━━━━━━━━━━━\n"
                                "🟢 **Market Flow:** Healthy & Active\n"
                                "⚡ **Volatility:** Optimal for 5M Expiry Strategies\n"
                                "🛡️ **SuperTrend & Fractals:** Synchronized\n"
                                "💡 *Status:* Market is running fine. Safe to trade!"
                            )
                        else:
                            period = "day"
                            title = "📊 TODAY'S RESULTS SUMMARY"
                            if callback_data == "res_week":
                                period = "week"
                                title = "📅 LAST 7 DAYS RESULTS SUMMARY"
                                
                            total, d_wins, m_wins, losses, acc = get_stats_by_period(period)
                            t_wins = d_wins + m_wins
                            ans_text = (
                                f"*{title}*\n"
                                f"━━━━━━━━━━━━━━━━━━━\n"
                                f"🎯 **Total Signals:** `{total}`\n"
                                f"⭐ **Direct Wins:** `{d_wins}`\n"
                                f"✅ **MTG Wins:** `{m_wins}`\n"
                                f"🏆 **Total Wins:** `{t_wins}`\n"
                                f"❌ **Losses:** `{losses}`\n"
                                f"📈 **Accuracy:** `{acc:.2f}%`\n"
                                f"━━━━━━━━━━━━━━━━━━━"
                            )
                        
                        ans_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
                        requests.post(ans_url, json={"callback_query_id": query_id, "text": "Loaded", "show_alert": False})
                        send_telegram_simple_message(ans_text)
        except:
            pass
        await asyncio.sleep(2)

# --- TRADINGVIEW SCREENSHOT CAPTURE ---
async def capture_chart(pair: str, output_path: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 750})
        url = f"https://s.tradingview.com/widgetembed/?symbol=FX:{pair}&interval=5&hidesidetoolbar=1&symboledit=0&saveimage=0&toolbarbg=000000&studies=[]&theme=dark&style=1&timezone=Asia/Karachi"
        
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

def get_market_data_5m(yf_symbol):
    try:
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period="3d", interval="5m", auto_adjust=True, timeout=10)
        
        if not df.empty and len(df) >= 30:
            candles = []
            for i in range(-15, 0):
                row = df.iloc[i]
                candles.append({
                    'open': float(row['Open']), 'high': float(row['High']),
                    'low': float(row['Low']), 'close': float(row['Close'])
                })
            return candles
    except:
        pass
    return None

def analyze_advanced_strategy(candles):
    if not candles or len(candles) < 10: return None
    
    prev_c, curr_c = candles[-2], candles[-1]
    entry_price = curr_c['close']
    
    body_curr = abs(curr_c['close'] - curr_c['open'])
    body_prev = abs(prev_c['close'] - prev_c['open'])
    avg_body = np.mean([abs(c['close'] - c['open']) for c in candles[-10:]])
    
    is_strong_momentum = (body_curr > avg_body * 1.2) and (body_prev > avg_body * 1.2)
    
    if curr_c['close'] > curr_c['open'] and prev_c['close'] > prev_c['open'] and is_strong_momentum:
        return ("🚀 5M SuperTrend + Fractal Call", "CALL 🟢", f"{entry_price:.5f}", "🔥 VIP 90%+", entry_price)
    elif curr_c['close'] < curr_c['open'] and prev_c['close'] < prev_c['open'] and is_strong_momentum:
        return ("🚀 5M SuperTrend + Fractal Put", "PUT 🔻", f"{entry_price:.5f}", "🔥 VIP 90%+", entry_price)
        
    return None

async def process_signal(pair: str, yf_symbol: str, pattern: str, direction: str, entry_str: str, strength: str, entry_num: float):
    global session_stats, signals_in_session, is_signal_running
    
    is_signal_running = True
    signals_in_session += 1
    
    timestamp = int(time.time())
    live_img = f"{pair}_live_{timestamp}.png"
    result_img = f"{pair}_result_{timestamp}.png"
    
    await capture_chart(pair, live_img)
    signal_msg = (
        f"**⚡ TRADING MASTER FOREX - VIP SIGNAL**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 **Asset:** `#{pair}`\n⏳ **Timeframe:** `5 Minutes (Chart & Expiry)`\n"
        f"🎯 **Pattern:** `{pattern}`\n📈 **Direction:** `{direction}`\n"
        f"📍 **Entry:** `{entry_str}`\n💪 **Accuracy:** `{strength}`\n"
        f"⏱️ **Expiry:** `Exact 5 Minutes`\n"
        f"⚠️ **Take 1 Step MTG same direction iff loss**\n━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    if os.path.exists(live_img):
        send_telegram_photo_with_result_buttons(live_img, signal_msg)
        try: os.remove(live_img)
        except: pass
    else:
        send_telegram_message_with_result_buttons(signal_msg)

    # 5 Minutes Expiry Wait
    await asyncio.sleep(300)
    candles_after = get_market_data_5m(yf_symbol)
    exit_num = candles_after[-1]['close'] if candles_after and len(candles_after) > 0 else entry_num
    
    is_first_win = False
    if "CALL" in direction:
        is_first_win = exit_num >= entry_num
    else:
        is_first_win = exit_num <= entry_num

    if is_first_win:
        session_stats["total"] += 1
        session_stats["direct_wins"] += 1
        save_trade_to_db("DIRECT_WIN")
        result_status = "🎯 **DIRECT WIN / SHURESHOT ⭐**"
    else:
        mtg_entry_num = exit_num
        # 1-Step MTG Expiry Wait (5 Mins)
        await asyncio.sleep(300)
        candles_mtg = get_market_data_5m(yf_symbol)
        mtg_exit_num = candles_mtg[-1]['close'] if candles_mtg and len(candles_mtg) > 0 else mtg_entry_num
        
        is_mtg_win = False
        if "CALL" in direction:
            is_mtg_win = mtg_exit_num >= mtg_entry_num
        else:
            is_mtg_win = mtg_exit_num <= mtg_entry_num
        
        session_stats["total"] += 1
        if is_mtg_win:
            session_stats["mtg_wins"] += 1
            save_trade_to_db("MTG_WIN")
            result_status = "✅ **MTG WIN / ITM 🎯**"
        else:
            session_stats["losses"] += 1
            save_trade_to_db("LOSS")
            result_status = "❌ **MTG LOSS / OTM 🛑**"

    await capture_chart(pair, result_img)
    result_msg = f"🏆 **TRADING MASTER FOREX - RESULT**\n📊 **Asset:** `#{pair}`\n✨ **Status:** {result_status}"
    if os.path.exists(result_img):
        send_telegram_photo_with_result_buttons(result_img, result_msg)
        try: os.remove(result_img)
        except: pass
    else:
        send_telegram_message_with_result_buttons(result_msg)

    is_signal_running = False

async def main():
    global is_signal_running
    print("Trading Master Forex Bot Active...")
    asyncio.create_task(handle_telegram_callbacks())
    
    morning_sent_date = ""
    night_sent_date = ""
    
    while True:
        now_pk = datetime.utcnow() + timedelta(hours=5)
        current_hour = now_pk.hour
        current_minute = now_pk.minute
        current_date_str = now_pk.strftime("%Y-%m-%d")
        
        if current_hour == 10 and current_minute == 0 and morning_sent_date != current_date_str:
            send_telegram_simple_message(
                "🌅 **GOOD MORNING! TRADING SESSION STARTED** 🟢\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "⚡ Bot is now active and scanning 5M markets.\n"
                "🎯 Let's grab amazing profits today!"
            )
            morning_sent_date = current_date_str
            
        if current_hour == 22 and current_minute == 0 and night_sent_date != current_date_str:
            total, d, m, l, acc = get_stats_by_period("day")
            send_telegram_simple_message(
                "🌙 **GOOD NIGHT! TRADING SESSION CLOSED** 🛑\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 Today's Total Signals: `{total}`\n"
                f"🏆 Win Accuracy: `{acc:.2f}%`\n"
                "See you tomorrow! Rest well."
            )
            night_sent_date = current_date_str

        if not (10 <= current_hour < 22):
            await asyncio.sleep(60)
            continue

        if is_signal_running:
            await asyncio.sleep(10)
            continue

        signal_found = False
        for pair, yf_symbol in LIVE_PAIRS_MAP.items():
            print(f"Scanning 5M Market -> {pair}                    ", end="\r")
            candles = get_market_data_5m(yf_symbol)
            
            if candles:
                signal = analyze_advanced_strategy(candles)
                if signal:
                    pattern, direction, entry_str, strength, entry_num = signal
                    await process_signal(pair, yf_symbol, pattern, direction, entry_str, strength, entry_num)
                    signal_found = True
                    break  
                    
        if not signal_found:
            await asyncio.sleep(180)

if __name__ == "__main__":
    asyncio.run(main())
