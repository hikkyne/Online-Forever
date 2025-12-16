import os
import sys
import json
import asyncio
import platform
import random
import requests
import websockets
from colorama import init, Fore
# from keep_alive import keep_alive  # Uncomment nếu cần

init(autoreset=True)

status = "idle"  # online / dnd / idle
ROTATE_DELAY = 15  # seconds

# Danh sách custom status
custom_status_list = [
    "(≧◡≦)",
    ">w<",
    "ಥ‿ಥ",
    "(つ﹏⊂)",
    "(•ˋ _ ˊ•)",
    "(>'-'<)",
    "(=^-ω-^=)",
    "(=①ω①=)",
    "(=｀ω´=)",
    "(=^･^=)",
    "(=ＴェＴ=)",
    "(=；ェ；=)",
    "(=｀ェ´=)",
    "(=^･ｪ･^=))ﾉ彡☆",
    "(=^-ｪ-^=)",
    "(=ΦｴΦ=)",
    "(ฅ^･ω･^ ฅ)",
    "(=ↀωↀ=)",
    "ฅ(•ㅅ•❀)ฅ",
    "ฅ^•ﻌ•^ฅ",
    "(＾・ω・＾)",
    "(=^-ω-^=)",
    "ヽ(=^･ω･^=)丿",
    "(=^-ω-^=)/",
    "(=^‥^=)",
    "(*^･ｪ･)ﾉ",
    "(●ↀωↀ●)",
    "(≚ᄌ≚)",
    "(=ノωヽ=)",
    "(￣ω￣;)",
    "(•̀ᴗ•́)و ̑̑",
    "(ノω<。)"
]

# Danh sách emoji
emoji_list = [
    {"name": "omencatdancespray_valorant_gif_5", "id": "1098605943777939456", "animated": True},
]

usertoken = os.getenv("TOKEN")
if not usertoken:
    print(f"{Fore.WHITE}[{Fore.RED}-{Fore.WHITE}] Please add a token inside Secrets.")
    sys.exit()

headers = {"Authorization": usertoken, "Content-Type": "application/json"}

validate = requests.get("https://canary.discordapp.com/api/v9/users/@me", headers=headers)
if validate.status_code != 200:
    print(f"{Fore.WHITE}[{Fore.RED}-{Fore.WHITE}] Your token might be invalid. Please check it again.")
    sys.exit()

userinfo = validate.json()
username = userinfo["username"]
userid = userinfo["id"]


async def heartbeat(ws, interval):
    """Send heartbeat to keep connection alive"""
    while True:
        try:
            await asyncio.sleep(interval / 1000)
            await ws.send(json.dumps({"op": 1, "d": None}))
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Heartbeat failed: {e}")
            break


async def rotate_status(ws, status_type):
    """Rotate custom status messages"""
    index = 0
    while True:
        try:
            current_status = custom_status_list[index % len(custom_status_list)]
            random_emoji = random.choice(emoji_list)
            
            payload = {
                "op": 3,
                "d": {
                    "since": 0,
                    "activities": [{
                        "type": 4,
                        "state": current_status,
                        "name": "Custom Status",
                        "id": "custom",
                        "emoji": {
                            "name": random_emoji["name"],
                            "id": random_emoji["id"],
                            "animated": random_emoji["animated"]
                        }
                    }],
                    "status": status_type,
                    "afk": False
                }
            }
            
            await ws.send(json.dumps(payload))
            print(f"{Fore.LIGHTGREEN_EX}[✓] Status updated: {current_status}")
            index += 1
            await asyncio.sleep(ROTATE_DELAY)
            
        except websockets.exceptions.ConnectionClosed:
            print(f"{Fore.RED}[ERROR] WebSocket closed in rotate_status")
            break
        except Exception as e:
            print(f"{Fore.RED}[ERROR] rotate_status: {e}")
            await asyncio.sleep(5)


