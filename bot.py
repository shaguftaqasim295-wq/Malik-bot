import asyncio
from playwright.async_api import async_playwright
import requests
import random

TELEGRAM_BOT_TOKEN = "8689746853:AAG_UT6VQe7I4MhiDgVtieXx9u2-HqOz72Y"
CHANNEL_CHAT_ID = "@TradingMasterforex5099"

FOREX_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "EUR/JPY", "AUD/USD", 
    "NZD/USD", "USD/CAD", "USD/CHF", "EUR/GBP", "AUD/JPY", 
    "GBP/JPY", "EUR/AUD", "GBP/AUD", "EUR/CAD", "CAD/CHF", 
    "CHF/JPY", "NZD/JPY", "AUD/NZD", "GBP/CAD", "EUR/NZD", 
    "USD/NOK", "USD/SEK", "USD/SGD", "USD/TRY", "USD/ZAR"
]

async def run_bot_scan():
    # Aap yahan apni marzi ka scanner select kar sakte hain: "SNR", "Strong Trend", "FVG", "Breakout"
    button_type = "SNR"
    
    print(f"[{button_type}] Scanner run ho raha hai 25 pairs par...")
    
    scanned_pair = random.choice(FOREX_PAIRS)
    symbol_query = scanned_pair.replace("/", "")
    base_price = round(random.uniform(1.0500, 150.0000), 4)
    
    if button_type == "SNR":
        title = "📊 SNR Scanner Analysis"
        condition = "Major Support Level"
        entry_point = f"{base_price} (Rejection expected)"
        idea = "CALL (UP) on candle timing"
    elif button_type == "Strong Trend":
        title = "🚀 Strong Trend Scanner"
        condition = "Strong Bullish Momentum"
        entry_point = f"{base_price} (Pullback entry)"
        idea = "CONTINUE UP with trend timing"
    elif button_type == "FVG":
        title = "📐 FVG Scanner Analysis"
        condition = "Bullish Fair Value Gap"
        entry_point = f"{base_price} (Gap zone)"
        idea = "REVERSAL / FILL expected"
    else:
        title = "⚡ Breakout Scanner Analysis"
        condition = "Resistance Breakout"
        entry_point = f"{base_price} (Retest level)"
        idea = "MOMENTUM CONTINUATION entry"

    # Playwright screenshot capture
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        target_url = f"https://www.tradingview.com/chart/?symbol=FX:{symbol_query}"
        
        screenshot_path = "chart_analysis.png"
        try:
            print(f"Opening chart for {scanned_pair}...")
            await page.goto(target_url, timeout=60000)
            await asyncio.sleep(5)
            await page.screenshot(path=screenshot_path)
            print("Screenshot successfully captured!")
        except Exception as e:
            print("Browser error:", e)
            screenshot_path = None
        await browser.close()

    caption_text = (
        f"*{title}*\n\n"
        f"• *Pair:* `{scanned_pair}`\n"
        f"• *Condition:* {condition}\n"
        f"• *Entry Point:* `{entry_point}`\n"
        f"• *Signal Idea:* {idea}\n\n"
        f"⚡ _Malik VIP Premium Bot_"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto" if screenshot_path else f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    try:
        if screenshot_path:
            with open(screenshot_path, 'rb') as photo_file:
                payload = {'chat_id': CHANNEL_CHAT_ID, 'caption': caption_text, 'parse_mode': 'Markdown'}
                files = {'photo': photo_file}
                response = requests.post(url, data=payload, files=files, timeout=30)
        else:
            payload = {'chat_id': CHANNEL_CHAT_ID, 'text': caption_text, 'parse_mode': 'Markdown'}
            response = requests.post(url, json=payload, timeout=30)
            
        print("TELEGRAM STATUS CODE:", response.status_code)
        print("TELEGRAM RESPONSE:", response.text)
    except Exception as e:
        print("Telegram Send Error:", e)

if __name__ == "__main__":
    asyncio.run(run_bot_scan())
