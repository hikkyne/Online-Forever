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
    "Ví dụ như nếu ngày mai em chết đi",
    "Thì ngay bây giờ anh cũng có thể mỉm cười lao theo",
    "Chỉ cần nghĩ đến khoảng thời gian không có em",
    "Là lồng ngực anh đau đớn đến mức không chịu nổi",
    "Đôi mắt lúc buồn ngủ, thói quen hay tỏ ra mạnh mẽ",
    "Cả giọng nói ngọt ngào khi ôm nhau",
    "Tất cả, tất cả... anh chỉ muốn là người duy nhất có được em",
    "Anh đau lắm, xin em đấy",
    "Em thật tàn nhẫn... tàn nhẫn... tàn nhẫn quá rồi",
    "Sự trừng phạt đã thối rữa một cách đẹp đẽ bên trong con người ích kỷ của em",
    "Nghe anh đi, nghe anh đi, nghe anh đi...",
    "Làm ơn hãy ôm anh thật dịu dàng, ôm anh thật dịu dàng...",
    "Dù anh biết là chuyện này chẳng thể nào",
    "Nhưng anh vẫn muốn giữ trọn tình yêu này cho riêng mình",
    "Nếu trong đầu ai khác có hình bóng em",
    "Anh sẽ nở nụ cười và nghiền nát tất cả",
    "Cả thích lẫn ghét, cả đôi bàn tay có phần tròn trịa",
    "Và cả lúc em nổi giận khi mặt bị làm bẩn",
    "Tất cả, tất cả... chỉ cần là của riêng anh thôi",
    "Anh đau lắm, xin em đấy",
    "Em thật tàn nhẫn... tàn nhẫn... tàn nhẫn quá rồi",
    "Tình yêu đã trở nên méo mó và xấu xí trong em mất rồi",
    "Nghe anh đi, nghe anh đi, nghe anh đi...",
    "Làm ơn hãy khóc thật nhiều, khóc thật nhiều cho anh...",
    "Những ảo tưởng và ham muốn không phanh lại được nữa",
    "Anh muốn làm tất cả những điều không thể nói ra",
    "Dùng khuôn mặt dễ thương đó mà đánh anh đi",
    "Phá hủy anh đi",
    "Em thật tàn nhẫn... tàn nhẫn... tàn nhẫn quá rồi",
    "Sự trừng phạt đã thối rữa một cách đẹp đẽ bên trong con người ích kỷ của em",
    "Nghe anh đi, nghe anh đi, nghe anh đi...",
    "Làm ơn hãy ôm anh thật dịu dàng, ôm anh thật dịu dàng...",
    "Hãy phá hủy anh đi, phá hủy anh đi, phá hủy anh đi, phá hủy anh đi",
    "Phá hủy anh đi, phá hủy anh đi, phá hủy anh đi, chính em hãy phá hủy anh đi"
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
