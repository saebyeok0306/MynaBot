import discord, asyncio
from discord.ext import commands, tasks

class Minecraft(commands.Cog):
    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
    
    @commands.command(name="마크", aliases=["마크서버", "서버"])
    async def 마크(self, ctx):
        if ctx.guild.id in [631471244088311840]:
            embed=discord.Embed(color=0xB22222, title="모드서버", description="`갈대`의 1.19.2 패브릭서버", timestamp=ctx.message.created_at)
            embed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
            embed.add_field(name = '서버주소', value = 'reedserver.kro.kr')
            embed.add_field(name = '서버문의', value = '@갈대#2519 에게 연락하세요!')
            embed.add_field(name = '서버모드', value = 'https://drive.google.com/drive/folders/1EEJq1CwCNP14cofTOmjZzGbtZD8uFBc8?usp=sharing')
            embed.add_field(name = '설치순서1', value = '다운받은 파일 중, fabric-installer-0.11.1.exe을 실행하여 1.19.2 패브릭모드를 설치한다.')
            embed.add_field(name = '설치순서2', value = 'mode.zip을 마인크래프트 모드폴더에 풀어놓는다.')
            embed.add_field(name = '설치순서3', value = '마크런처에서 설치된 1.19.2 패브릭모드를 켜서, westreed.kro.kr 주소로 서버 접속하기.')
            await ctx.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Minecraft(bot))

# @commands.command(name="마크", aliases=['마인크래프트', '마크서버'])
# async def 마크(self, ctx, *input):
#     embed=discord.Embed(color=0xB22222, title="산업모드서버", description="`갈대`의 1.18.2 포지서버", timestamp=ctx.message.created_at)
#     embed.set_thumbnail(url=ctx.author.display_avatar)
#     embed.add_field(name = '서버주소', value = 'westreed.kro.kr')
#     embed.add_field(name = '서버문의', value = '@갈대#2519 에게 연락하세요!')
#     embed.add_field(name = '서버모드', value = 'https://drive.google.com/drive/folders/1oT2hivIlCF9Cm5TIsFr3pK-vkvnw1zaT?usp=sharing')
#     embed.add_field(name = '상세정보', value = '상세한 설명은 "!갈대서버"를 입력하세요.')
#     embed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
#     await ctx.channel.send(embed=embed)

# @commands.command(name="갈대서버")
# async def 갈대서버(self, ctx, *input):
#     embed=discord.Embed(color=0xB22222, title="갈대서버 상세설명", description="모드파일 : https://drive.google.com/drive/folders/1oT2hivIlCF9Cm5TIsFr3pK-vkvnw1zaT?usp=sharing\n넣는경로 : C:\\Users\\\계정명\\AppData\\Roaming\\\.minecraft\\mods", timestamp=ctx.message.created_at)
#     embed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
#     embed.add_field(name = '설치순서1', value = '다운받은 파일 중, forge-1.18.2-40.1.0-installer.jar을 실행하여 1.18.2 포지를 설치한다.')
#     embed.add_field(name = '설치순서2', value = 'userMods.zip을 마인크래프트 모드폴더에 풀어놓는다.')
#     embed.add_field(name = '설치순서3', value = '마크런처에서 설치된 1.18.2 포지를 켜서, westreed.kro.kr 주소로 서버 접속하기.')
#     await ctx.channel.send(embed=embed)