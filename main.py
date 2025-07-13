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
  
  # "(⁄ ⁄•⁄ω⁄•⁄ ⁄) Ooooooooooooooo reeeeeeeeeeeeeee!!!",
  # ">w< Oreoooooooooooooo reeeeeeeeeeeeeee~",
  # "(つ﹏⊂) Oooooo... o re... oooooooooreeeee...",
  # "(⌒‿⌒) Reeeeeeeeeeeeeeeeeeeee ooooooooooo!!",
  # "(⁄ ⁄•⁄ω⁄•⁄ ⁄) Ore? Oooooooooo... reeeeeeeee ;_;",
  # "(≧◡≦) Reeeeeeeee oooooooooo ore oooooooo~",
  # "(°◡°♡) Ore ore ore ore!",
  # "(⁄ ⁄>⁄ω⁄<⁄ ⁄) O re re re re ~",
  # ">///< Ore re o re re o re!",
  # "(⌒ω⌒) Re ore re ore ~",
  # "(づ｡◕‿‿◕｡)づ O re o re ore ore ^_^",
  # ">w< Ore o re o re o re!",
  # "(((o(*ﾟ▽ﾟ*)o))) Oreeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee!!",
  # ">w< Oooooooooooooooooreeeeeeeeeeeeeeeeeee",
  # "(⁄ ⁄•⁄ω⁄•⁄ ⁄) Rere rere rereeeeeee oooooooooooo~",
  # "ヾ(≧▽≦*)o Oooo reee oooo reee ore reeeee ooooo!",
  # "(((φ(◎ロ◎;)φ))) Oooooooooooooooooooooooooooooooo reeeeeeeeeeeeeee!",
  # "(;´༎ຶД༎ຶ`) Ore? Re? Oooooooo... reeeeeee...",
  # "(⁄ ⁄>⁄ω⁄<⁄ ⁄) O re o re ooooooo reeeeeee ooooooo reeeee",
  # "(•́ ͜ʖ •̀) Just a lil ooooooooooo reeeeeeeeeeeee for your soul",
  # "(＾◡＾)っ Ore reeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee!! ooooooo!!",
  # "(*≧ω≦) Reeeeeeeeeeeeeeeeeee ooooooooooooooo ore oreeeee!!",
  # "(°ロ°)☝ Re re ore re, ore re?",
  # "ಥ‿ಥ Ore... o re... ore re...",
  # "( ´•̥̥̥ω•̥̥̥` ) Re ore o re, ore re re",
  # "(つ﹏⊂) Ore re... o re...",
  # "(☆▽☆) Ore ore, re re, ore o re!",
  # ">w< O re! Ore? Re re!!",
  # "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ Ore o re ore re o re re!",
  # "(｡•́︿•̀｡) Re... o re re... ore ore...",
  # "(⌒‿⌒) Ore re ore re ore re ore re",
  # "(*≧▽≦) Ooooooooooooore oooooooooooore reeeee~",
  # "(｡♥‿♥｡) Ore ore oreeeeeeeeeeeeeeeeeeeeeee",
  # "(╯°□°）╯︵ ┻━┻ Ooooooo reee ooooooo reee ooooooo",
  # "ヽ(；▽；)ノ Reeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee!",
  # "(灬º‿º灬) Oooooo reeeee oreeeeeeee~",
  # "(╯°□°）╯︵ ┻━┻ Ore re?! Ore ore re re!!",
  # "(⁄ ⁄•⁄ω⁄•⁄ ⁄) Re ore re ore... o re!",
  # "(°◡°♡) Ore, o re, re ore, ore re",
  # "(ﾉ≧ڡ≦) Re o re o re ore o re o re re!!",
 #   "(⁄ ⁄•⁄ω⁄•⁄ ⁄) Your morning eyes, I could stare like watching stars",
 #  "(•́ ͜ʖ •̀) u i i a i i i a a i i",

 #  ">w< I could walk you by, and I'll tell without a thought",
 #  "(⌒‿⌒) u i u i i a u a i i",

 #  "(つ﹏⊂) You'd be mine, would you mind if I took your hand tonight?",
 #  "(＾◡＾)っ o re u i i a o re u i a",

 #  "(⌒‿⌒) Know you're all that I want this life",
 #  "(☆▽☆) i i i a i i u i a a",
 # " ₍^. .^₎⟆  ♪  u i ii a",
 #  "(≧◡≦) I'll imagine we fell in love",
 #  "(⁄ ⁄•⁄ω⁄•⁄ ⁄) u i u i a u i i i a a",

 #  "(°◡°♡) I'll nap under moonlight skies with you",
 #  "(｡•́︿•̀｡) i a i a u u i a i i",

 #  "(⁄ ⁄>⁄ω⁄<⁄ ⁄) I think I'll picture us, you with the waves",
 #  "(つ﹏⊂) a u i i o re o re i i a",

 #  "(⌒ω⌒) The ocean's colors on your face",
 #  "(•́ ͜ʖ •̀) u i u i i a i u i a",

 #  "(づ｡◕‿‿◕｡)づ I'll leave my heart with your air",
 #  "(((o(*ﾟ▽ﾟ*)o))) o re o re u i a a a i i",

 #  ">w< So let me fly with you",
 #  "(´｡• ω •｡`) u u i a i i i a o re",

 #  "(((o(*ﾟ▽ﾟ*)o))) Will you be forever with me?",
 #  "(⌒‿⌒) u i a i u i i a i a",

 #  " ₍^. .^₎⟆  ♪  u i ii a",
 #  "(;´༎ຶД༎ຶ`) My love will always stay by you",
 #  "(｡•́︿•̀｡) i i i a u i a u a i",

 #  "(•́ ͜ʖ •̀) I'll keep it safe, so don't you worry a thing",
 #  "(つ﹏⊂) o re u i u i a o o a i a",

 #  "(＾◡＾)っ I'll tell you I love you more",
 #  "(⁄ ⁄•⁄ω⁄•⁄ ⁄) a a u i i a i i a u",

 #  "(*≧ω≦) It's stuck with you forever, so promise you won't let it go",
 #  "(☆▽☆) u i a i u i u i a i i a",

 #  "(°ロ°)☝ I'll trust the universe will always bring me to you",
 #  "(⌒ω⌒) u i o re u i u i a o re a",

 # " ₍^. .^₎⟆  ♪  u i ii a",
 #  "ಥ‿ಥ I'll imagine we fell in love",
 #  "(•́ ͜ʖ •̀) u i u i u i i a i i",

 #  "( ´•̥̥̥ω•̥̥̥` ) I'll nap under moonlight skies with you",
 #  "(≧◡≦) u u a i i o re o re i i",

 #  "(☆▽☆) I think I'll picture us, you with the waves",
 #  "(づ｡◕‿‿◕｡) a i i u i a o re u u i",

 #  ">w< The ocean's colors on your face",
 #  "(＾◡＾)っ u i a i u u u i a i",

 #  "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ I'll leave my heart with your air",
 #  "(つ﹏⊂) i a i a i a o re i i",

 #  "(｡•́︿•̀｡) So let me fly with you",
 #  "(⁄ ⁄>⁄ω⁄<⁄ ⁄) o re o re u i u i a a",
 # " ₍^. .^₎⟆  ♪  u i ii a",
 #  "(•́ ͜ʖ •̀) Will you be forever with me?",
 #  "(•́ ͜ʖ •̀) a i u i i a i i a u i",
]
# custom_status_list = [
#     " If you were to die tomorrow ^_^",
#     " I could laugh and jump in from now on ;)",
#     " But thinking about the time without us :-(",
#     " Makes my heart ache unbearably (╯︵╰,)",
#     " Sleepy eyes, pretending to be strong ^_^;",
#     " Our voices turn sweet when we embrace (´｡• ᵕ •｡)",
#     " Everything, everything, I want it just for me >w<",
#     " It’s so hard, please… (ノ_<。)",
#     " You're so unfair, so unfair, so unfair :-(",
#     " Beautifully rotten within your selfishness :$",
#     " Listen to the punishment, listen, listen (((φ(◎ロ◎;)φ)))",
#     " Please, hold me gently, hold me gently ^.^",
#     " I know it’s useless, but I want this love to myself :SB-)",
#     " If someone else is thinking of you, I’ll crush it >:(",
#     " Your likes, dislikes, and your soft hands (o^▽^o)",
#     " The way you get mad when your face gets dirty >_<;",
#     " I want all of you just for myself ~♥",
#     " It hurts… please (つ﹏⊂)",
#     " The love in you grew ugly (⚆_⚆)",
#     " Listen, listen, listen, please ^_^",
#     " Cry out fiercely, cry out fiercely ;-;",
#     " I want to do everything, even the things I can’t say (>.<)",
#     " Hit me with that cute expression of yours ^.~",
#     " Break me… destroy me… >_<",
#     " You’re so unfair… already ┐(︶▽︶)┌",
#     " Please, hold me gently, again and again (⌒‿⌒)",
#     " Break me… break me… you break me… (╯°□°）╯︵ ┻━┻",


