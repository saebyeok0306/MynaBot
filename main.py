import datetime
import discord
import os
from discord.ext import commands, tasks
from dotenv import dotenv_values
from dotenv import load_dotenv

import utils.Database as db
import utils.Logs as logs

load_dotenv(verbose=True, override=True)

# venv\Scripts\activate
# venv\Scripts\deactivate
# pip freeze > requirements.txt
# .venv$ pip install -r requirements.txt 

# pip install discord.py[voice]

# screen -S dc python main.py
# screen -S dc -X quit

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')
status_count = 0
core_list = [
    'Administrator', 'Command', 'ColorName',
    'Papago', 'ChatGPT', 'ArmyCard', 'Youtube',
    'Message', 'Extension', 'VoiceClient'
]

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

    await logs.send_log(bot=bot, log_text=log_text)

@bot.event
async def on_member_remove(member):
    log_text = f"{member.guild} 서버에서 {member.display_name} 님이 나갔습니다. ("

    role_res = await db.DeleteRoleServerByAuthor(member)
    if role_res: log_text += f"역할 제거, "
    user_res = db.DeleteUserByAuthor(member)
    if user_res: log_text += f"유저정보 제거, "
    log_text += ")"
    
    await logs.send_log(bot=bot, log_text=log_text)

if __name__ == '__main__':
    config = dotenv_values(".env")
    bot.run(config['Discord_Token'])