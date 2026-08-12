import requests

TELEGRAM_BOT_TOKEN = "8689746853:AAG_UT6VQe7I4MhiDgVtieXx9u2-HqOz72Y"
CHANNEL_CHAT_ID = "-1006927353586"

def send_test_message():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHANNEL_CHAT_ID,
        'text': "🟢 *System is running successfully!* \n\nNaya token aur Chat ID configure ho chuki hai."
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        print("TELEGRAM STATUS CODE:", response.status_code)
        print("TELEGRAM RESPONSE:", response.text)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    send_test_message()