#     " Tatoeba kimi ga ashita shinu nara (´；д；)",
#     " Boku wa ima kara waratte tobikomeru darou ^_^",
#     " Futari igai no jikan o omou to (つ﹏⊂)",
#     " Doushiyou mo nai hodo mune ga itakunaru yo ;_;",
#     " Nemusou na me tsuyogaru kuse (>_<)",
#     " Daki au toki wa amaku naru koe mo (⁄ ⁄•⁄ω⁄•⁄ ⁄)",
#     " Zenbu zenbu mou boku dake ga ii ~♥",
#     " Kurushii yo onegai (ノ_<。)",
#     " Kimi wa zurui zurui zurui hito da mou >:(",
#     " Wagamama na kimi no naka de kirei ni kusatta batsu (⚆_⚆)",
#     " Kiite kiite kiite kiite kiite kiite yo (((φ(◎ロ◎;)φ)))",
#     " Onegai yasashiku daite yasashiku daite (´｡• ᵕ •｡)",
#     " Kono itoshisa o hitorijime shitai yo ^_~",
#     " Kimi ga iru nara egao de tsubushite mawarou >:)",
#     " Sukoshi marui te mo kawaii (っ´ω)っ",
#     " Chotto okoru tokoro mo suki >_<;",
#     " Aijou wa kimi no naka de minikuku sodatta na :-(",
#     " Hageshiku naite hageshiku naite (T_T)",
#     " Ienai koto mo zenbu shitai yo (つ﹏⊂)",
#     " Kawaii sono hyoujou de boku o nagutte (⊃｡•́‿•̀｡)⊃",
#     " Kowashite… kimi ga kowashite me >.<",

    
#     " Bình yên kia ơi ^.^",
#     " Hãy khóc thay cho lòng tôi mỗi khi buồn ;-;",
#     " Dẫu chẳng thể mua cho riêng mình một cảm giác _(:з)∠)_",
#     " Để lòng mỗi ngày an yên ^_^",
#     " Cất bước tìm nơi ấm áp tôi như một ánh sao không nhà (⚆_⚆)",
#     " Ở nơi ấy chẳng có vội vã nhìn dòng người đi qua >_<",
#     " Bên kia là nắng ^_~",
#     " Có than trách ai bao giờ vậy mà ┑(￣Д ￣)┍",
#     " Cuộc đời vẫn cứ thế lạnh lùng lướt qua :-(",
#     " Yên bình có quá đắt không (((φ(◎ロ◎;)φ)))",
#     " Mà sao cơn giông vội vã kéo đến phủ kín nát lòng :(",
#     " Ngơ ngác choáng váng vì linh hồn ta hiếu động (•ˋ _ ˊ•)",
#     " Về một thế giới mang tên cầu vồng ^.^",
#     " Dòng thời gian lặng im thờ ơ :-|",
#     " Về ngôi nhà ta muốn thu mình trong màn đêm つ﹏⊂",
#     " Bao nhiêu là thêm là bớt cho nỗi niềm găm sâu vào tim (╥﹏╥)",
#     " Bình yên ơi sao lại khó tìm >.<",
#     " Bình yên ơi sao lại khó tìm đến vậy :-(",

