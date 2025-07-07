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
    " If you were to die tomorrow ^_^",
    " I could laugh and jump in from now on ;)",
    " But thinking about the time without us :-(",
    " Makes my heart ache unbearably (╯︵╰,)",
    " Sleepy eyes, pretending to be strong ^_^;",
    " Our voices turn sweet when we embrace (´｡• ᵕ •｡`)",
    " Everything, everything, I want it just for me >w<",
    " It’s so hard, please… (ノ_<。)",
    " You're so unfair, so unfair, so unfair :-(",
    " Beautifully rotten within your selfishness :$",
    " Listen to the punishment, listen, listen (((φ(◎ロ◎;)φ)))",
    " Please, hold me gently, hold me gently ^.^",
    " I know it’s useless, but I want this love to myself :SB-)",
    " If someone else is thinking of you, I’ll crush it >:(",
    " Your likes, dislikes, and your soft hands (o^▽^o)",
    " The way you get mad when your face gets dirty >_<;",
    " I want all of you just for myself ~♥",
    " It hurts… please (つ﹏⊂)",
    " The love in you grew ugly (⚆_⚆)",
    " Listen, listen, listen, please ^_^",
    " Cry out fiercely, cry out fiercely ;-;",
    " I want to do everything, even the things I can’t say (>.<)",
    " Hit me with that cute expression of yours ^.~",
    " Break me… destroy me… >_<",
    " You’re so unfair… already ┐(︶▽︶)┌",
    " Please, hold me gently, again and again (⌒‿⌒)",
    " Break me… break me… you break me… (╯°□°）╯︵ ┻━┻",


    " Tatoeba kimi ga ashita shinu nara (´；д；`)",
    " Boku wa ima kara waratte tobikomeru darou ^_^",
    " Futari igai no jikan o omou to (つ﹏⊂)",
    " Doushiyou mo nai hodo mune ga itakunaru yo ;_;",
    " Nemusou na me tsuyogaru kuse (>_<)",
    " Daki au toki wa amaku naru koe mo (⁄ ⁄•⁄ω⁄•⁄ ⁄)",
    " Zenbu zenbu mou boku dake ga ii ~♥",
    " Kurushii yo onegai (ノ_<。)",
    " Kimi wa zurui zurui zurui hito da mou >:(",
    " Wagamama na kimi no naka de kirei ni kusatta batsu (⚆_⚆)",
    " Kiite kiite kiite kiite kiite kiite yo (((φ(◎ロ◎;)φ)))",
    " Onegai yasashiku daite yasashiku daite (´｡• ᵕ •｡`)",
    " Kono itoshisa o hitorijime shitai yo ^_~",
    " Kimi ga iru nara egao de tsubushite mawarou >:)",
    " Sukoshi marui te mo kawaii (っ´ω`)っ",
    " Chotto okoru tokoro mo suki >_<;",
    " Aijou wa kimi no naka de minikuku sodatta na :-(",
    " Hageshiku naite hageshiku naite (T_T)",
    " Ienai koto mo zenbu shitai yo (つ﹏⊂)",
    " Kawaii sono hyoujou de boku o nagutte (⊃｡•́‿•̀｡)⊃",
    " Kowashite… kimi ga kowashite me >.<"

    
    " Bình yên kia ơi ^.^",
    " Hãy khóc thay cho lòng tôi mỗi khi buồn ;-;",
    " Dẫu chẳng thể mua cho riêng mình một cảm giác _(:з)∠)_",
    " Để lòng mỗi ngày an yên ^_^",
    " Cất bước tìm nơi ấm áp tôi như một ánh sao không nhà (⚆_⚆)",
    " Ở nơi ấy chẳng có vội vã nhìn dòng người đi qua >_<",
    " Bên kia là nắng ^_~",
    " Có than trách ai bao giờ vậy mà ┑(￣Д ￣)┍",
    " Cuộc đời vẫn cứ thế lạnh lùng lướt qua :-(",
    " Yên bình có quá đắt không (((φ(◎ロ◎;)φ)))",
    " Mà sao cơn giông vội vã kéo đến phủ kín nát lòng :(",
    " Ngơ ngác choáng váng vì linh hồn ta hiếu động (•ˋ _ ˊ•)",
    " Về một thế giới mang tên cầu vồng ^.^",
    " Dòng thời gian lặng im thờ ơ :-|",
    " Về ngôi nhà ta muốn thu mình trong màn đêm つ﹏⊂",
    " Bao nhiêu là thêm là bớt cho nỗi niềm găm sâu vào tim (╥﹏╥)",
    " Bình yên ơi sao lại khó tìm >.<",
    " Bình yên ơi sao lại khó tìm đến vậy :-(",

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