async def handle_events(ws):
    """Handle incoming WebSocket events without storing large payloads"""
    try:
        while True:
            # Đọc message nhưng không lưu trữ để tránh memory issues
            msg = await ws.recv()
            # Chỉ parse nếu message nhỏ hơn 100KB để tránh lỗi
            if len(msg) < 100000:
                data = json.loads(msg)
                # Có thể log events quan trọng ở đây nếu cần
                if data.get("op") == 9:  # Invalid session
                    print(f"{Fore.YELLOW}[!] Invalid session, reconnecting...")
                    break
    except websockets.exceptions.ConnectionClosed:
        print(f"{Fore.RED}[ERROR] WebSocket closed in handle_events")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] handle_events: {e}")


async def onliner(token, status_type):
    """Main WebSocket connection handler"""
    retry_count = 0
    max_retries = 999
    
    while retry_count < max_retries:
        try:
            # Giảm max_size xuống để tránh nhận messages quá lớn
            async with websockets.connect(
                "wss://gateway.discord.gg/?v=10&encoding=json",
                max_size=2 * 1024 * 1024,  # 2MB thay vì 10MB
                compression=None,
                ping_interval=None,
                ping_timeout=None
            ) as ws:
                print(f"{Fore.LIGHTCYAN_EX}[*] WebSocket connected")
                
                # Nhận hello message
                hello = json.loads(await ws.recv())
                heartbeat_interval = hello["d"]["heartbeat_interval"]
                print(f"{Fore.LIGHTCYAN_EX}[*] Heartbeat interval: {heartbeat_interval}ms")
                
                # Identify với intents = 0 để không nhận events không cần thiết
                identify = {
                    "op": 2,
                    "d": {
                        "token": token,
                        "intents": 0,  # Không subscribe vào bất kỳ events nào
                        "properties": {
                            "$os": "Windows 10",
                            "$browser": "Google Chrome",
                            "$device": "Windows",
                        },
                        "presence": {
                            "status": status_type,
                            "afk": False
                        }
                    }
                }
                
                await ws.send(json.dumps(identify))
                print(f"{Fore.LIGHTGREEN_EX}[✓] Identified with Discord")
                
                # Reset retry count khi kết nối thành công
                retry_count = 0
                
                # Tạo các tasks
                heartbeat_task = asyncio.create_task(heartbeat(ws, heartbeat_interval))
                rotate_task = asyncio.create_task(rotate_status(ws, status_type))
                event_task = asyncio.create_task(handle_events(ws))
                
                # Chờ cho đến khi có task nào complete
                done, pending = await asyncio.wait(
                    [heartbeat_task, rotate_task, event_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Cancel các task còn lại
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                
                # Check lỗi từ task đã complete
                for task in done:
                    try:
                        task.result()
                    except Exception as e:
                        print(f"{Fore.RED}[ERROR] Task failed: {e}")
                        
        except websockets.exceptions.ConnectionClosedError as e:
            retry_count += 1
            wait_time = min(2 ** retry_count, 60)
            print(f"{Fore.YELLOW}[!] Connection closed: {e}")
            print(f"{Fore.YELLOW}[!] Retrying in {wait_time}s... (Attempt {retry_count}/{max_retries})")
            await asyncio.sleep(wait_time)
            
        except Exception as e:
            retry_count += 1
            wait_time = min(2 ** retry_count, 60)
            print(f"{Fore.RED}[ERROR] Unexpected error: {e}")
            print(f"{Fore.YELLOW}[!] Retrying in {wait_time}s... (Attempt {retry_count}/{max_retries})")
            await asyncio.sleep(wait_time)


async def run_onliner():
    """Main entry point"""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    
    print(f"{Fore.WHITE}[{Fore.LIGHTGREEN_EX}+{Fore.WHITE}] Logged in as {Fore.LIGHTBLUE_EX}{username} {Fore.WHITE}({userid})!")
    print(f"{Fore.WHITE}[{Fore.LIGHTGREEN_EX}+{Fore.WHITE}] Status rotation: {Fore.LIGHTBLUE_EX}{ROTATE_DELAY}s")
    print(f"{Fore.WHITE}[{Fore.LIGHTGREEN_EX}+{Fore.WHITE}] Total statuses: {Fore.LIGHTBLUE_EX}{len(custom_status_list)}")
    print(f"{Fore.LIGHTCYAN_EX}{'='*50}")
    
    await onliner(usertoken, status)


if __name__ == "__main__":
    # keep_alive()  # Uncomment nếu cần
    asyncio.run(run_onliner())
