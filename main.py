import requests
import time
import os

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

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

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

    if available_sizes and not previously_in_stock:
        send_telegram_message(
            f"🟢 Zara alert 🇪🇸\n\nVestido disponible en tallas: {', '.join(available_sizes)}"
        )
        previously_in_stock = True

    if not available_sizes:
        previously_in_stock = False

while True:
    try:
        check_stock()
    except Exception as e:
        print("Error:", e)

    time.sleep(120)  # check every 2 minutes
