import discord
from discord.ext import commands

import utils.Utility as util


class Minecraft(commands.Cog):
    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot

    @commands.command(name="마크", aliases=["마크서버", "서버"])
    async def 마크(self, ctx):
        allowed_guild = util.is_allow_guild(ctx, util.GUILD_COMMAND_TYPE.MINECRAFT)

        if allowed_guild is False:
            return

        embed = discord.Embed(color=0xB22222, title="모드서버", description="`갈대`의 좀비 아포칼립스 서버",
                              timestamp=ctx.message.created_at)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
        embed.add_field(name='서버주소', value='minecraft.devlog.run')
        embed.add_field(name='서버문의', value='`@갈대`에게 연락하세요!')
        embed.add_field(name='서버모드',
                        value='https://drive.google.com/drive/folders/1n6GBysSh_Et_eeuKMoIfTKrNd2VY3Zwt?usp=sharing')
        embed.add_field(name='설치순서1', value='Modrinth App을 다운로드 받고 로그인한다.\n(링크 : https://modrinth.com/app)')
        embed.add_field(name='설치순서2', value='서버모드 파일링크에서 다운 받아서 실행한다.')
        embed.add_field(name='설치순서3', value='Modrinth App에 등록된 모드팩으로 실행한다.')
        await ctx.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Minecraft(bot))
