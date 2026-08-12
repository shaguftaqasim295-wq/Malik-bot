import requests

TELEGRAM_BOT_TOKEN = "8689746853:AAHgj8KPZ6jUcejQ7vKmv_jcAjhwUMAZ-3Q"
CHANNEL_CHAT_ID = "-1006927353586"

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
payload = {
    'chat_id': CHANNEL_CHAT_ID,
    'text': "Test message from script"
}

response = requests.post(url, json=payload)
print("TELEGRAM STATUS CODE:", response.status_code)
print("TELEGRAM RESPONSE:", response.text)
