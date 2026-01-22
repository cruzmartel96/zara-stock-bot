import requests
import time
import os
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# Zara SKUs for Spain
SKUS = {
    "M": 464886562,
    "L": 464886563,
    "XL": 464886564
}

AVAILABILITY_URL = "https://www.zara.com/es/es/products/availability"

previously_in_stock = False
last_heartbeat_date = None


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })


# Startup confirmation
send_telegram_message(
    "🤖 Zara bot started.\nMonitoring sizes: M, L, XL (Spain 🇪🇸)"
)


def check_stock():
    global previously_in_stock

    payload = {
        "skus": list(SKUS.values())
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.post(AVAILABILITY_URL, json=payload, headers=headers)
    data = response.json()

    available_sizes = []

    for item in data.get("skusAvailability", []):
        if item["availability"] == "in_stock":
            for size, sku in SKUS.items():
                if sku == item["sku"]:
                    available_sizes.append(size)

    # Notify only once per restock
    if available_sizes and not previously_in_stock:
        send_telegram_message(
            f"🟢 Zara alert 🇪🇸\n\nVestido disponible en tallas: {', '.join(available_sizes)}"
        )
        previously_in_stock = True

    # Reset when all are out of stock again
    if not available_sizes:
        previously_in_stock = False


def daily_heartbeat():
    global last_heartbeat_date

    today = datetime.now().date()

    if last_heartbeat_date != today:
        send_telegram_message(
            "🟡 Zara bot running\nAll monitored sizes (M, L, XL) are currently out of stock 🇪🇸"
        )
        last_heartbeat_date = today


while True:
    try:
        check_stock()
        daily_heartbeat()
    except Exception as e:
        print("Error:", e)

    time.sleep(120)  # check every 2 minutes

