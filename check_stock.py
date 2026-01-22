import os
import time
import json
import requests
from datetime import datetime, timezone

# -------------------------
# CONFIG
# -------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PRODUCT_ID = "464887739"
STORE_ID = "10703"  # Spain store

AVAILABILITY_URL = (
    f"https://www.zara.com/itxrest/2/catalog/store/"
    f"{STORE_ID}/product/{PRODUCT_ID}/availability"
)

TARGET_SIZES = {
    464886562: "M",
    464886563: "L",
    464886564: "XL"
}

STATE_FILE = "/tmp/state.json"  # local to runner

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

MAX_RETRIES = 3
INITIAL_BACKOFF = 5
TIMEOUT = 15

# -------------------------
# HELPERS
# -------------------------

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram credentials missing")
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print("Telegram send failed:", e)


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"last_heartbeat": None, "notified": {}}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


# -------------------------
# STOCK CHECK
# -------------------------

def check_stock():
    state = load_state()  # always loaded at the top
    backoff = INITIAL_BACKOFF

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(AVAILABILITY_URL, headers=HEADERS, timeout=TIMEOUT)

            # ----------------- HANDLE BLOCKED / NON-200 STATUS -----------------
            if response.status_code != 200:
                msg = f"⚠️ Zara blocked this run (status {response.status_code}, attempt {attempt}/{MAX_RETRIES})"
                print(msg)
                send_telegram(msg)
                save_state(state)
                return

            # silent log of Zara JSON
            with open("/tmp/zara_last_response.json", "w") as f:
                json.dump(response.json(), f)

            # parse sizes
            data = response.json()
            sizes = data.get("products", [{}])[0].get("sizeAvailability", [])

            for size in sizes:
                size_id = size.get("id")
                availability = size.get("availability")

                if size_id in TARGET_SIZES and availability == "in_stock" and not state["notified"].get(str(size_id)):
                    send_telegram(f"🟢 Zara alert! Size {TARGET_SIZES[size_id]} is IN STOCK 🎉")
                    state["notified"][str(size_id)] = True

                if size_id in TARGET_SIZES and availability != "in_stock":
                    state["notified"][str(size_id)] = False

            # ----------------- DAILY HEARTBEAT -----------------
            today = datetime.now(timezone.utc).date().isoformat()
            if state.get("last_heartbeat") != today:
                send_telegram("💓 Zara bot is alive — still checking stock")
                state["last_heartbeat"] = today

            save_state(state)
            return

        except Exception as e:
            print(f"Request error on attempt {attempt}: {e}")
            if attempt == MAX_RETRIES:
                send_telegram(f"❌ Zara stock check failed after {MAX_RETRIES} attempts\n{e}")
                return
            time.sleep(backoff)
            backoff *= 2


# -------------------------
# ENTRY POINT
# -------------------------

if __name__ == "__main__":
    check_stock()

