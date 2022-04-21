import discord, asyncio, json
import sys, os
import data.Functions as fun
from discord.ext import commands


# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)
token = ''
with open("data/token.json", "r") as f:
    loaded_data = json.load(f)  # 데이터 로드하기
    token = loaded_data['token']

for filename in os.listdir('core'):
    if filename.endswith(".py"):
        bot.load_extension(f"core.{filename[:-3]}")
        print(f"{filename[:-3]}가 로드되었습니다.")

@bot.event
async def on_ready():
    print('로그인되었습니다!')
    print(bot.user.name)
    print(bot.user.id)
    print('==============================')
    game = discord.Game("명령어는 [!도움말] 참고")
    await bot.change_presence(status=discord.Status.online, activity=game)

    fun.getGuilds(bot)


bot.run(token)