# ]

# Danh sách emoji (cả custom và unicode)
emoji_list = [
    {"name": ":Omen_Cool:", "id": "1159446145601388614", "animated": False},
    {"name": ":Omen_Drink:", "id": "1159446161225171035", "animated": False},
    {"name": ":Omen_Gun:", "id": "1159446167369809971", "animated": False},
    {"name": ":Omen_Laugh:", "id": "1159446172663025674", "animated": False},
    {"name": ":pnv_vlromen:", "id": "1030578509493571655", "animated": False},
    {"name": ":Omen_Rage:", "id": "1159446183090065438", "animated": False},
    {"name": ":omencatdancespray_valorant_gif_5:", "id": "1098605943777939456", "animated": True},
    {"name": ":OwOmen:", "id": "938763834057961492", "animated": False},
    {"name": ":pepeomen:", "id": "938761185820561419", "animated": False},
    {"name": ":meguuusad:", "id": "795804879402565726", "animated": False},
    {"name": ":bocchisad:", "id": "636320419305095199", "animated": False},
      {"name": ":amuugu:", "id": "590941044724596757", "animated": True},
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

    index = 0
    while True:
        current_status = custom_status_list[index % len(custom_status_list)]
        try:
            await onliner(usertoken, status, current_status)
        except Exception as e:
            print(f"{Fore.RED}[ERROR] {e}")
        index += 1
        await asyncio.sleep(30)  # đổi status mỗi 30 giây

# keep_alive()  # Nếu không dùng host cần keep-alive (như Replit), bạn có thể comment dòng này
asyncio.run(run_onliner())
