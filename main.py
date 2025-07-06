import os
import sys
import json
import asyncio
import platform
import requests
import websockets
from colorama import init, Fore
from keep_alive import keep_alive

init(autoreset=True)

status = "idle"  # online/dnd/idle
custom_status_list = [
    "Bình yên kia ơi",
    "Hãy khóc thay cho lòng tôi mỗi khi buồn",
    "Dẫu chẳng thể mua cho riêng mình một cảm giác",
    "Để lòng mỗi ngày an yên",
    "Cất bước tìm nơi ấm áp tôi như một ánh sao không nhà",
    "Ở nơi ấy chẳng có vội vã nhìn dòng người đi qua",
    "Bên kia là nắng",
    "Có than trách ai bao giờ vậy mà",
    "Cuộc đời vẫn cứ thế lạnh lùng lướt qua",
    "Yên bình có quá đắt không",
    "Mà sao cơn giông vội vã kéo đến phủ kín nát lòng",
    "Ngơ ngác choáng váng vì linh hồn ta hiếu động",
    "Về một thế giới mang tên cầu vồng",
    "Dòng thời gian lặng im thờ ơ",
    "Về ngôi nhà ta muốn thu mình trong màn đêm",
    "Bao nhiêu là thêm là bớt cho nỗi niềm găm sâu vào tim",
    "Bình yên ơi sao lại khó tìm",
    "Bên kia là nắng",
    "Có than trách ai bao giờ vậy mà",
    "Cuộc đời vẫn cứ thế lạnh lùng lướt qua",
    "Yên bình có quá đắt không mà sao",
    "Cơn giông vội vã kéo đến phủ kín nát lòng",
    "Ngơ ngác",
    "Choáng váng vì linh hồn ta hiếu động",
    "Về một thế giới mang tên cầu vồng",
    "Dòng thời gian lặng im",
    "Thờ ơ về ngôi nhà ta muốn thu mình trong màn đêm",
    "Bao nhiêu là thêm là bớt cho nỗi niềm găm sâu vào tim",
    "Bình yên ơi sao lại khó tìm",
    "Bình yên ơi sao lại khó tìm đến vậy"
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

userinfo = requests.get("https://canary.discordapp.com/api/v9/users/@me", headers=headers).json()
username = userinfo["username"]
userid = userinfo["id"]

async def onliner(token, status, custom_status):
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

        cstatus = {
            "op": 3,
            "d": {
                "since": 0,
                "activities": [
                    {
                        "type": 4,
                        "state": custom_status,
                        "name": "Custom Status",
                        "id": "custom",
                        "emoji": {
                            "name": ":Omen_Cry:",
                            "id": "1159446150747783188",
                            "animated": False,
                        },
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

    index = 0
    while True:
        current_status = custom_status_list[index % len(custom_status_list)]
        try:
            await onliner(usertoken, status, current_status)
        except Exception as e:
            print(f"{Fore.RED}[ERROR] {e}")
        index += 1
        await asyncio.sleep(30)  # Thay đổi trạng thái mỗi 30 giây

keep_alive()
asyncio.run(run_onliner())
