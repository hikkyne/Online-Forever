import os
import sys
import json
import asyncio
import websockets
from colorama import init, Fore

init(autoreset=True)

# Configuration
STATUS = "idle"  # online/dnd/idle
CUSTOM_STATUS_TEXT = "zzzz"
EMOJI_ID = "1368069418428665958"
EMOJI_NAME = ":aPeepo_Sleep:"
EMOJI_ANIMATED = True

# Get token from environment
usertoken = os.getenv("TOKEN")
if not usertoken:
    print(f"{Fore.WHITE}[{Fore.RED}-{Fore.WHITE}] TOKEN environment variable not set.")
    sys.exit(1)

headers = {"Authorization": usertoken, "Content-Type": "application/json"}


async def maintain_presence(token, status):
    """Maintain Discord presence via WebSocket connection."""
    uri = "wss://gateway.discord.gg/?v=9&encoding=json"
    
    try:
        async with websockets.connect(uri) as ws:
            # Receive HELLO event
            hello_event = json.loads(await ws.recv())
            heartbeat_interval = hello_event["d"]["heartbeat_interval"]
            
            # Send IDENTIFY payload
            identify_payload = {
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {
                        "$os": "linux",
                        "$browser": "discord.py",
                        "$device": "discord.py",
                    },
                    "presence": {
                        "status": status,
                        "afk": False
                    },
                },
            }
            await ws.send(json.dumps(identify_payload))
            
            # Send PRESENCE UPDATE with custom status and emoji
            presence_payload = {
                "op": 3,
                "d": {
                    "since": 0,
                    "activities": [
                        {
                            "type": 4,
                            "state": CUSTOM_STATUS_TEXT,
                            "name": "Custom Status",
                            "id": "custom",
                            "emoji": {
                                "name": EMOJI_NAME,
                                "id": EMOJI_ID,
                                "animated": EMOJI_ANIMATED,
                            },
                        }
                    ],
                    "status": status,
                    "afk": False,
                },
            }
            await ws.send(json.dumps(presence_payload))
            
            # Send initial heartbeat
            heartbeat_payload = {"op": 1, "d": None}
            await asyncio.sleep(heartbeat_interval / 1000)
            await ws.send(json.dumps(heartbeat_payload))
            
            print(f"{Fore.WHITE}[{Fore.LIGHTGREEN_EX}+{Fore.WHITE}] Presence updated successfully!")
            
            # Keep connection alive with heartbeats
            while True:
                await asyncio.sleep(heartbeat_interval / 1000)
                await ws.send(json.dumps(heartbeat_payload))
                
    except websockets.exceptions.ConnectionClosed:
        print(f"{Fore.WHITE}[{Fore.YELLOW}!{Fore.WHITE}] Connection closed, reconnecting...")
        raise
    except Exception as e:
        print(f"{Fore.WHITE}[{Fore.RED}-{Fore.WHITE}] Error: {e}")
        raise


async def main():
    """Main loop with auto-reconnect."""
    print(f"{Fore.WHITE}[{Fore.LIGHTGREEN_EX}+{Fore.WHITE}] Discord Status Bot Started")
    print(f"{Fore.WHITE}[{Fore.LIGHTBLUE_EX}*{Fore.WHITE}] Status: {STATUS}")
    print(f"{Fore.WHITE}[{Fore.LIGHTBLUE_EX}*{Fore.WHITE}] Custom Status: {CUSTOM_STATUS_TEXT}")
    
    while True:
        try:
            await maintain_presence(usertoken, STATUS)
        except Exception as e:
            print(f"{Fore.WHITE}[{Fore.YELLOW}!{Fore.WHITE}] Reconnecting in 5 seconds...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.WHITE}[{Fore.LIGHTGREEN_EX}+{Fore.WHITE}] Bot stopped gracefully.")
        sys.exit(0)
