import os
import json
import requests
from datetime import datetime, timezone

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# Zara availability endpoint you already discovered
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

    r = requests.get(AVAILABILITY_URL, timeout=15)
    r.raise_for_status()
    data = r.json()

    availability = {
        item["sku"]: item["availability"]
        for item in data.get("skusAvailability", [])
    }

    for sku, size in TARGET_SKUS.items():
        status = availability.get(sku)
        previously_notified = state["notified"].get(str(sku), False)

        if status == "in_stock" and not previously_notified:
            send_telegram(f"🛍️ Zara alert: size {size} is BACK IN STOCK!")
            state["notified"][str(sku)] = True

        if status != "in_stock":
            state["notified"][str(sku)] = False


    # 💓 Daily heartbeat
    today = datetime.now(timezone.utc).date().isoformat()
    if state["last_heartbeat"] != today:
        send_telegram("💓 Zara bot is alive — still checking stock")
        state["last_heartbeat"] = today

    save_state(state)


if __name__ == "__main__":
    check_stock()
