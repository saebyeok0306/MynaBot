import discord, asyncio, json, datetime
import sys, os
import data.Database as db
import data.Functions as fun
import data.Logs as logs
from discord.ext import commands, tasks
from dotenv import dotenv_values
from dotenv import load_dotenv

load_dotenv(verbose=True, override=True)


# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
# screen -S dc python3 main.py
# screen -S dc -X quit

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!!', intents=intents)
status_count = 0
core_list = ['Administrator', 'Command', 'ColorName', 'Papago', 'ChatGPT', 'ArmyCard', 'Profile', 'Youtube', 'TTS', 'Message']

async def loadCore():
    print("코어모듈을 로드합니다...")
    for filename in os.listdir('core'):
        if filename.endswith('.py'):
            extensionName = filename[:-3]
            if extensionName in core_list:
                await bot.load_extension(f'core.{extensionName}')


@bot.event
async def on_ready():
    print('로그인되었습니다!')
    print(bot.user.name)
    print(bot.user.id)
    print('==============================')
    
    now = datetime.datetime.now()
    nowTime = f"{now.year}.{now.month:02}.{now.day:02} {now.hour:02}:{now.minute:02d}"

    logs.bot_log_channel = 1177975720111259739

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

    for guild in bot.guilds:
        db.SaveUserDBAtGuild(guild)

@bot.event
async def on_message(message):
    if message.author.bot: return None

    # await on_message_tts(message)

    await bot.process_commands(message)


@bot.command(name='로드', aliases=['load'])
async def load_commands(ctx, extension):
    if ctx.message.author.guild_permissions.administrator:
        await bot.load_extension(f'core.{extension}')
        await ctx.send(f':white_check_mark: {extension}을(를) 로드했습니다!')

@bot.command(name='언로드', aliases=['unload'])
async def unload_commands(ctx, extension):
    if ctx.message.author.guild_permissions.administrator:
        await bot.unload_extension(f'core.{extension}')
        await ctx.send(f':white_check_mark: {extension}을(를) 언로드했습니다!')

@bot.command(name='리로드', aliases=['reload'])
async def reload_commands(ctx, extension=None):
    if ctx.message.author.guild_permissions.administrator:
        if extension is None: # extension이 None이면 (그냥 !리로드 라고 썼을 때)
            for filename in os.listdir('core'):
                if filename.endswith('.py'):
                    extensionName = filename[:-3]
                    if extensionName in coreList:
                        try: await bot.unload_extension(f'core.{extensionName}')
                        except: pass
                        await bot.load_extension(f'core.{extensionName}')
                        await ctx.send(f':white_check_mark: {extensionName}을(를) 다시 불러왔습니다!')
        else:
            await bot.unload_extension(f'core.{extension}')
            await bot.load_extension(f'core.{extension}')
            await ctx.send(f':white_check_mark: {extension}을(를) 다시 불러왔습니다!')
    
# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.CommandNotFound):             return
#     elif isinstance(error, commands.MissingRequiredArgument):   return
#     elif isinstance(error, commands.BadArgument):               return
#     else:
#         with open('log/error.txt', 'a', encoding='utf-8') as l:
#             now = datetime.datetime.now()
#             nowDatetime = "{}-{:02d}-{:02d} {:02d}:{:02d}".format(now.year, now.month, now.day, now.hour, now.minute)
#             text = f'user : {ctx.author.name}#{ctx.author.discriminator}\n'
#             text += f'cmd : {ctx.message.content} from {ctx.message.guild.name}.{ctx.message.channel.name}\n'
#             text += f'error : {error}\n'
#             text += f'date : {nowDatetime}'
#             text += f'\n\n'
#             l.write(text)

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
    bot.run(config['Discord_Token2'])