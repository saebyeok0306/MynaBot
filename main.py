import discord, asyncio, json, random, datetime
import sys, os
import data.Database as db
import data.Functions as fun
import data.Logs as logs
from discord.ext import commands, tasks
from dotenv import dotenv_values
from dotenv import load_dotenv

load_dotenv(verbose=True, override=True)

# venv\Scripts\activate
# venv\Scripts\deactivate
# pip freeze > requirements.txt
# .venv$ pip install -r requirements.txt 

# pip install discord.py[voice]

# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# screen -S dc python main.py
# screen -S dc -X quit

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')
status_count = 0
core_list = ['Administrator', 'Command', 'UserRoles', 'Papago', 'ChatGPT', 'Minecraft', 'ArmyCard', 'Profile', 'Youtube', 'TTS']

async def loadCore():
    print("코어모듈을 로드합니다...")
    for filename in os.listdir('core'):
        if filename.endswith('.py'):
            extension_name = filename[:-3]
            if extension_name in core_list:
                await bot.load_extension(f'core.{extension_name}')
                # print(f'{extension_name}가 로드되었습니다.')

@bot.event
async def on_ready():
    print('로그인되었습니다!')
    print(bot.user.name)
    print(bot.user.id)
    print('==============================')
    
    now = datetime.datetime.now()
    nowTime = f"{now.year}.{now.month:02}.{now.day:02} {now.hour:02}:{now.minute:02d}"

    logs.bot_log_channel = 1176773323158458370

    @tasks.loop(seconds=10)
    async def change_status():
        global status_count

        if status_count == 0:
            await bot.change_presence(activity=discord.Game(f"{nowTime}에 부팅됨!"))
        elif status_count == 1:
            await bot.change_presence(activity=discord.Game(f"명령어는 '!도움말'"))
        elif status_count == 2:
            await bot.change_presence(activity=discord.Game(f"{len(bot.guilds)} 서버에 마이나봇이 있음!"))
        else:
            await bot.change_presence(activity=discord.Game(f"{sum(map(lambda x : x.member_count, bot.guilds))} 명이 이용"))

        status_count += 1
        if status_count > 3:
            status_count = 0

    change_status.start()
    await loadCore()

@bot.event
async def on_message(message):
    if message.author.bot: return None

    if message.guild.id == 631471244088311840:
        if random.randint(1, 10) <= 2:
            if message.content.count('ㅋ') >= 2:
                emoji = ['<a:jerry:762198111119605770>','<:dog1:647472178287214593>','<a:SpongeBob3:762542652381069352>','<a:SpongeBob2:762541940914782260>', '<:cat2:671208661997060096>','<:troll2:733561463930749007>','<:troll3:733561496076025866>', '<:cat3:750001125477974106>']
                await message.add_reaction(random.choice(emoji))
            
            elif '캬루' in message.content:
                emoji = ['<:jjag2:740050586828931164>', '<:cat2:745897614708441168>', '<:cat3:750001125477974106>', '<:cat4:750001279014797342>', '<:cat5:750001356709822504>', '<:cat7:750324958554751106>', '<:cat8:753133462642229248>', '<:cat9:753132725107556442>', '<:jjag:739874314324672532>', '<a:jjag3:740055407103574097>']
                await message.add_reaction(random.choice(emoji))
            
        if '몰?루' == message.content or '몰!루' == message.content:
            await message.add_reaction('<a:molu:968521092476051526>')
        elif '아?루' == message.content or '아!루' == message.content:
            await message.add_reaction('<a:aru:968710530376282212>')

    await bot.process_commands(message)

@bot.command(name='로드', aliases=['load'])
async def load_commands(ctx, extension):
    if ctx.message.author.id == 383483844218585108:
        await bot.load_extension(f'core.{extension}')
        await ctx.send(f':white_check_mark: {extension}을(를) 로드했습니다!')

@bot.command(name='언로드', aliases=['unload'])
async def unload_commands(ctx, extension):
    if ctx.message.author.id == 383483844218585108:
        await bot.unload_extension(f'core.{extension}')
        await ctx.send(f':white_check_mark: {extension}을(를) 언로드했습니다!')

@bot.command(name='리로드', aliases=['reload'])
async def reload_commands(ctx, extension=None):
    if ctx.message.author.id == 383483844218585108:
        if extension is None: # extension이 None이면 (그냥 !리로드 라고 썼을 때)
            for filename in os.listdir('core'):
                if filename.endswith('.py'):
                    extension_name = filename[:-3]
                    if extension_name in core_list:
                        try: await bot.unload_extension(f'core.{extension_name}')
                        except: pass
                        await bot.load_extension(f'core.{extension_name}')
                        await ctx.send(f':white_check_mark: {extension_name}을(를) 다시 불러왔습니다!')
        else:
            await bot.unload_extension(f'core.{extension}')
            await bot.load_extension(f'core.{extension}')
            await ctx.send(f':white_check_mark: {extension}을(를) 다시 불러왔습니다!')
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):             return False
    elif isinstance(error, commands.MissingRequiredArgument):   return False
    elif isinstance(error, commands.BadArgument):               return False
    else:
        with open('log/error.txt', 'a', encoding='utf-8') as l:
            now = datetime.datetime.now()
            nowDatetime = "{}-{:02d}-{:02d} {:02d}:{:02d}".format(now.year, now.month, now.day, now.hour, now.minute)
            text = f'user : {ctx.author.name}#{ctx.author.discriminator}\n'
            text += f'cmd : {ctx.message.content}\n'
            text += f'from : {ctx.message.guild.name}.{ctx.message.channel.name}\n'
            text += f'error : {error}\n'
            text += f'date : {nowDatetime}'
            text += f'\n\n'
            l.write(text)
        return True

@bot.event
async def on_member_join(member):
    log_text = f"{member.guild} 서버에 {member.display_name} 님이 가입했습니다. ("
    user_res = db.SaveUserDB(member)
    if user_res: log_text += "유저정보 추가, "
    log_text += ")"

    await logs.SendLog(bot=bot, log_text=log_text)

@bot.event
async def on_member_remove(member):
    log_text = f"{member.guild} 서버에서 {member.display_name} 님이 나갔습니다. ("

    role_res = await db.DeleteRoleServerByAuthor(member)
    if role_res: log_text += f"역할 제거, "
    user_res = db.DeleteUserByAuthor(member)
    if user_res: log_text += f"유저정보 제거, "
    log_text += ")"
    
    await logs.SendLog(bot=bot, log_text=log_text)

if __name__ == '__main__':
    config = dotenv_values(".env")
    bot.run(config['Discord_Token'])