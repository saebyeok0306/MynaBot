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
    
    @commands.command(name="로그보기", aliases=["에러로그", "에러로그보기"])
    async def 로그보기(self, ctx, *input):
        if ctx.message.author.guild_permissions.administrator:
            showPage = 9
            if len(input) == 1:
                if input[0] == 'all' or input[0] =='All':
                    showPage = 0
                else:
                    try: showPage = int(input[0])
                    except: pass

            content = []
            with open('log/error.txt', 'r', encoding='utf-8') as l:
                header = ''
                _temp = ''
                while True:
                    text = l.readline()
                    if text == '': break
                    if text.startswith('user :'):
                        header = text.replace('\n', '').replace('user : ', '')
                        continue

                    if text == '\n':
                        _temp += text
                        _temp = _temp.replace('\n\n', '')
                        content.append([header, _temp])
                        _temp = ''
                    else:
                        _temp += text
            
            content.reverse()
            if showPage != 0:
                content = content[:showPage]
            
            embed=discord.Embed(color=0xFFA1A1, title=":scroll: 에러로그", description=f'에러를 기록한 로그를 취합합니다.')
            embed.set_footer(text = f"{ctx.author.display_name} | 에러로그", icon_url = ctx.author.avatar_url)
            for text in content:
                embed.add_field(name=f'{text[0]}', value=f'{text[1]}')
            await ctx.channel.send(embed = embed)
    
    @commands.command(name="로그삭제", aliases=["로그지우기"])
    async def 로그삭제(self, ctx):
        with open('log/error.txt', 'w', encoding='utf-8') as l:
            l.write('')
        await ctx.channel.send(f'로그를 전부 지웠어요!')

def setup(bot):
    bot.add_cog(Administrator(bot))