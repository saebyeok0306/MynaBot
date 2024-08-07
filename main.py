import asyncio

import discord
from discord.ext import commands
from dotenv import dotenv_values
from dotenv import load_dotenv

import utils.Utility as util
import utils.database.Database as db

load_dotenv(verbose=True, override=True)


# https://github.com/staciax/valorant-discord-bot/blob/master/bot.py
class MynaBot(commands.Bot):
    bot_app_info: discord.AppInfo

    def __init__(self, test_flag: bool) -> None:
        super().__init__(command_prefix='!!' if test_flag else '!', case_insensitive=True,
                         intents=discord.Intents.all())

        if test_flag is False:
            self.remove_command('help')

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner

    async def setup_hook(self):
        try:
            self.owner_id = int(config['OWNER_ID'])  # type: ignore
        except KeyError:
            self.bot_app_info = await self.application_info()
            self.owner_id = self.bot_app_info.owner.id

    async def on_ready(self) -> None:
        await self.tree.sync()

    async def start(self, token) -> None:
        return await super().start(token, reconnect=True)  # type: ignore


if __name__ == '__main__':
    # argv --test 포함시 테스트봇으로 실행됨.
    test_flag = util.is_test_version()
    config = dotenv_values(".env")

    discord_token = config['Discord_Token2'] if test_flag else config['Discord_Token']

    db.init_db()

    bot = MynaBot(test_flag)
    asyncio.run(bot.load_extension(f'core.Event'))
    asyncio.run(bot.start(token=discord_token))
