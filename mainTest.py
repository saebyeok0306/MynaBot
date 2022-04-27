import discord, asyncio, json, datetime
import sys, os
import data.Functions as fun
from discord.ext import commands


# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

intents = discord.Intents.all()
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


@bot.command(name='로드', aliases=['load'])
async def load_commands(ctx, extension):
    if ctx.message.author.guild_permissions.administrator:
        bot.load_extension(f'core.{extension}')
        await ctx.send(f':white_check_mark: {extension}을(를) 로드했습니다!')

@bot.command(name='언로드', aliases=['unload'])
async def unload_commands(ctx, extension):
    if ctx.message.author.guild_permissions.administrator:
        bot.unload_extension(f'core.{extension}')
        await ctx.send(f':white_check_mark: {extension}을(를) 언로드했습니다!')

@bot.command(name='리로드', aliases=['reload'])
async def reload_commands(ctx, extension=None):
    if ctx.message.author.guild_permissions.administrator:
        if extension is None: # extension이 None이면 (그냥 !리로드 라고 썼을 때)
            for filename in os.listdir('core'):
                if filename.endswith('.py'):
                    extensionName = filename[:-3]
                    try: bot.unload_extension(f'core.{extensionName}')
                    except: pass
                    bot.load_extension(f'core.{extensionName}')
                    await ctx.send(f':white_check_mark: {extensionName}을(를) 다시 불러왔습니다!')
        else:
            bot.unload_extension(f'core.{extension}')
            bot.load_extension(f'core.{extension}')
            await ctx.send(f':white_check_mark: {extension}을(를) 다시 불러왔습니다!')
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):             return
    elif isinstance(error, commands.MissingRequiredArgument):   return
    elif isinstance(error, commands.BadArgument):               return
    else:
        with open('log/error.txt', 'a', encoding='utf-8') as l:
            now = datetime.datetime.now()
            nowDatetime = "{}-{:02d}-{:02d} {:02d}:{:02d}".format(now.year, now.month, now.day, now.hour, now.minute)
            text = f'user : {ctx.author.name}#{ctx.author.discriminator}\n'
            text += f'cmd : {ctx.message.content} from {ctx.message.guild.name}.{ctx.message.channel.name}\n'
            text += f'error : {error}\n'
            text += f'date : {nowDatetime}'
            text += f'\n\n'
            l.write(text)
        
        # embed = discord.Embed(title='Error', description='오류가 발생했습니다.', color=0xFF0000)
        # embed.add_field(name='상세내용', value=f'```{error}```')
        # await ctx.send(embed=embed)


@bot.event
async def on_member_remove(member):
    await fun.deleteUserRole(member.guild, member) # delete role
    fun.removeUserDB(member.id) # db에서 데이터 삭제

bot.run(token)