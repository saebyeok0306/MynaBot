import io
from typing import Union

import PIL.Image
import aiohttp
import discord
from PIL import Image, ImageDraw
from discord.ext import commands


class RoleIcon(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.title = '아이콘 변경'

    async def edit_role_icon(self, ctx: commands.Context, role: discord.Role, icon: Union[None, bytes], descript_text: str):
        try:
            await role.edit(display_icon=icon)
            embed = discord.Embed(
                title=f':magic_wand: 닉네임 {descript_text}',
                description=f'{ctx.author.mention} {descript_text} 작업을 성공적으로 수행했어요!',
                color=0x51ffc8
            )
            await ctx.channel.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title=f':tickets: 닉네임 아이콘 안내',
                description=f'{ctx.author.mention} {descript_text}에 실패했습니다.\n-# 봇에게 역할 수정 권한이 없습니다.',
                color=0xdc5468
            )
            embed.set_footer(text=f"{ctx.author.display_name} | {self.title}",
                             icon_url=ctx.author.display_avatar)
            await ctx.channel.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title=f':tickets: 닉네임 아이콘 안내',
                description=f'{ctx.author.mention} {descript_text}에 실패했습니다.\n-# {e}',
                color=0xdc5468
            )
            embed.set_footer(text=f"{ctx.author.display_name} | {self.title}",
                             icon_url=ctx.author.display_avatar)
            await ctx.channel.send(embed=embed)

    @commands.command(name="아이콘")
    async def 아이콘(self, ctx: commands.Context):
        files = ctx.message.attachments
        roles = ctx.author.roles
        icon_role = None
        for role in roles:
            if str(ctx.author.id) == role.name:
                icon_role = role
                break

        if ctx.guild.premium_tier < 2:
            embed = discord.Embed(
                title=f':tickets: 닉네임 아이콘 안내',
                description=f'{ctx.author.mention} 아이콘 변경은 서버 부스트 레벨이 2단계 이상부터 가능합니다.\n-# 해당 기능이 부스트 레벨 2단계부터 활성화됩니다.',
                color=0xdc5468
            )
            embed.set_footer(text=f"{ctx.author.display_name} | {self.title}", icon_url=ctx.author.display_avatar)
            await ctx.channel.send(embed=embed)
            return

        if len(files) > 1:
            embed = discord.Embed(
                title=f':tickets: 닉네임 아이콘 안내',
                description=f'{ctx.author.mention} 아이콘으로 사용할 이미지는 1개만 업로드해주세요.\n-# png, jpg 확장자만 가능',
                color=0xdc5468
            )
            embed.set_footer(text=f"{ctx.author.display_name} | {self.title}", icon_url=ctx.author.display_avatar)
            await ctx.channel.send(embed=embed)
            return

        if len(files) == 0:
            if icon_role is not None and icon_role.display_icon is not None:
                await self.edit_role_icon(ctx, icon_role, None, "아이콘 초기화")

            else:
                embed = discord.Embed(
                    title=f':tickets: 닉네임 아이콘 안내',
                    description=f'{ctx.author.mention} 아이콘으로 사용할 이미지 1개를 함께 업로드해야 합니다.\n-# png, jpg 확장자만 가능',
                    color=0xdc5468
                )
                embed.set_footer(text=f"{ctx.author.display_name} | {self.title}", icon_url=ctx.author.display_avatar)
                await ctx.channel.send(embed=embed)
            return

        image: discord.Attachment = files[0]
        content_type = image.content_type.split("/")[1]

        if content_type not in ['png', 'jpg', 'jpeg']:
            embed = discord.Embed(
                title=f':tickets: 닉네임 아이콘 안내',
                description=f'{ctx.author.mention} 아이콘으로 사용할 이미지는 png, jpg 확장자만 가능합니다.',
                color=0xdc5468
            )
            embed.set_footer(text=f"{ctx.author.display_name} | {self.title}", icon_url=ctx.author.display_avatar)
            await ctx.channel.send(embed=embed)
            return

        if icon_role is None:
            embed = discord.Embed(
                title=f':tickets: 닉네임 아이콘 안내',
                description=f'{ctx.author.mention} 컬러닉네임이 활성화된 계정만 가능합니다.\n`!색상변경` 명령어를 사용해서 컬러닉네임을 활성화해주세요.',
                color=0xdc5468
            )
            embed.set_footer(text=f"{ctx.author.display_name} | {self.title}", icon_url=ctx.author.display_avatar)
            await ctx.channel.send(embed=embed)
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(image.url) as resp:
                if resp.status != 200:
                    embed = discord.Embed(
                        title=f':tickets: 닉네임 아이콘 안내',
                        description=f'{ctx.author.mention} 이미지를 다운로드 받는데 실패했습니다.\n-# {resp.content}',
                        color=0xdc5468
                    )
                    embed.set_footer(text=f"{ctx.author.display_name} | {self.title}",
                                     icon_url=ctx.author.display_avatar)
                    return
                image_data = await resp.read()

        # 이미지를 256x256으로 리사이징
        with Image.open(io.BytesIO(image_data)) as img:
            img: PIL.Image.Image = img.convert("RGBA")  # 투명 배경 유지
            # 정사각형으로 자르기
            size = min(img.size)
            img = img.crop((0, 0, size, size))
            
            # 이미지 크기를 256x256으로 리사이징
            img = img.resize((256, 256))

            # 둥근 사각형 마스크 생성
            mask = Image.new("L", (256, 256), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, 256, 256), radius=50, fill=255)

            # 마스크를 이미지에 적용
            img.putalpha(mask)

            # 이미지를 바이트로 변환
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format="PNG")
            img_byte_arr.seek(0)
        
        # 역할 아이콘 수정
        await self.edit_role_icon(ctx, icon_role, img_byte_arr.getvalue(), "아이콘 변경")


async def setup(bot):
    await bot.add_cog(RoleIcon(bot))
