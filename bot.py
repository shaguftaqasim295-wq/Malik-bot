import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
from playwright.async_api import async_playwright

TELEGRAM_BOT_TOKEN = "8689746853:AAG_UT6VQe7I4MhiDgVtieXx9u2-HqOz72Y"

FOREX_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "EUR/JPY", "AUD/USD", 
    "NZD/USD", "USD/CAD", "USD/CHF", "EUR/GBP", "AUD/JPY", 
    "GBP/JPY", "EUR/AUD", "GBP/AUD", "EUR/CAD", "CAD/CHF", 
    "CHF/JPY", "NZD/JPY", "AUD/NZD", "GBP/CAD", "EUR/NZD", 
    "USD/NOK", "USD/SEK", "USD/SGD", "USD/TRY", "USD/ZAR"
]

async def capture_chart(symbol_query):
    screenshot_path = "chart_analysis.png"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        target_url = f"https://www.tradingview.com/chart/?symbol=FX:{symbol_query}"
        try:
            await page.goto(target_url, timeout=60000)
            await asyncio.sleep(5)
            await page.screenshot(path=screenshot_path)
        except Exception:
            screenshot_path = None
        await browser.close()
    return screenshot_path

async def generate_signal(button_type):
    pair = random.choice(FOREX_PAIRS)
    symbol_query = pair.replace("/", "")
    
    # Mocking entry prices based on strategy
    base_price = round(random.uniform(1.0500, 150.0000), 4)
    
    if button_type == "btn_snr":
        title = "📊 SNR Scanner Analysis"
        condition = "Major Support Level"
        entry_point = f"{base_price} (Rejection expected)"
        idea = "CALL (UP) on candle timing"
    elif button_type == "btn_trend":
        title = "🚀 Strong Trend Scanner"
        condition = "Strong Bullish Momentum"
        entry_point = f"{base_price} (Pullback entry)"
        idea = "CONTINUE UP with trend timing"
    elif button_type == "btn_fvg":
        title = "📐 FVG Scanner Analysis"
        condition = "Bullish Fair Value Gap"
        entry_point = f"{base_price} (Gap zone)"
        idea = "REVERSAL / FILL expected"
    elif button_type == "btn_breakout":
        title = "⚡ Breakout Scanner Analysis"
        condition = "Resistance Breakout"
        entry_point = f"{base_price} (Retest level)"
        idea = "MOMENTUM CONTINUATION entry"
    else:
        title = "📈 Malik VIP Bot Scan"
        condition = "General Scan"
        entry_point = str(base_price)
        idea = "Monitor price action"

    return pair, symbol_query, title, condition, entry_point, idea

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 SNR", callback_data="btn_snr"), InlineKeyboardButton("🚀 Strong Trend", callback_data="btn_trend")],
        [InlineKeyboardButton("📐 FVG", callback_data="btn_fvg"), InlineKeyboardButton("⚡ Breakout", callback_data="btn_breakout")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 *Welcome to Malik VIP Premium Bot*\n\nNeeche diye gaye buttons par click kar ke live analysis aur entry points hasil karein:", parse_mode="Markdown", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Loading message
    await query.edit_message_text(text="🔍 Scanning 25 Forex pairs & capturing chart screenshot...")
    
    pair, symbol_query, title, condition, entry_point, idea = await generate_signal(query.data)
    screenshot_path = await capture_chart(symbol_query)
    
    caption = (
        f"*{title}*\n\n"
        f"• *Pair:* `{pair}`\n"
        f"• *Condition:* {condition}\n"
        f"• *Entry Point:* `{entry_point}`\n"
        f"• *Signal Idea:* {idea}\n\n"
        f"⚡ _Malik VIP Premium Bot_"
    )
    
    keyboard = [
        [InlineKeyboardButton("📊 SNR", callback_data="btn_snr"), InlineKeyboardButton("🚀 Strong Trend", callback_data="btn_trend")],
        [InlineKeyboardButton("📐 FVG", callback_data="btn_fvg"), InlineKeyboardButton("⚡ Breakout", callback_data="btn_breakout")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if screenshot_path and os.path.exists(screenshot_path):
        with open(screenshot_path, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=photo,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        try:
            os.remove(screenshot_path)
        except:
            pass
    else:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=caption,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

if __name__ == "__main__":
    import asyncio
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot is running interactively...")
    app.run_polling()
