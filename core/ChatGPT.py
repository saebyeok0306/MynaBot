import discord, asyncio
import openai
from discord.ext import commands, tasks
import xml.etree.ElementTree as elemTree

class ChatGPT(commands.Cog):
    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
    
    @commands.command(name="마이나야", aliases=["검색"])
    async def 마이나야(self, ctx, *input):
        # tree = elemTree.parse('./keys.xml')
        # SECRETKEY = tree.find('string[@name="chatSecret"]').text
        print(input)
    
async def setup(bot):
    await bot.add_cog(ChatGPT(bot))