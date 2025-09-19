# main.py
import os
import sys
import json
import asyncio
import platform
import requests
import websockets
from colorama import init, Fore
from keep_alive import keep_alive  # nếu bạn đang dùng keep_alive riêng, giữ import này

init(autoreset=True)

# ========= Cấu hình =========
STATUS = "idle"                     # online | dnd | idle | invisible
CUSTOM_STATUS = "Chơi vơi"               # custom status text (ngắn)
GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"
REST_BASE    = "https://discord.com/api/v9"

# ========= Env =========
TOKEN = os.getenv("TOKEN")
EMOJI_ID = os.getenv("EMOJI_ID")  # <-- BẮT BUỘC có
EMOJI_ANIMATED = os.getenv("EMOJI_ANIMATED", "false").lower() == "true"

if not TOKEN:
    print(f"{Fore.WHITE}[{Fore.RED}-{Fore.WHITE}] Please add TOKEN in environment variables.")
    sys.exit(1)
if not EMOJI_ID:
    print(f"{Fore.WHITE}[{Fore.RED}-{Fore.WHITE}] Please add EMOJI_ID in environment variables.")
    sys.exit(1)

headers = {"Authorization": TOKEN, "Content-Type": "application/json"}

# Validate token
validate = requests.get(f"{REST_BASE}/users/@me", headers=headers)
if validate.status_code != 200:
    print(f"{Fore.WHITE}[{Fore.RED}-{Fore.WHITE}] Your token might be invalid. Please check it again.")
    sys.exit(1)

userinfo = validate.json()
username = userinfo.get("username", "unknown")
userid   = userinfo.get("id", "unknown")

# ========= Gateway helpers =========
async def op_send(ws, payload: dict):
    """Gửi payload an toàn (tránh >1MB)."""
    data = json.dumps(payload, separators=(",", ":"))
    if len(data) > 800_000:
        print(f"{Fore.WHITE}[{Fore.RED}!{Fore.WHITE}] Blocked oversized payload len={len(data)}")
        return
    await ws.send(data)

async def identify(ws):
    # OP 2 IDENTIFY
    payload = {
        "op": 2,
        "d": {
            "token": TOKEN,
            "properties": {
                "$os": platform.system(),
                "$browser": "chrome",
                "$device": "desktop",
            },
            "presence": {"status": STATUS, "afk": False},
            "compress": False,
        },
    }
    await op_send(ws, payload)

async def set_custom_status(ws):
    # OP 3 PRESENCE UPDATE (type 4 = Custom Status)
    # Với emoji custom: chỉ dùng ID; "name" để None (null). Nếu emoji animated, đặt animated=True.
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
                    "emoji": {
                        "name": None,                # không cần name, chỉ dùng id
                        "id": EMOJI_ID,              # <-- ID emoji custom
                        "animated": EMOJI_ANIMATED,  # true nếu là <a:...:id>
                    },
                }
            ],
            "status": STATUS,
            "afk": False,
        },
    }
    await op_send(ws, payload)

async def heartbeat_loop(ws, interval_ms: int):
    """Gửi heartbeat đều đặn. d phải là None (null)."""
    try:
        while True:
            await asyncio.sleep(interval_ms / 1000)
            await op_send(ws, {"op": 1, "d": None})
    except asyncio.CancelledError:
        pass

async def onliner():
    """Kết nối gateway, identify, đặt custom status, chạy heartbeat + nhận sự kiện."""
    backoff = 1
    while True:
        try:
            async with websockets.connect(
                GATEWAY_URL,
                max_size=2**20,      # inbound limit (1MB)
                ping_interval=20,
                ping_timeout=20,
            ) as ws:
                # Nhận HELLO (OP 10)
                hello = json.loads(await ws.recv())
                heartbeat_interval = hello["d"]["heartbeat_interval"]

                # Identify & đặt custom status
                await identify(ws)
                await set_custom_status(ws)

                print(
                    f"{Fore.WHITE}[{Fore.LIGHTGREEN_EX}+{Fore.WHITE}] Logged in as "
                    f"{Fore.LIGHTBLUE_EX}{username}{Fore.WHITE} ({userid}) – "
                    f"status: {STATUS}, custom: '{CUSTOM_STATUS}', emoji_id: {EMOJI_ID}, animated={EMOJI_ANIMATED}"
                )

                # Chạy heartbeat song song
                hb_task = asyncio.create_task(heartbeat_loop(ws, heartbeat_interval))

                # Lắng nghe sự kiện từ gateway (KHÔNG gửi lại, KHÔNG in payload lớn)
                async for _ in ws:
                    pass

                hb_task.cancel()

        except Exception as e:
            print(f"{Fore.WHITE}[{Fore.RED}!{Fore.WHITE}] Gateway error: {e}")

        # Reconnect với backoff
        await asyncio.sleep(backoff)
        backoff = min(backoff * 2, 60)

async def main():
    try:
        keep_alive()  # nếu bạn có web healthcheck riêng
    except Exception:
        pass

    await onliner()

if __name__ == "__main__":
    asyncio.run(main())
