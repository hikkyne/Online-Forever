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

init(autoreset=True)

status = "idle"
ROTATE_DELAY = 60

custom_status_list = [
    "(つ﹏⊂) zzz",
    "(￣ω￣;)",
    "(•̀ᴗ•́)و ̑̑",
    "(ノω<。)",
    "(つ﹏⊂) zzzz",
]

emoji_list = [
    {"name": "omencatdancespray_valorant_gif_5", "id": "753167522643181599", "animated": False},
]

usertoken = os.getenv("TOKEN")
if not usertoken:
    print(f"{Fore.WHITE}[{Fore.RED}-{Fore.WHITE}] Please add a token inside Secrets.")
    sys.exit()

headers = {"Authorization": usertoken, "Content-Type": "application/json"}
validate = requests.get("https://canary.discordapp.com/api/v9/users/@me", headers=headers)
if validate.status_code != 200:
    print(f"{Fore.WHITE}[{Fore.RED}-{Fore.WHITE}] Your token might be invalid.")
    sys.exit()

userinfo = validate.json()
username = userinfo["username"]
userid = userinfo["id"]


def log(msg, color=Fore.WHITE):
    print(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M:%S')}] {color}{msg}")


class DiscordClient:
    def __init__(self, token, status_type):
        self.token = token
        self.status_type = status_type
        self.ws = None
        self.heartbeat_interval = None
        self.is_ready = False
        self.status_index = 0
        self.should_run = True
        
    async def send_heartbeat(self):
        """Heartbeat loop"""
        count = 0
        while self.should_run:
            try:
                await asyncio.sleep(self.heartbeat_interval / 1000)
                if self.ws and not self.ws.closed:
                    await self.ws.send(json.dumps({"op": 1, "d": None}))
                    count += 1
                    if count % 20 == 0:
                        log(f"Heartbeat #{count}", Fore.LIGHTBLACK_EX)
            except Exception as e:
                log(f"Heartbeat error: {e}", Fore.RED)
                break
                
    async def update_status(self):
        """Update status with current text"""
        if not self.is_ready or not self.ws or self.ws.closed:
            return False
            
        try:
            text = custom_status_list[self.status_index % len(custom_status_list)]
            emoji = random.choice(emoji_list)
            
            payload = {
                "op": 3,
                "d": {
                    "since": 0,
                    "activities": [{
                        "type": 4,
                        "state": text,
                        "name": "Custom Status",
                        "id": "custom",
                        "emoji": {
                            "name": emoji["name"],
                            "id": emoji["id"],
                            "animated": emoji["animated"]
                        }
                    }],
                    "status": self.status_type,
                    "afk": False
                }
            }
            
            await self.ws.send(json.dumps(payload))
            log(f"✓ Status #{self.status_index + 1}: {text}", Fore.LIGHTGREEN_EX)
            return True
        except Exception as e:
            log(f"Status update error: {e}", Fore.RED)
            return False
            
    async def rotate_status_loop(self):
        """Main status rotation loop"""
        # Wait for ready
        while not self.is_ready and self.should_run:
            await asyncio.sleep(0.5)
            
        if not self.should_run:
            return
            
        log("Status rotation started!", Fore.LIGHTCYAN_EX)
        
        while self.should_run:
            if self.is_ready:
                success = await self.update_status()
                if success:
                    self.status_index += 1
                    
            await asyncio.sleep(ROTATE_DELAY)
            
    async def handle_messages(self):
        """Handle incoming gateway messages"""
        try:
            async for msg in self.ws:
                if len(msg) > 100000:
                    continue
                    
                try:
                    data = json.loads(msg)
                    op = data.get("op")
                    
                    if op == 10:  # Hello
                        self.heartbeat_interval = data["d"]["heartbeat_interval"]
                        log(f"Heartbeat: {self.heartbeat_interval}ms", Fore.LIGHTCYAN_EX)
                        
                    elif op == 0:  # Dispatch
                        event = data.get("t")
                        if event == "READY":
                            self.is_ready = True
                            log("✓ READY - Bot is online!", Fore.LIGHTGREEN_EX)
                        elif event == "RESUMED":
                            self.is_ready = True
                            log("✓ Session resumed", Fore.LIGHTGREEN_EX)
                            
                    elif op == 9:  # Invalid Session
                        resumable = data.get("d", False)
                        log(f"Invalid session (resumable: {resumable})", Fore.YELLOW)
                        self.is_ready = False
                        
                        if not resumable:
                            # Wait before re-identifying
                            await asyncio.sleep(random.uniform(1, 5))
                            await self.identify()
                            
                    elif op == 7:  # Reconnect
                        log("Server requested reconnect", Fore.YELLOW)
                        self.should_run = False
                        break
                        
                except json.JSONDecodeError:
                    pass
                    
        except websockets.exceptions.ConnectionClosed as e:
            log(f"Connection closed: {e.code if hasattr(e, 'code') else 'unknown'}", Fore.RED)
        except Exception as e:
            log(f"Message handler error: {e}", Fore.RED)
            
    async def identify(self):
        """Send identify to Discord"""
        payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "properties": {
                    "$os": "windows",
                    "$browser": "chrome",
                    "$device": "pc"
                },
                "presence": {
                    "status": self.status_type,
                    "since": 0,
                    "activities": [],
                    "afk": False
                }
            }
        }
        
        await self.ws.send(json.dumps(payload))
        log("Identify sent", Fore.LIGHTCYAN_EX)
        
    async def connect(self):
        """Main connection loop"""
        retry = 0
        
        while retry < 999:
            try:
                log("Connecting to Discord...", Fore.LIGHTCYAN_EX)
                
                self.ws = await websockets.connect(
                    "wss://gateway.discord.gg/?v=10&encoding=json",
                    max_size=2 * 1024 * 1024,
                    compression=None
                )
                
                log("Connected!", Fore.LIGHTGREEN_EX)
                
                # Reset state
                self.is_ready = False
                self.should_run = True
                retry = 0
                
                # Wait for Hello and identify
                hello = await self.ws.recv()
                data = json.loads(hello)
                self.heartbeat_interval = data["d"]["heartbeat_interval"]
                
                await self.identify()
                
                # Start tasks
                heartbeat_task = asyncio.create_task(self.send_heartbeat())
                rotate_task = asyncio.create_task(self.rotate_status_loop())
                
                # Handle messages (blocking)
                await self.handle_messages()
                
                # Cleanup
                self.should_run = False
                heartbeat_task.cancel()
                rotate_task.cancel()
                
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass
                try:
                    await rotate_task
                except asyncio.CancelledError:
                    pass
                    
            except Exception as e:
                retry += 1
                wait = min(2 ** retry, 60)
                log(f"Error: {e}", Fore.RED)
                log(f"Retrying in {wait}s...", Fore.YELLOW)
                await asyncio.sleep(wait)


async def main():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
        
    print(f"\n{Fore.LIGHTCYAN_EX}{'='*60}")
    print(f"{Fore.LIGHTGREEN_EX}Discord Status Rotator")
    print(f"{Fore.LIGHTCYAN_EX}{'='*60}\n")
    print(f"{Fore.WHITE}User: {Fore.LIGHTBLUE_EX}{username} {Fore.LIGHTBLACK_EX}({userid})")
    print(f"{Fore.WHITE}Interval: {Fore.LIGHTBLUE_EX}{ROTATE_DELAY}s {Fore.LIGHTBLACK_EX}| Statuses: {len(custom_status_list)}")
    print(f"{Fore.LIGHTCYAN_EX}{'='*60}\n")
    
    client = DiscordClient(usertoken, status)
    await client.connect()


if __name__ == "__main__":
    asyncio.run(main())
