"""
keep_alive.py — Run this as a separate process or cron job.
Pings your own app every 10 minutes to prevent any hosting platform
(Render, Railway, etc.) from spinning it down due to inactivity.
Also makes a lightweight MongoDB ping to keep the Atlas connection warm.
"""

import time
import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

APP_URL = os.getenv("APP_URL", "http://localhost:5000")  # Set this in .env
MONGO_URI = os.getenv("MONGO_URI")
PING_INTERVAL = 600  # 10 minutes


def ping_app():
    try:
        r = requests.get(APP_URL, timeout=10)
        print(f"[App ping] {r.status_code}")
    except Exception as e:
        print(f"[App ping] Failed: {e}")


def ping_mongo():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        client.close()
        print("[Mongo ping] OK")
    except Exception as e:
        print(f"[Mongo ping] Failed: {e}")


if __name__ == "__main__":
    print("Keep-alive started.")
    while True:
        ping_app()
        ping_mongo()
        time.sleep(PING_INTERVAL)