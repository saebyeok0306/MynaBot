import discord, datetime
from discord.ext import commands
from PIL import Image,ImageDraw,ImageFont

import utils.Logs as logs

class Profile(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.path = 'data/Profile'
        self.exp = [int(1.03**lv)+lv for lv in range(501)]

        # for lv in range(501):
        #     print(lv, self.exp[lv])

    def GetLevel(self, exp):
        if self.exp[-1] <= exp: return 500
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
    
    @commands.command(name="프로필", aliases=["내정보", "Profile", "profile", "정보"])
    async def 프로필(self, ctx):
        import os
        
        await ctx.author.display_avatar.save("user_img.png")
        username = ctx.author.display_name
        join_date = ctx.author.joined_at # datetime
        join_date = join_date.replace(tzinfo=None)
        today = datetime.datetime.now()
        d_day = today - join_date + datetime.timedelta(days=1)
        exp = d_day.days
        level = self.GetLevel(exp)
        need_exp = self.exp[level]
        prev_exp = self.exp[level-1 if level > 0 else 0]
        cur_exp  = exp - prev_exp
        diff_exp = need_exp - prev_exp

        user_img = Image.open("user_img.png").resize(size=(280,280), resample=Image.LANCZOS)
        img_bg = Image.open(f'{self.path}/profile.png')
        font30 = ImageFont.truetype(os.path.join('data', 'NanumGothic.ttf'), 30, encoding="UTF-8")
        font35 = ImageFont.truetype(os.path.join('data', 'NanumGothic.ttf'), 35, encoding="UTF-8")
        font40 = ImageFont.truetype(os.path.join('data', 'NanumGothic.ttf'), 40, encoding="UTF-8")
        font50 = ImageFont.truetype(os.path.join('data', 'NanumGothic.ttf'), 50, encoding="UTF-8")
        draw = ImageDraw.Draw(img_bg)
        draw.text((370,225),f"Lv.{level}",fill="#9AEACD",stroke_width=1,stroke_fill="#9AEACD",font=font40,align='left')
        draw.text((500,212),f"{username}님",fill="white",font=font50,align='left')
        draw.text((370,275), f"{join_date.strftime('%Y.%m.%d')}   D+{exp}",fill="white",font=font40,align='left')
        draw.text((450,405), f"{exp}/{need_exp}",fill="white",font=font35,align='left')
        draw.text((370,455), f"경험치는 서버가입일로부터 지난 일수입니다.",fill="white",font=font30,align='left')

        # 경험치바
        exp_percent = round(cur_exp / diff_exp, 3)
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

        await logs.SendLog(bot=self.bot, log_text=f"{ctx.guild.name}의 {ctx.author.display_name}님이 프로필 명령어를 실행했습니다. (Lv.{level})")
    
    
async def setup(bot):
    await bot.add_cog(Profile(bot))