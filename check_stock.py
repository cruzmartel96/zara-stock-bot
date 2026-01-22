import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

PRODUCT_ID = 464886560  # XS
STORE_ID = 10703        # Spain

URL = f"https://www.zara.com/itxrest/2/catalog/store/{STORE_ID}/product/{PRODUCT_ID}/detail"


def send_telegram(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        },
        timeout=10
    )


def check_stock():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    r = requests.get(URL, headers=headers, timeout=15)

    if r.status_code != 200:
        print(f"Zara returned {r.status_code}")
        return

    data = r.json()

    for size in data.get("sizeAvailability", []):
        if size.get("sizeId") == PRODUCT_ID:
            status = size.get("availability")
            print("Stock status:", status)

            if status == "in_stock":
                send_telegram("🛍️ Zara alert: XS is BACK IN STOCK!")
            return

    print("Size not found")


if __name__ == "__main__":
    check_stock()

