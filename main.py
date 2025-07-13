import os
import sys
import json
import asyncio
import platform
import requests
import websockets
from colorama import init, Fore
from keep_alive import keep_alive  # Nếu không dùng Replit/Railway, bạn có thể xóa dòng này

init(autoreset=True)

status = "idle"  # Trạng thái Discord: online / idle / dnd
custom_status = "(=^-ω-^=) ngủ sớm"  # Custom status text - giới hạn 128 ký tự

# Lấy token từ biến môi trường
usertoken = os.getenv("TOKEN")
if not usertoken:
    print(f"{Fore.WHITE}[{Fore.RED}-{Fore.WHITE}] Please add a token inside Secrets.")
    sys.exit()

headers = {
    "Authorization": usertoken,
    "Content-Type": "application/json"
}

# Kiểm tra token hợp lệ
validate = requests.get("https://canary.discordapp.com/api/v9/users/@me", headers=headers)
if validate.status_code != 200:
    print(f"{Fore.WHITE}[{Fore.RED}-{Fore.WHITE}] Your token might be invalid. Please check it again.")
    sys.exit()

userinfo = validate.json()
username = userinfo["username"]
discriminator = userinfo["discriminator"]
userid = userinfo["id"]

async def onliner(token, status):
    async with websockets.connect("wss://gateway.discord.gg/?v=9&encoding=json") as ws:
        start = json.loads(await ws.recv())
        heartbeat = start["d"]["heartbeat_interval"]

        # Payload đăng nhập Discord Gateway
        auth = {
            "op": 2,
            "d": {
                "token": token,
                "properties": {
                    "$os": "Windows",
                    "$browser": "Chrome",
                    "$device": "Desktop"
                },
                "presence": {
                    "status": status,
                    "afk": False
                }
            }
        }
        await ws.send(json.dumps(auth))

        # Custom status với emoji tuỳ chỉnh
        safe_status = custom_status[:128] if custom_status else ""
        cstatus = {
            "op": 3,
            "d": {
                "since": 0,
                "activities": [
                    {
                        "type": 4,
                        "state": safe_status,
                        "name": "Custom Status",
                        "id": "custom",
                        "emoji": {
                            "name": "omencatdancespray_valorant_gif_5",
                            "id": "1364244170369400942",
                            "animated": True
                        }
                    }
                ],
                "status": status,
                "afk": False
            }
        }

        # Kiểm tra trước khi gửi để tránh lỗi message quá lớn
        msg = json.dumps(cstatus)
        if len(msg.encode("utf-8")) > 1024 * 1024:
            print(f"{Fore.RED}[ERROR] Message too big ({len(msg)} bytes). Skipped.")
            return
        await ws.send(msg)

        # Gửi heartbeat lần đầu
        await asyncio.sleep(heartbeat / 1000)
        await ws.send(json.dumps({"op": 1, "d": None}))

async def run_onliner():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    print(f"{Fore.WHITE}[{Fore.LIGHTGREEN_EX}+{Fore.WHITE}] Logged in as {Fore.LIGHTBLUE_EX}{username}#{discriminator} {Fore.WHITE}({userid})!")

    try:
        while True:
            await onliner(usertoken, status)
            await asyncio.sleep(50)  # Delay vòng lặp
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"{Fore.RED}[ERROR] WebSocket closed: {e}")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Unexpected: {e}")
# Chạy chương trình
asyncio.run(run_onliner())
