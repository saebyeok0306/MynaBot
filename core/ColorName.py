import discord
import random
from discord.ext import commands

import utils.Logs as logs
import utils.Utility as util
from utils.Role import *


class ColorName(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.title = '닉네임 색상변경'

    @commands.command(name="색상변경", aliases=['색상수정'])
    async def 색상변경(self, ctx, *input):
        if ctx.channel.id not in util.get_bot_channel(self.bot, ctx):
            embed = discord.Embed(
                title=f':exclamation: 채널 설정 안내',
                description=f'{ctx.author.mention} 해당서버의 관리자께서,\n채널주제에 `#{self.bot.user.name}`를 작성해주셔야 합니다.',
                color=0xff0000
            )
            embed.set_footer(text=f"{ctx.author.display_name} | {self.title}", icon_url=ctx.author.display_avatar)
            await ctx.channel.send(embed=embed)
            return False

        # if ctx.guild.id not in [631471244088311840, 966942556078354502, 740177366231285820]:
        #     embed = discord.Embed(title = f':exclamation: 닉네임 색상변경 안내', description = f'{ctx.author.mention} 색상변경 기능은 현재 디스코드 서버에서는 지원되지 않습니다.', color = 0xff0000)
        #     embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.display_avatar)
        #     await ctx.channel.send(embed = embed)
        #     return False

        colorLists = {
            '랜덤': '000000',
            '흰색': 'ffffff',
            '아이보리': 'f7f7e8',
            '크림': 'f7f5c9',
            '빨강': 'e97d7d',
            '홍색': 'f15b5b',
            '분홍': 'f7add7',
            '주황': 'e67e22',
            '노랑': 'f1c40f',
            '레몬': 'f6f436',
            '핑크': 'e91e63',
            '보라': '9b59b6',
            '인디고': '49007e',
            '파랑': '3498db',
            '초록': '5cb323',
            '연두': '2ecc71',
            '민트': '51ffc9',
            '하늘': 'b9e0ff',
            '갈색': '966147'
        }

        async def Error():
            embed = discord.Embed(
                title=f':tickets: 닉네임 색상변경 안내',
                description=f'{ctx.author.mention} 색상을 입력하실 땐, 색상코드(0x51FFC9)와 같이 입력하시거나 기본 색상이름을 쓰시면 됩니다.',
                color=0x51ffc9
            )
            colorText = ''
            for col, hexs in colorLists.items():
                colorText += f'{col}, '
            embed.add_field(name=f'기본 색상 종류', value=f'{colorText[:-2]}')
            embed.set_footer(text=f"{ctx.author.display_name} | {self.title}", icon_url=ctx.author.display_avatar)
            await ctx.channel.send(embed=embed)

        if len(input) == 0:
            await Error()
            return False

        colors = 0
        input_color = input[0]
        if input_color == '랜덤':
            colors = random.randint(1, 0xFFFFFF)
        elif input_color[:2] == '0x':
            colors = int(input_color, 16)
        elif colorLists.get(input_color):
            colors = int(colorLists[input_color], 16)
        else:
            await Error()
            return False

        if colors > 0xFFFFFF:
            embed = discord.Embed(
                title=f':tickets: 닉네임 색상변경 안내',
                description=f'{ctx.author.mention} 색상의 범위는 `0x000001`에서 `0xFFFFFF`까지 입니다.',
                color=0x51ffc9
            )
            embed.set_footer(text=f"{ctx.author.display_name} | {self.title}", icon_url=ctx.author.display_avatar)
            await ctx.channel.send(embed=embed)
            return False

        if colors == 0x000000 or colors == 0x36393F:
            embed = discord.Embed(
                title=f':tickets: 닉네임 색상변경 안내',
                description=f'{ctx.author.mention} 해당 색상은 금지된 색상입니다.',
                color=0x51ffc9
            )
            embed.set_footer(text=f"{ctx.author.display_name} | {self.title}", icon_url=ctx.author.display_avatar)
            await ctx.channel.send(embed=embed)
            return False

        # 1. 서버에 역할이 있는지 체크하기
        user_role = get_role_server_by_author(ctx.author)
        if not user_role:
            user_role = await create_role_author(ctx.author)

        # 2. 유저에게 역할이 부여되어있는지 체크하기
        role = get_role_author(ctx.author)
        if not role:
            await ctx.author.add_roles(user_role)
            role = user_role

        await role.edit(color=colors)

        embed = discord.Embed(
            title=f':star2: 닉네임 색상변경',
            description=f'{ctx.author.mention} 색상변경이 완료되었어요!',
            color=colors
        )
        embed.set_footer(text=f"{ctx.author.display_name} | {self.title}", icon_url=ctx.author.display_avatar)
        await ctx.channel.send(embed=embed)
        await logs.send_log(bot=self.bot,
                            log_text=f"{ctx.guild.name}의 {ctx.author.display_name}님이 색상변경 명령어를 실행했습니다.")
        return True


async def setup(bot):
    await bot.add_cog(ColorName(bot))
