import asyncio
from typing import Any

import discord
from discord.ext import commands
from discord.ext.commands import Context, errors
from discord.ext.commands._types import BotT
from dotenv import dotenv_values
from dotenv import load_dotenv

import utils.Logs as logs
import utils.Utility as util
import utils.database.Database as db

load_dotenv(verbose=True, override=True)


# https://github.com/staciax/valorant-discord-bot/blob/master/bot.py
class MynaBot(commands.Bot):
    bot_app_info: discord.AppInfo

    def __init__(self, test_flag: bool) -> None:
        super().__init__(command_prefix='!!' if test_flag else '!', case_insensitive=True,
                         intents=discord.Intents.all())
        self.BCFlag = False
        self.BC_LIST = []

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
        ...

    async def start(self, token) -> None:
        return await super().start(token, reconnect=True)  # type: ignore

    async def on_command_error(self, context: Context[BotT], exception: errors.CommandError, /) -> None:
        import traceback
        # 오류 메시지를 터미널에 출력
        await logs.send_log(self, f"An error occurred: {exception}")
        # 로그를 통해서 더 많은 정보를 확인하고 싶으면 logging 모듈을 사용할 수도 있습니다.
        traceback.print_exception(type(exception), exception, exception.__traceback__)

    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:
        import traceback
        # 이벤트 핸들러에서 발생한 오류를 처리
        await logs.send_log(self, f"An error occurred in {event_method}:\n{traceback.format_exc()}")
        traceback.print_exc()


if __name__ == '__main__':
    # argv --test 포함시 테스트봇으로 실행됨.
    test_flag = util.is_test_version()
    config = dotenv_values(".env")

    discord_token = config['Discord_Token2'] if test_flag else config['Discord_Token']

    db.init_db()

    bot = MynaBot(test_flag)
    asyncio.run(bot.load_extension(f'core.Event'))
    asyncio.run(bot.start(token=discord_token))
