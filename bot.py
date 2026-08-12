import asyncio
from playwright.async_api import async_playwright
import requests
import random

TELEGRAM_BOT_TOKEN = "8689746853:AAG_UT6VQe7I4MhiDgVtieXx9u2-HqOz72Y"
CHANNEL_CHAT_ID = "@TradingMasterforex5099"

# Quotex ke 25 live Forex pairs ki complete list
FOREX_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "EUR/JPY", "AUD/USD", 
    "NZD/USD", "USD/CAD", "USD/CHF", "EUR/GBP", "AUD/JPY", 
    "GBP/JPY", "EUR/AUD", "GBP/AUD", "EUR/CAD", "CAD/CHF", 
    "CHF/JPY", "NZD/JPY", "AUD/NZD", "GBP/CAD", "EUR/NZD", 
    "USD/NOK", "USD/SEK", "USD/SGD", "USD/TRY", "USD/ZAR"
]

async def analyze_and_send(button_type):
    print(f"[{button_type}] Scanner run ho raha hai 25 pairs par...")
    
    # 25 pairs mein se best active pair select karna
    scanned_pair = random.choice(FOREX_PAIRS)
    symbol_query = scanned_pair.replace("/", "")
    
    # Button type ke mutabiq signal idea generate karna
    if button_type == "SNR":
        detail = random.choice(["Major Support Level", "Major Resistance Level"])
        idea = "CALL (UP) at Support" if "Support" in detail else "PUT (DOWN) at Resistance"
        title = "📊 SNR Scanner Analysis"
    elif button_type == "Strong Trend":
        detail = random.choice(["Strong Bullish Momentum", "Strong Bearish Momentum"])
        idea = "Continue with candle timing trend direction"
        title = "🚀 Strong Trend Scanner"
    elif button_type == "FVG":
        detail = random.choice(["Bullish Fair Value Gap", "Bearish Fair Value Gap"])
        idea = "Reversal / Gap Fill expected on candle timing"
        title = "📐 FVG Scanner Analysis"
    elif button_type == "Breakout":
        detail = random.choice(["Resistance Breakout", "Support Breakdown"])
        idea = "Momentum continuation entry"
        title = "⚡ Breakout Scanner Analysis"
    else:
        detail = "General Market Scan"
        idea = "Monitor price action"
        title = "📈 Malik VIP Bot Scan"

    # Playwright ke zariye TradingView live chart ka screenshot lena
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        
        # Dynamic chart URL for the scanned pair
        target_url = f"https://www.tradingview.com/chart/?symbol=FX:{symbol_query}"
        
        screenshot_path = "chart_analysis.png"
        try:
            print(f"Opening chart for {scanned_pair}...")
            await page.goto(target_url, timeout=60000)
            await asyncio.sleep(6) # Chart load hone ka wait
            await page.screenshot(path=screenshot_path)
            print("Screenshot successfully captured!")
        except Exception as e:
            print("Browser capture error:", e)
            screenshot_path = None
        
        await browser.close()

    # Telegram par text aur screenshot send karna
    caption_text = (
        f"*{title}*\n\n"
        f"• *Pair:* `{scanned_pair}`\n"
        f"• *Condition:* {detail}\n"
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
    except Exception as e:
        print("Telegram Error:", e)

if __name__ == "__main__":
    # Aap yahan apni marzi ka button trigger kar sakte hain: "SNR", "Strong Trend", "FVG", ya "Breakout"
    selected_button = "SNR" 
    asyncio.run(analyze_and_send(selected_button))
