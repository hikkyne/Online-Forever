import os
import sys
import json
import asyncio
import websockets
from colorama import init, Fore

init(autoreset=True)

# ===== CONFIGURATION FROM ENVIRONMENT VARIABLES =====
# Get token from environment (REQUIRED)
usertoken = os.getenv("TOKEN")
if not usertoken:
    print(f"{Fore.WHITE}[{Fore.RED}-{Fore.WHITE}] TOKEN environment variable not set.")
    sys.exit(1)

# Status configuration (with defaults)
STATUS = os.getenv("STATUS", "idle")  # online/dnd/idle
CUSTOM_STATUS_TEXT = os.getenv("CUSTOM_STATUS_TEXT", "")

# Emoji configuration (with defaults)
EMOJI_ID = os.getenv("EMOJI_ID", "1368069418428665958")
EMOJI_NAME = os.getenv("EMOJI_NAME", ":aPeepo_Sleep:")
EMOJI_ANIMATED = os.getenv("EMOJI_ANIMATED", "true").lower() in ("true", "1", "yes")


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
    print(f"\n{Fore.LIGHTCYAN_EX}{'='*60}")
    print(f"{Fore.LIGHTGREEN_EX}Discord Status Bot")
    print(f"{Fore.LIGHTCYAN_EX}{'='*60}\n")
    print(f"{Fore.WHITE}Status: {Fore.LIGHTBLUE_EX}{STATUS}")
    print(f"{Fore.WHITE}Custom Status: {Fore.LIGHTBLUE_EX}{CUSTOM_STATUS_TEXT}")
    print(f"{Fore.WHITE}Emoji: {Fore.LIGHTBLUE_EX}{EMOJI_NAME} (ID: {EMOJI_ID})")
    print(f"{Fore.WHITE}Animated: {Fore.LIGHTBLUE_EX}{EMOJI_ANIMATED}")
    print(f"{Fore.LIGHTCYAN_EX}{'='*60}\n")
    
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
