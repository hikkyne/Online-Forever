# main.py
import os, sys, json, asyncio, platform, requests, websockets
from colorama import init, Fore
from flask import Flask
from threading import Thread

init(autoreset=True)

STATUS = "idle"            # online | dnd | idle | invisible
CUSTOM_STATUS = "zzz"      # chữ ngắn
GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"
REST_BASE   = "https://discord.com/api/v9"

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print(f"{Fore.WHITE}[{Fore.RED}-{Fore.WHITE}] Please add TOKEN in Railway Variables.")
    sys.exit(1)

# Validate token
headers = {"Authorization": TOKEN, "Content-Type": "application/json"}
r = requests.get(f"{REST_BASE}/users/@me", headers=headers)
if r.status_code != 200:
    print(f"{Fore.WHITE}[{Fore.RED}-{Fore.WHITE}] Your token might be invalid.")
    sys.exit(1)
me = r.json()
username = me.get("username", "unknown")
userid   = me.get("id", "unknown")

# ---- Flask keep-alive (một bản duy nhất) ----
app = Flask(__name__)

@app.get("/")
def root():
    return '<meta http-equiv="refresh" content="0; URL=https://phantom.fr.to/support"/>'

def run_flask():
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)

def start_keep_alive():
    Thread(target=run_flask, daemon=True).start()

# ---- Discord Gateway helpers ----
async def op_send(ws, payload: dict):
    data = json.dumps(payload)
    # Phòng sự cố: KHÔNG BAO GIỜ gửi khối > 1MB
    if len(data) > 800_000:
        print(f"{Fore.WHITE}[{Fore.RED}!{Fore.WHITE}] BLOCKED sending payload > 800KB (len={len(data)})")
        return
    await ws.send(data)

async def identify(ws):
    await op_send(ws, {
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
    })

async def set_custom_status(ws):
    await op_send(ws, {
        "op": 3,
        "d": {
            "since": 0,
            "activities": [
                {
                    "type": 4,   # Custom Status
                    "state": CUSTOM_STATUS,
                    "name": "Custom Status",
                    "id": "custom",
                }
            ],
            "status": STATUS,
            "afk": False,
        },
    })

async def heartbeat_loop(ws, interval_ms):
    HEARTBEAT_PAYLOAD = {"op": 1, "d": None}  # CHỈ thế này thôi!
    try:
        while True:
            await asyncio.sleep(interval_ms / 1000)
            await op_send(ws, HEARTBEAT_PAYLOAD)
    except asyncio.CancelledError:
        pass

async def gateway_loop():
    backoff = 1
    while True:
        try:
            async with websockets.connect(
                GATEWAY_URL,
                max_size=2**20,   # limit inbound 1MB (chuẩn)
                ping_interval=20,
                ping_timeout=20,
            ) as ws:
                # Nhận HELLO (OP 10)
                hello = json.loads(await ws.recv())
                hb_interval = hello["d"]["heartbeat_interval"]

                await identify(ws)
                await set_custom_status(ws)

                hb_task = asyncio.create_task(heartbeat_loop(ws, hb_interval))

                print(f"{Fore.WHITE}[{Fore.LIGHTGREEN_EX}+{Fore.WHITE}] Logged in as "
                      f"{Fore.LIGHTBLUE_EX}{username}{Fore.WHITE} ({userid}) – status: {STATUS}, custom: '{CUSTOM_STATUS}'")

                # Lắng nghe sự kiện nhưng KHÔNG gửi lại
                async for _ in ws:
                    # Bỏ qua để không phình log/payload
                    pass

                hb_task.cancel()

        except Exception as e:
            print(f"{Fore.WHITE}[{Fore.RED}!{Fore.WHITE}] Gateway error: {e}")

        await asyncio.sleep(backoff)
        backoff = min(backoff * 2, 60)

async def main():
    start_keep_alive()
    await gateway_loop()

if __name__ == "__main__":
    asyncio.run(main())
