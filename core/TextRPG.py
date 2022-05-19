import sqlite3, discord, asyncio, random, math
import data.Functions as fun
from discord.ext import commands

class TextRPG(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot

def setup(bot):
    bot.add_cog(TextRPG(bot))