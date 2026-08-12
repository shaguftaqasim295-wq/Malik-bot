import requests

TELEGRAM_BOT_TOKEN = "8689746853:AAHgj8KPZ6jUcejQ7vKmv_jcAjhwUMAz-3Q"
CHANNEL_CHAT_ID = "-1006927353586"

def send_test_message():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHANNEL_CHAT_ID,
        'text': "🟢 *System is running...*\n\nBot successfully connect ho gaya hai!",
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        print("Response:", response.text)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    send_test_message()
