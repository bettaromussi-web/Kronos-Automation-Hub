import requests
import os

def send_telegram_msg(message):
    token = os.getenv('8640695510:AAGohMq0xkYrLayTv33MvzYtVFPDU1DLqKI')
    chat_id = os.getenv('696552391')
    url = f"https://telegram.org{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=payload)
