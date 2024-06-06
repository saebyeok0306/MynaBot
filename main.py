import asyncio

import discord
from discord.ext import commands
from dotenv import dotenv_values
from dotenv import load_dotenv

import utils.Utility as util
import utils.database.Database as db
from utils.database.test import test_running

load_dotenv(verbose=True, override=True)

if __name__ == '__main__':
    # argv --test 포함시 테스트봇으로 실행됨.
    test_flag = util.is_test_version()
    config = dotenv_values(".env")

    discord_token = config['Discord_Token2'] if test_flag else config['Discord_Token']
    command_prefix = '!!' if test_flag else '!'
    intents = discord.Intents.all()

    bot = commands.Bot(command_prefix=command_prefix, intents=intents)
    if test_flag is False:
        bot.remove_command('help')

    db.init_db()

    asyncio.run(bot.load_extension(f'core.Event'))
    bot.run(token=discord_token)
