import os
import json
import requests
from datetime import datetime, timezone

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

PRODUCT_ID = 464887739
STORE_ID = 10703

AVAILABILITY_URL = "https://www.zara.com/es/es/products/availability"

TARGET_SKUS = {
    464886562: "M",
    464886563: "L",
    464886564: "XL"
}

STATE_FILE = "state.json"


def send_telegram(message):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": message},
        timeout=10
    )


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"notified": {}, "last_heartbeat": None}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def check_stock():
    state = load_state()

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Content-Type": "application/json",
        "Referer": "https://www.zara.com/es/es/",
        "Origin": "https://www.zara.com"
    }

    payload = {
        "products": [
            {
                "productId": PRODUCT_ID,
                "storeId": STORE_ID
            }
        ]
    }

    response = requests.post(
        AVAILABILITY_URL,
        headers=headers,
        json=payload,
        timeout=15
    )

    response.raise_for_status()
    data = response.json()

    availability = {
        item["sku"]: item["availability"]
        for item in data["products"][0]["skusAvailability"]
    }

    for sku, size in TARGET_SKUS.items():
        status = availability.get(sku)
        was_notified = state["notified"].get(str(sku), False)

        if status == "in_stock" and not was_notified:
            send_telegram(f"🛍️ Zara alert: size {size} is BACK IN STOCK!")
            state["notified"][str(sku)] = True

        if status != "in_stock":
            state["notified"][str(sku)] = False

    today = datetime.now(timezone.utc).date().isoformat()
    if state["last_heartbeat"] != today:
        send_telegram("💓 Zara bot is alive — still checking stock")
        state["last_heartbeat"] = today

    save_state(state)


if __name__ == "__main__":
    check_stock()

    save_state(state)


if __name__ == "__main__":
    check_stock()
