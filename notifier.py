import requests
import os

def invia_notifica(testo):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = "https://" + "api." + "telegram.org/" + "bot" + str(token) + "/sendMessage"
    payload = {'chat_id': str(chat_id), 'text': testo, 'parse_mode': 'Markdown'}
    try: requests.post(url, data=payload, timeout=15)
    except: pass
