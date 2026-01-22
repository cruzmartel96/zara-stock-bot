import os
import time
import requests

# =====================
# CONFIG
# =====================

AVAILABILITY_URL = "https://www.zara.com/es/es/products/availability"

MAX_RETRIES = 3
INITIAL_BACKOFF = 2  # seconds
TIMEOUT = 10

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.zara.com/",
    "Origin": "https://www.zara.com",
}


# =====================
# TELEGRAM
# =====================

def send_telegram_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram credentials missing")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")


# =====================
# STOCK CHECK
# =====================

def check_stock():
    backoff = INITIAL_BACKOFF

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                AVAILABILITY_URL,
                headers=HEADERS,

    save_state(state)


if __name__ == "__main__":
    check_stock()
