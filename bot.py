import requests

# Aapka naya aur active Telegram Bot Token
TELEGRAM_BOT_TOKEN = "8689746853:AAG_UT6VQe7I4MhiDgVtieXx9u2-HqOz72Y"

# Aapke channel ka direct username (Isme koi minus sign ya ID nikalne ki zaroorat nahi hai)
CHANNEL_CHAT_ID = "@TradingMasterforex5099"

def send_telegram_message():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHANNEL_CHAT_ID,
        'text': "🟢 *Malik VIP Premium Bot* \n\nSystem successfully connected and running!"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print("TELEGRAM STATUS CODE:", response.status_code)
        print("TELEGRAM RESPONSE:", response.text)
        
        if response.status_code == 200:
            print("SUCCESS: Message successfully channel par bhej diya gaya hai!")
        else:
            print("ERROR: Telegram API ne error return kiya hai.")
            
    except Exception as e:
        print("Connection Error:", e)

if __name__ == "__main__":
    send_telegram_message()
