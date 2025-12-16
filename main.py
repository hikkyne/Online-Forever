import os
import sys
import json
import asyncio
import platform
import random
import requests
import websockets
from colorama import init, Fore
from keep_alive import keep_alive  # Chạy nếu dùng Replit hoặc Railway, nếu không dùng thì có thể bỏ dòng này

init(autoreset=True)

status = "idle"  # online / dnd / idle

# Danh sách custom status
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
# Danh sách emoji (cả custom và unicode)
emoji_list = [
    {"name": ":omencatdancespray_valorant_gif_5:", "id": "1098605943777939456", "animated": True},
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

async def onliner(token, status):
    async with websockets.connect("wss://gateway.discord.gg/?v=9&encoding=json") as ws:
        start = json.loads(await ws.recv())
        heartbeat = start["d"]["heartbeat_interval"]

        auth = {
            "op": 2,
            "d": {
                "token": token,
                "properties": {
                    "$os": "Windows 10",
                    "$browser": "Google Chrome",
                    "$device": "Windows",
                },
                "presence": {"status": status, "afk": False},
            },
        }
        await ws.send(json.dumps(auth))

        # Random emoji
        random_emoji = random.choice(emoji_list)
        emoji_payload = (
            random_emoji if random_emoji["id"]
            else {"name": random_emoji["name"]}
        )

        cstatus = {
            "op": 3,
            "d": {
                "since": 0,
                "activities": [
                    {
                        "type": 4,
                        "state": "",
                        "name": "Custom Status",
                        "id": "custom",
                        "emoji": emoji_payload,
                    }
                ],
                "status": status,
                "afk": False,
            },
        }
        await ws.send(json.dumps(cstatus))

        while True:
            await asyncio.sleep(heartbeat / 1000)
            await ws.send(json.dumps({"op": 1, "d": None}))

async def run_onliner():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    print(f"{Fore.WHITE}[{Fore.LIGHTGREEN_EX}+{Fore.WHITE}] Logged in as {Fore.LIGHTBLUE_EX}{username} {Fore.WHITE}({userid})!")
    await onliner(usertoken, status)
    # index = 0
    # while True:
    #     current_status = custom_status_list[index % len(custom_status_list)]
    #     try:
    #         await onliner(usertoken, status, current_status)
    #     except Exception as e:
    #         print(f"{Fore.RED}[ERROR] {e}")
    #     index += 1
    #     await asyncio.sleep(30)  # đổi status mỗi 30 giây

# keep_alive() 
asyncio.run(run_onliner())
