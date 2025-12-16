import os
import sys
import json
import asyncio
import platform
import random
import requests
import websockets
from colorama import init, Fore
# from keep_alive import keep_alive

init(autoreset=True)

status = "idle"  # online / dnd / idle
ROTATE_DELAY = 15  # seconds

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


class DiscordStatusRotator:
    def __init__(self, token, status_type):
        self.token = token
        self.status_type = status_type
        self.ws = None
        self.heartbeat_interval = None
        self.ready = False
        self.session_id = None
        self.status_index = 0
        
    async def send_heartbeat(self):
        """Send heartbeat continuously"""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval / 1000)
                if self.ws and not self.ws.closed:
                    await self.ws.send(json.dumps({"op": 1, "d": self.session_id}))
            except Exception as e:
                print(f"{Fore.RED}[ERROR] Heartbeat: {e}")
                break
    
    async def update_status(self, custom_text):
        """Update Discord status"""
        if not self.ws or self.ws.closed or not self.ready:
            return False
            
        try:
            random_emoji = random.choice(emoji_list)
            payload = {
                "op": 3,
                "d": {
                    "since": 0,
                    "activities": [{
                        "type": 4,
                        "state": custom_text,
                        "name": "Custom Status",
                        "id": "custom",
                        "emoji": {
                            "name": random_emoji["name"],
                            "id": random_emoji["id"],
                            "animated": random_emoji["animated"]
                        }
                    }],
                    "status": self.status_type,
                    "afk": False
                }
            }
            
            await self.ws.send(json.dumps(payload))
            print(f"{Fore.LIGHTGREEN_EX}[✓] Status updated: {custom_text}")
            return True
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Update status: {e}")
            return False
    
    async def rotate_status_loop(self):
        """Continuously rotate status"""
        # Đợi cho READY
        while not self.ready:
            await asyncio.sleep(0.5)
        
        print(f"{Fore.LIGHTCYAN_EX}[*] Starting status rotation (every {ROTATE_DELAY}s)...")
        
        while True:
            try:
                if not self.ready:
                    await asyncio.sleep(1)
                    continue
                
                current_status = custom_status_list[self.status_index % len(custom_status_list)]
                success = await self.update_status(current_status)
                
                if success:
                    self.status_index += 1
                
                await asyncio.sleep(ROTATE_DELAY)
                
            except Exception as e:
                print(f"{Fore.RED}[ERROR] Rotate loop: {e}")
                await asyncio.sleep(5)
    
    async def handle_gateway_events(self):
        """Handle incoming gateway events"""
        try:
            async for message in self.ws:
                if len(message) > 100000:  # Skip large messages
                    continue
                
                try:
                    data = json.loads(message)
                    op = data.get("op")
                    
                    if op == 10:  # Hello
                        self.heartbeat_interval = data["d"]["heartbeat_interval"]
                        print(f"{Fore.LIGHTCYAN_EX}[*] Heartbeat interval: {self.heartbeat_interval}ms")
                        
                    elif op == 0:  # Dispatch
                        event = data.get("t")
                        
                        if event == "READY":
                            self.session_id = data["d"].get("session_id")
                            self.ready = True
                            print(f"{Fore.LIGHTGREEN_EX}[✓] READY! Session ID: {self.session_id[:8]}...")
                            
                        elif event == "RESUMED":
                            self.ready = True
                            print(f"{Fore.LIGHTGREEN_EX}[✓] Session resumed")
                            
                    elif op == 9:  # Invalid Session
                        resumable = data.get("d", False)
                        print(f"{Fore.YELLOW}[!] Invalid session (resumable: {resumable})")
                        self.ready = False
                        await asyncio.sleep(random.uniform(1, 5))
                        # Re-identify
                        await self.identify()
                        
                    elif op == 7:  # Reconnect
                        print(f"{Fore.YELLOW}[!] Server requested reconnect")
                        return
                        
                except json.JSONDecodeError:
                    pass
                    
        except websockets.exceptions.ConnectionClosed as e:
            print(f"{Fore.RED}[ERROR] Connection closed: {e}")
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Gateway events: {e}")
    
    async def identify(self):
        """Send identify payload"""
        identify_payload = {
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
        
        await self.ws.send(json.dumps(identify_payload))
        print(f"{Fore.LIGHTCYAN_EX}[*] Identify sent")
    
    async def connect(self):
        """Connect to Discord Gateway"""
        retry_count = 0
        
        while retry_count < 999:
            try:
                print(f"{Fore.LIGHTCYAN_EX}[*] Connecting to Discord Gateway...")
                
                self.ws = await websockets.connect(
                    "wss://gateway.discord.gg/?v=10&encoding=json",
                    max_size=2 * 1024 * 1024,
                    compression=None
                )
                
                print(f"{Fore.LIGHTGREEN_EX}[✓] Connected!")
                
                # Reset state
                self.ready = False
                self.session_id = None
                retry_count = 0
                
                # Start tasks
                heartbeat_task = asyncio.create_task(self.send_heartbeat())
                rotate_task = asyncio.create_task(self.rotate_status_loop())
                
                # Handle events (blocking)
                await self.handle_gateway_events()
                
                # Cancel tasks when connection closes
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
                retry_count += 1
                wait_time = min(2 ** retry_count, 60)
                print(f"{Fore.RED}[ERROR] {e}")
                print(f"{Fore.YELLOW}[!] Reconnecting in {wait_time}s...")
                await asyncio.sleep(wait_time)


async def main():
    """Main entry point"""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    
    print(f"\n{Fore.LIGHTCYAN_EX}{'='*60}")
    print(f"{Fore.LIGHTGREEN_EX}Discord Status Rotator")
    print(f"{Fore.LIGHTCYAN_EX}{'='*60}\n")
    print(f"{Fore.WHITE}User: {Fore.LIGHTBLUE_EX}{username} {Fore.LIGHTBLACK_EX}({userid})")
    print(f"{Fore.WHITE}Rotation: {Fore.LIGHTBLUE_EX}{ROTATE_DELAY}s {Fore.LIGHTBLACK_EX}| Statuses: {len(custom_status_list)}")
    print(f"{Fore.LIGHTCYAN_EX}{'='*60}\n")
    
    rotator = DiscordStatusRotator(usertoken, status)
    await rotator.connect()


if __name__ == "__main__":
    # keep_alive()
    asyncio.run(main())
