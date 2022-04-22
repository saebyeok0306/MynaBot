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
    token = loaded_data['token2']

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
    game = discord.Game("테스트를 위한 봇입니다.")
    await bot.change_presence(status=discord.Status.online, activity=game)

    fun.getGuilds(bot)

@bot.event
async def on_message(message):
    if message.content.endswith('ㅋ') and message.content.count('ㅋ') >= 3:
        await message.add_reaction('<a:jerry:966960330217521172>')

bot.run(token)