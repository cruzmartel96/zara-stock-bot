import requests
import json
import os
from datetime import datetime, timezone

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# Zara SKUs (Spain)
SKUS = {
    "M": 464886562,
    "L": 464886563,
    "XL": 464886564
}

AVAILABILITY_URL = "https://www.zara.com/es/es/products/availability"
STATE_FILE = "state.json"


def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)


def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "previously_in_stock": False,
            "last_heartbeat": None
        }
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def check_stock():
    state = load_state()

    payload = {"skus": list(SKUS.values())}
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.post(AVAILABILITY_URL, json=payload, headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()

    available_sizes = []

    for item in data.get("skusAvailability", []):
        if item.get("availability") == "in_stock":
            for size, sku in SKUS.items():
                if sku == item.get("sku"):
                    available_sizes.append(size)

    # Notify once per restock
    if available_sizes and not state["previously_in_stock"]:
        send_telegram(
            f"🟢 Zara alert 🇪🇸\n\nVestido disponible en tallas: {', '.join(available_sizes)}"
        )
        state["previously_in_stock"] = True

    # Reset when all out of stock
    if not available_sizes:
        state["previously_in_stock"] = False

    # Daily heartbeat (once per UTC day)
    today = datetime.now(timezone.utc).date().isoformat()
    if state["last_heartbeat"] != today:
        send_telegram(
            "🟡 Zara bot running\nAll monitored sizes (M, L, XL) are currently out of stock 🇪🇸"
        )
        state["last_heartbeat"] = today

    save_state(state)


if __name__ == "__main__":
    check_stock()
