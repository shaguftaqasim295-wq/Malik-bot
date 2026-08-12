import requests

TELEGRAM_BOT_TOKEN = "8689746853:AAHgj8KPZ6jUcejQ7vKmv_jcAjhwUMAZ-3Q"
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"

try:
    response = requests.get(url)
    print("Updates Response:", response.text)
except Exception as e:
    print("Error:", e)
