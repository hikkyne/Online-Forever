import os
import json
import asyncio
import platform
import random
import requests
import websockets
from colorama import init, Fore

init(autoreset=True)

status = "idle"  # online / dnd / idle
ROTATE_DELAY = 30  # seconds

custom_status_list = [
  "(✿˘︶˘)♡ Your morning eyes, I could stare like watching stars",
  "(⌒‿⌒) u i a i i a o re i a a",

  ">w< I could walk you by, and I'll tell without a thought",
  "(⌒‿⌒) u i u i i a u a i i",

  "(つ﹏⊂) You'd be mine, would you mind if I took your hand tonight?",
  "(＾◡＾)っ o re u i i a o re u i a",

  "(⌒‿⌒) Know you're all that I want this life",
  "(☆▽☆) i i i a i i u i a a",

  " ₍^. .^₎⟆  ♪  u i ii a",

  "(≧◡≦) I'll imagine we fell in love",
  "(⁄ ⁄•⁄ω⁄•⁄ ⁄) u i u i a u i i i a a",

  "(°◡°♡) I'll nap under moonlight skies with you",
  "(｡•́︿•̀｡) i a i a u u i a i i",

  "(⁄ ⁄>⁄ω⁄<⁄ ⁄) I think I'll picture us, you with the waves",
  "(つ﹏⊂) a u i i o re o re i i a",

  "(⌒ω⌒) The ocean's colors on your face",
  "(•́ ͜ʖ •̀) u i u i i a i u i a",

  "(づ｡◕‿‿◕｡)づ I'll leave my heart with your air",
  "(((o(*ﾟ▽ﾟ*)o))) o re o re u i a a a i i",

  ">w< So let me fly with you",
  "(´｡• ω •｡`) u u i a i i i a o re",

  "(((o(*ﾟ▽ﾟ*)o))) Will you be forever with me?",
  "(⌒‿⌒) u i a i u i i a i a",

  " ₍^. .^₎⟆  ♪  u i ii a",

  "(;´༎ຶД༎ຶ`) My love will always stay by you",
  "(｡•́︿•̀｡) i i i a u i a u a i",

  "(•́ ͜ʖ •̀) I'll keep it safe, so don't you worry a thing",
  "(つ﹏⊂) o re u i u i a o o a i a",

  "(＾◡＾)っ I'll tell you I love you more",
  "(⁄ ⁄•⁄ω⁄•⁄ ⁄) a a u i i a i i a u",

  "(*≧ω≦) It's stuck with you forever, so promise you won't let it go",
  "(☆▽☆) u i a i u i u i a i i a",

  "(°ロ°)☝ I'll trust the universe will always bring me to you",
  "(⌒ω⌒) u i o re u i u i a o re a",

  " ₍^. .^₎⟆  ♪  u i ii a",

  "ಥ‿ಥ I'll imagine we fell in love",
  "(•́ ͜ʖ •̀) u i u i u i i a i i",

  "( ´•̥̥̥ω•̥̥̥` ) I'll nap under moonlight skies with you",
  "(≧◡≦) u u a i i o re o re i i",

  "(☆▽☆) I think I'll picture us, you with the waves",
  "(づ｡◕‿‿◕｡) a i i u i a o re u u i",

  ">w< The ocean's colors on your face",
  "(＾◡＾)っ u i a i u u u i a i",

  "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ I'll leave my heart with your air",
  "(つ﹏⊂) i a i a i a o re i i",

  "(｡•́︿•̀｡) So let me fly with you",
  "(⁄ ⁄>⁄ω⁄<⁄ ⁄) o re o re u i u i a a",

  " ₍^. .^₎⟆  ♪  u i ii a",

  "(•́ ͜ʖ •̀) Will you be forever with me?",
  "(•́ ͜ʖ •̀) a i u i i a i i a u i",
]

emoji_list = [
    {"name": "omencatdancespray_valorant_gif_5", "id": "1098605943777939456", "animated": True},
]

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("Missing TOKEN")
    exit()

headers = {"Authorization": TOKEN}
r = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
user = r.json()
username = user["username"]
userid = user["id"]

async def heartbeat(ws, interval):
    while True:
        await asyncio.sleep(interval / 1000)
        try:
            await ws.send(json.dumps({"op": 1, "d": None}))
        except:
            break

async def rotate_status(ws):
    index = 0
    while True:
        lyric = custom_status_list[index % len(custom_status_list)]
        emoji = random.choice(emoji_list)

        payload = {
            "op": 3,
            "d": {
                "since": 0,
                "activities": [{
                    "type": 4,
                    "name": "Custom Status",
                    "state": lyric,
                    "emoji": emoji
                }],
                "status": status,
                "afk": False
            }
        }

        await ws.send(json.dumps(payload))
        index += 1
        await asyncio.sleep(ROTATE_DELAY)

async def main():
    os.system("cls" if platform.system() == "Windows" else "clear")
    print(f"{Fore.GREEN}[+] Logged in as {username} ({userid})")

    async with websockets.connect(
        "wss://gateway.discord.gg/?v=9&encoding=json",
        max_size=2**20
    ) as ws:

        hello = json.loads(await ws.recv())
        interval = hello["d"]["heartbeat_interval"]

        identify = {
            "op": 2,
            "d": {
                "token": TOKEN,
                "intents": 0,
                "properties": {
                    "$os": "windows",
                    "$browser": "chrome",
                    "$device": "pc"
                },
                "presence": {
                    "status": status,
                    "afk": False
                }
            }
        }
        await ws.send(json.dumps(identify))

        asyncio.create_task(heartbeat(ws, interval))
        asyncio.create_task(rotate_status(ws))

        while True:
            await ws.recv()  # giữ socket sống

asyncio.run(main())
