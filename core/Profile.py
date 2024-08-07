from typing import Literal

import datetime
import discord
from PIL import Image, ImageDraw, ImageFont
from discord import app_commands, Interaction
from discord.ext import commands
from sqlalchemy import and_

import utils.Logs as logs
from main import MynaBot
from utils.database.Database import SessionContext
from utils.database.model.exp import Exp


class Profile(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.path = 'data/Profile'
        self.exp = [int(1.03**lv)+lv for lv in range(1001)]

        # for lv in range(501):
        #     print(lv, self.exp[lv])

    def GetLevel(self, exp):
        if self.exp[-1] <= exp: return 1000
        for lv in range(len(self.exp)):
            if exp < self.exp[lv]:
                return lv
        return 0

    def CircleMasking(self, img, width, height):
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0,0,width,height), fill=255) # masking
        masked_img = Image.new("RGBA", (width,height), (0,0,0,0))
        masked_img.paste(img, mask=mask)
        return masked_img
    
    def RectMasking(self, img, origin_size:tuple[int,int], mask_size:tuple[int,int]):
        mask = Image.new("L", origin_size, 0)
        draw = ImageDraw.Draw(mask)
        mask_width, mask_height = mask_size
        draw.rectangle((0,0,mask_width,mask_height), fill=255) # masking
        masked_img = Image.new("RGBA", origin_size, (0,0,0,0))
        masked_img.paste(img, mask=mask)
        return masked_img
    
    def round_rectangle(self, size, radius, color):
        """Draw a rounded rectangle"""
        width, height = size
        rectangle = Image.new('RGBA', size, (0,0,0,0))
        draw = ImageDraw.Draw(rectangle)
        draw.rounded_rectangle(((0,0),(width, height)), radius=radius, fill=color)

        return rectangle

    def get_profile(self, ctx):
        username = ctx.author.display_name
        join_date = ctx.author.joined_at  # datetime
        join_date = join_date.replace(tzinfo=None)
        today = datetime.datetime.now()
        d_day = today - join_date + datetime.timedelta(days=1)

        cat_exp = 0
        chat_exp = 0
        visit_exp = 0
        with SessionContext() as session:
            user_exp = session.query(Exp).filter(and_(Exp.id == ctx.author.id, Exp.guild_id == ctx.guild.id)).first()
            if user_exp is not None:
                chat_exp = user_exp.chat_count
                cat_exp = user_exp.cat_count * 2
                visit_exp = user_exp.today_exp * 100

        exp = d_day.days + cat_exp + chat_exp + visit_exp
        level = self.GetLevel(exp)
        need_exp = self.exp[level]
        prev_exp = self.exp[level - 1 if level > 0 else 0]
        cur_exp = exp - prev_exp
        diff_exp = need_exp - prev_exp

        return {
            "username": username,
            "join_date": join_date,
            "days": d_day.days,
            "exp": exp,
            "level": level,
            "need_exp": need_exp,
            "prev_exp": prev_exp,
            "cur_exp": cur_exp,
            "diff_exp": diff_exp,
            "chat_exp": chat_exp,
            "cat_exp": cat_exp,
            "visit_exp": visit_exp
        }

    def get_profile_interaction(self, interaction: Interaction[MynaBot]):
        username = interaction.user.display_name
        join_date = interaction.user.joined_at  # datetime
        join_date = join_date.replace(tzinfo=None)
        today = datetime.datetime.now()
        d_day = today - join_date + datetime.timedelta(days=1)

        cat_exp = 0
        chat_exp = 0
        visit_exp = 0
        with SessionContext() as session:
            user_exp = session.query(Exp).filter(and_(Exp.id == interaction.user.id, Exp.guild_id == interaction.guild.id)).first()
            if user_exp is not None:
                chat_exp = user_exp.chat_count
                cat_exp = user_exp.cat_count * 2
                visit_exp = user_exp.today_exp * 100

        exp = d_day.days + cat_exp + chat_exp + visit_exp
        level = self.GetLevel(exp)
        need_exp = self.exp[level]
        prev_exp = self.exp[level - 1 if level > 0 else 0]
        cur_exp = exp - prev_exp
        diff_exp = need_exp - prev_exp

        return {
            "username": username,
            "join_date": join_date,
            "days": d_day.days,
            "exp": exp,
            "level": level,
            "need_exp": need_exp,
            "prev_exp": prev_exp,
            "cur_exp": cur_exp,
            "diff_exp": diff_exp,
            "chat_exp": chat_exp,
            "cat_exp": cat_exp,
            "visit_exp": visit_exp
        }

    @commands.command()
    async def 프로필2(self, ctx):
        import os
        
        await ctx.author.display_avatar.save("user_img.png")
        profile_data = self.get_profile(ctx)

        user_img = Image.open("user_img.png").resize(size=(280,280), resample=Image.LANCZOS)
        img_bg = Image.open(f'{self.path}/profile.png')
        font35 = ImageFont.truetype(os.path.join('data', 'NanumGothic.ttf'), 35, encoding="UTF-8")
        font40 = ImageFont.truetype(os.path.join('data', 'NanumGothic.ttf'), 40, encoding="UTF-8")
        font45 = ImageFont.truetype(os.path.join('data', 'NanumGothic.ttf'), 45, encoding="UTF-8")
        draw = ImageDraw.Draw(img_bg)
        draw.text((370,225),f"Lv.{profile_data['level']}",fill="#9AEACD",stroke_width=1,stroke_fill="#9AEACD",font=font40,align='left')
        draw.text((500,212),f"{profile_data['username']}님",fill="white",font=font45,align='left')
        draw.text((370,275), f"{profile_data['join_date'].strftime('%Y.%m.%d')}   D+{profile_data['days']}",fill="white",font=font40,align='left')
        draw.text((450,405), f"{profile_data['exp']}/{profile_data['need_exp']}",fill="white",font=font35,align='left')
        # draw.text((370,455), f"경험치는 서버가입일로부터 지난 일수입니다.",fill="white",font=font30,align='left')

        # 경험치바
        exp_percent = round(profile_data['cur_exp'] / profile_data['diff_exp'], 3)
        exp_bar_length = int(550 * exp_percent)
        if exp_bar_length > 0:
            exp_img = self.round_rectangle((550, 58), 40, "#31C791")
            exp_img = self.RectMasking(exp_img, origin_size=(550, 58), mask_size=(exp_bar_length, 58))
            img_bg.alpha_composite(exp_img, (365,335))
            # draw.rounded_rectangle(((365,335),(exp_bar_length,393)), radius=40, fill="#31C791") # (365,335),(915,393)
        draw.text((620,345), f"{int(exp_percent*100)}%",fill="white",font=font35,align='left')
        
        rounded_user_img = self.CircleMasking(user_img, 280, 280)
        img_bg.alpha_composite(rounded_user_img, (60,180))
        img_bg = img_bg.resize(size=(400, 220), resample=Image.LANCZOS) # 1000, 550
        img_bg.save(f"{self.path}/result.png")
        file = discord.File(f"{self.path}/result.png")
        await ctx.reply(file=file, mention_author=False)

        await logs.send_log(bot=self.bot, log_text=f"{ctx.guild.name}의 {ctx.author.display_name}님이 프로필 명령어를 실행했습니다. (Lv.{profile_data['level']})")

    @app_commands.command(description='내 프로필을 확인할 수 있어요.')
    @app_commands.describe(flag='내 프로필 정보를 다른사람도 볼 수 있게 공개할지 선택합니다.')
    async def 프로필(self, interaction: Interaction[MynaBot], flag: Literal['공개', '비공개'] = '비공개'):
        profile_data = self.get_profile_interaction(interaction)
        exp_percent = int(round(profile_data['cur_exp'] / profile_data['diff_exp'], 3)*100)
        embed = discord.Embed(title=f"{interaction.user.display_name}님의 프로필", color=0x5d73ac)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="Level", value=f"Lv.{profile_data['level']}")
        embed.add_field(name="Join", value=f"{profile_data['join_date'].strftime('%Y.%m.%d')} D+{profile_data['days']}")
        embed.add_field(name="Exp", value=f"{profile_data['exp']}/{profile_data['need_exp']} ({exp_percent}%)")
        embed.add_field(name="JoinExp", value=f"{profile_data['days']} Exp")
        embed.add_field(name="ChatExp", value=f"{profile_data['chat_exp'] + profile_data['visit_exp']} Exp")
        embed.add_field(name="EtcExp", value=f"{profile_data['cat_exp']} Exp")
        embed.set_footer(text=f"{interaction.user} | 프로필", icon_url=interaction.user.display_avatar)

        flag = False if flag == '공개' else True
        await interaction.response.send_message(embed=embed, ephemeral=flag)

        await logs.send_log(bot=self.bot,
                            log_text=f"{interaction.guild.name}의 {interaction.user.display_name}님이 프로필 명령어를 실행했습니다. (Lv.{profile_data['level']})")


async def setup(bot):
    await bot.add_cog(Profile(bot))