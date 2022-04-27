import discord, asyncio, random, math
import data.Functions as fun
from discord.ext import commands

class Administrator(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="관리자청소", aliases=["관리자삭제","관리자제거","관리자지우기"])
    async def 관리자청소(self, ctx, *input):
        if ctx.message.author.guild_permissions.administrator:
            remove = 5
            if len(input) >= 1 and input[0].isdigit():
                remove = int(input[0])

            await ctx.channel.purge(limit=remove+1)
            msg = await ctx.channel.send(content = f'**{remove}개**의 메시지를 삭제했어요!')
            await msg.delete(delay=1)

def setup(bot):
    bot.add_cog(Administrator(bot))