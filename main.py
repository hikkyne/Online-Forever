import os
import sys
import json
import asyncio
import platform
import requests
import websockets
from colorama import init, Fore
from flask import Flask
from threading import Thread

# ========= Config =========
init(autoreset=True)

STATUS = "idle"           # online | dnd | idle | invisible (Discord Gateway)
CUSTOM_STATUS = "zzz"     # Custom Status text (short thôi)
GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"  # v10 mới
REST_BASE   = "https://discord.com/api/v9"                    # REST base

# ========= Token =========
USERTOKEN = os.getenv("TOKEN")
if not USERTOKEN:
    print(f"{Fore.WHITE}[{Fore.RED}-{Fore.WHITE}] Please add TOKEN in Railway Variables.")
    sys.exit(1)

headers = {"Authorization": USERTOKEN, "Content-Type": "application/json"}
validate = requests.get(f"{REST_BASE}/users/@me", headers=headers)
if validate.status_code != 200:
    print(f"{Fore.WHITE}[{Fore.RED}-{Fore.WHITE}] Your token might be invalid.")
    sys.exit(1)

userinfo = validate.json()
username = userinfo.get("username", "unknown")
userid   = userinfo.get("id", "unknown")

# ========= Flask keep-alive (1 bản duy nhất) =========
app = Flask(__name__)

@app.get("/")
def root():
    # Có thể đổi thành landing nhỏ hoặc healthcheck
    return '<meta http-equiv="refresh" content="0; URL=https://phantom.fr.to/support"/>'

def run_flask():
    port = int(os.environ.get("PORT", "8080"))  # Railway sẽ set PORT
    app.run(host="0.0.0.0", port=port)

def start_keep_alive():
    Thread(target=run_flask, daemon=True).start()

# ========= Discord Gateway =========
async def identify(ws):
    # OP 2 IDENTIFY
    payload = {
        "op": 2,
        "d": {
            "token": USERTOKEN,
            "properties": {
                "$os": platform.system(),
                "$browser": "chrome",
                "$device": "desktop",
            },
            "presence": {"status": STATUS, "afk": False},
            "compress": False,
        },
    }
    await ws.send(json.dumps(payload))

async def set_custom_status(ws):
    # OP 3 PRESENCE UPDATE – activity type 4 = Custom Status (user accounts)
    payload = {
        "op": 3,
        "d": {
            "since": 0,
            "activities": [
                {
                    "type": 4,
                    "state": CUSTOM_STATUS,
                    "name": "Custom Status",
                    "id": "custom",
                }
            ],
            "status": STATUS,
            "afk": False,
        },
    }
    await ws.send(json.dumps(payload))

async def heartbeat_loop(ws, interval_ms):
    # Gửi OP 1 đều đặn; "d" phải là null (None), không nhồi dữ liệu
    try:
        while True:
            await asyncio.sleep(interval_ms / 1000)
            payload = {"op": 1, "d": None}
            await ws.send(json.dumps(payload))
    except asyncio.CancelledError:
        # khi đóng/reconnect
        pass

async def gateway_loop():
    backoff = 1
    while True:
        try:
            async with websockets.connect(GATEWAY_URL, max_size=2**20) as ws:
                # Nhận HELLO (OP 10) để lấy heartbeat_interval
                hello = json.loads(await ws.recv())
                hb_interval = hello["d"]["heartbeat_interval"]

                # IDENTIFY và đặt custom status
                await identify(ws)
                await set_custom_status(ws)

                # Chạy heartbeat song song
                hb_task = asyncio.create_task(heartbeat_loop(ws, hb_interval))

                print(f"{Fore.WHITE}[{Fore.LIGHTGREEN_EX}+{Fore.WHITE}] Logged in as "
                      f"{Fore.LIGHTBLUE_EX}{username}{Fore.WHITE} ({userid}) – status: {STATUS}, custom: '{CUSTOM_STATUS}'")

                # Lắng nghe các sự kiện (đừng echo ra những payload lớn)
                async for _ in ws:
                    # Không cần in sự kiện để tránh log khủng -> frame outbound không phình
                    # Có thể thêm logic nếu muốn handle OP 7/9/… để resume
                    pass

                hb_task.cancel()
        except Exception as e:
            print(f"{Fore.WHITE}[{Fore.RED}!{Fore.WHITE}] Gateway error: {e}")
        # Exponential backoff nhẹ khi reconnect
        await asyncio.sleep(backoff)
        backoff = min(backoff * 2, 60)

async def main():
    start_keep_alive()
    await gateway_loop()

if __name__ == "__main__":
    # Railway sẽ chạy "python main.py" (Start Command)
    asyncio.run(main())
