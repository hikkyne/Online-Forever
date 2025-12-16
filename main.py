import os
import sys
import json
import asyncio
import platform
import random
import requests
import websockets
from colorama import init, Fore
from datetime import datetime
# from keep_alive import keep_alive  # Uncomment nếu cần

init(autoreset=True)

status = "idle"  # online / dnd / idle
ROTATE_DELAY = 15  # seconds

# Danh sách custom status
custom_status_list = [
    "(つ﹏⊂) zzz",
    "(￣ω￣;)",
    "(•̀ᴗ•́)و ̑̑",
    "(ノω<。)"
]

# Danh sách emoji
emoji_list = [
    {"name": "omencatdancespray_valorant_gif_5", "id": "753167522643181599", "animated": True},
]

usertoken = os.getenv("TOKEN")
if not usertoken:
    print(f"{Fore.WHITE}[{Fore.RED}-{Fore.WHITE}] Please add a token inside Secrets.")
    sys.exit()

headers = {"Authorization": usertoken, "Content-Type": "application/json"}

validate = requests.get("[https://canary.discordapp.com/api/v9/users/@me](https://canary.discordapp.com/api/v9/users/@me)", headers=headers)
if validate.status_code != 200:
    print(f"{Fore.WHITE}[{Fore.RED}-{Fore.WHITE}] Your token might be invalid. Please check it again.")
    sys.exit()

userinfo = validate.json()
username = userinfo["username"]
userid = userinfo["id"]


def log(message, color=Fore.WHITE):
    """Helper function to log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Fore.LIGHTBLACK_EX}[{timestamp}] {color}{message}")


async def heartbeat(ws, interval):
    """Send heartbeat to keep connection alive"""
    heartbeat_count = 0
    while True:
        try:
            await asyncio.sleep(interval / 1000)
            await ws.send(json.dumps({"op": 1, "d": None}))
            heartbeat_count += 1
            if heartbeat_count % 10 == 0:  # Log mỗi 10 heartbeats
                log(f"Heartbeat #{heartbeat_count} sent", Fore.LIGHTBLACK_EX)
        except Exception as e:
            log(f"Heartbeat failed: {e}", Fore.RED)
            break


async def rotate_status(ws, status_type):
    """Rotate custom status messages"""
    index = 0
    
    # Đợi 3 giây sau khi connect trước khi bắt đầu rotate
    await asyncio.sleep(3)
    log("Starting status rotation...", Fore.LIGHTCYAN_EX)
    
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
            
            log(f"Sending status update #{index + 1}: {current_status}", Fore.LIGHTYELLOW_EX)
            await ws.send(json.dumps(payload))
            log(f"Status sent successfully!", Fore.LIGHTGREEN_EX)
            
            index += 1
            log(f"Waiting {ROTATE_DELAY} seconds until next rotation...", Fore.LIGHTBLACK_EX)
            await asyncio.sleep(ROTATE_DELAY)
            
        except websockets.exceptions.ConnectionClosed:
            log("WebSocket closed in rotate_status", Fore.RED)
            break
        except Exception as e:
            log(f"Error in rotate_status: {e}", Fore.RED)
            await asyncio.sleep(5)


async def handle_events(ws):
    """Handle incoming WebSocket events"""
    try:
        while True:
            msg = await ws.recv()
            
            # Parse message để check response
            if len(msg) < 100000:
                try:
                    data = json.loads(msg)
                    op = data.get("op")
                    
                    # Log các events quan trọng
                    if op == 0:  # Dispatch
                        event_type = data.get("t")
                        if event_type == "READY":
                            log("✓ READY event received - Connected successfully!", Fore.LIGHTGREEN_EX)
                        elif event_type == "PRESENCE_UPDATE":
                            log("✓ Presence updated", Fore.LIGHTGREEN_EX)
                    elif op == 9:  # Invalid session
                        log("Invalid session, need to reconnect", Fore.YELLOW)
                        break
                    elif op == 11:  # Heartbeat ACK
                        pass  # Không log để tránh spam
                        
                except json.JSONDecodeError:
                    pass
                    
    except websockets.exceptions.ConnectionClosed:
        log("WebSocket closed in handle_events", Fore.RED)
    except Exception as e:
        log(f"Error in handle_events: {e}", Fore.RED)


async def onliner(token, status_type):
    """Main WebSocket connection handler"""
    retry_count = 0
    max_retries = 999
    
    while retry_count < max_retries:
        try:
            log("Connecting to Discord Gateway...", Fore.LIGHTCYAN_EX)
            
            async with websockets.connect(
                "wss://gateway.discord.gg/?v=10&encoding=json",
                max_size=2 * 1024 * 1024,
                compression=None,
                ping_interval=None,
                ping_timeout=None
            ) as ws:
                log("WebSocket connected!", Fore.LIGHTGREEN_EX)
                
                # Nhận hello message
                hello = json.loads(await ws.recv())
                heartbeat_interval = hello["d"]["heartbeat_interval"]
                log(f"Heartbeat interval: {heartbeat_interval}ms", Fore.LIGHTCYAN_EX)
                
                # Identify
                identify = {
                    "op": 2,
                    "d": {
                        "token": token,
                        "intents": 0,
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
                log("Identify payload sent", Fore.LIGHTCYAN_EX)
                
                # Reset retry count
                retry_count = 0
                
                # Tạo các tasks
                heartbeat_task = asyncio.create_task(heartbeat(ws, heartbeat_interval))
                rotate_task = asyncio.create_task(rotate_status(ws, status_type))
                event_task = asyncio.create_task(handle_events(ws))
                
                log("All tasks started, running...", Fore.LIGHTGREEN_EX)
                log("="*60, Fore.LIGHTBLACK_EX)
                
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
                
                # Check lỗi
                for task in done:
                    try:
                        task.result()
                    except Exception as e:
                        log(f"Task failed: {e}", Fore.RED)
                        
        except websockets.exceptions.ConnectionClosedError as e:
            retry_count += 1
            wait_time = min(2 ** retry_count, 60)
            log(f"Connection closed: {e}", Fore.YELLOW)
            log(f"Retrying in {wait_time}s... (Attempt {retry_count}/{max_retries})", Fore.YELLOW)
            await asyncio.sleep(wait_time)
            
        except Exception as e:
            retry_count += 1
            wait_time = min(2 ** retry_count, 60)
            log(f"Unexpected error: {e}", Fore.RED)
            log(f"Retrying in {wait_time}s... (Attempt {retry_count}/{max_retries})", Fore.YELLOW)
            await asyncio.sleep(wait_time)


async def run_onliner():
    """Main entry point"""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    
    print(f"\n{Fore.LIGHTCYAN_EX}{'='*60}")
    print(f"{Fore.LIGHTGREEN_EX}Discord Status Rotator")
    print(f"{Fore.LIGHTCYAN_EX}{'='*60}\n")
    print(f"{Fore.WHITE}User: {Fore.LIGHTBLUE_EX}{username} {Fore.LIGHTBLACK_EX}({userid})")
    print(f"{Fore.WHITE}Rotation Interval: {Fore.LIGHTBLUE_EX}{ROTATE_DELAY}
