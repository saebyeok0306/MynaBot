import discord, random, asyncio, datetime
from discord.ext import commands
from PIL import Image,ImageDraw,ImageFont

class ArmyCard(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.path = 'data/ArmyCard'
        self.img_path = f'{self.path}/Fun'
    
    async def create_card(self, ctx, name, join_date, exit_date):
        import os

        today = datetime.datetime.now()
        total_day = exit_date - join_date
        service_day = today - join_date
        remain_day = exit_date - today + datetime.timedelta(days=1)

        if remain_day.days > 10:
            remain_day_str = f"{remain_day.days}일"
        else:
            remain_day_str = f"{int(remain_day.total_seconds()*1000000)}마이크로초"
        
        # 입대하기 전
        if service_day.days < 0:
            filename = random.choice(os.listdir(self.img_path))
            file = discord.File(f"{self.img_path}/{filename}", filename=filename)
            embed = discord.Embed(color=0xB22222, title=f"{name}님의 남은 입대일", description=f'D-{-service_day.days}일 남았네요.', timestamp=ctx.message.created_at)
            embed.set_thumbnail(url=f"attachment://{filename}")
            await ctx.reply(file=file, embed=embed, mention_author=False)
        
        # 전역한 이후
        elif remain_day.days < 0:
            return
            
        # 복무 중
        else:
            if remain_day.days <= 100 and random.randint(1, 100) >= 90:
                img_bg = Image.open(f'{self.path}/card.png')
                font = ImageFont.truetype(os.path.join("data", 'NanumGothic.ttf'), 26, encoding="UTF-8")
                draw = ImageDraw.Draw(img_bg)
                draw.text((20, 7), f"{name}님의 남은 복무일", fill="white", stroke_width=2, stroke_fill="black", font=font, align='left')
                draw.text((140, 35), f"D-{remain_day.days} 만큼 남았군요?", fill="white", stroke_width=2, stroke_fill="black", font=font, align='left')
                draw.text((140, 35), f"D-{remain_day.days}", fill="red", stroke_width=2, stroke_fill="black", font=font, align='left')
                img_bg.save(f"{self.path}/result.png")
                file = discord.File(f"{self.path}/result.png")
                await ctx.reply(file=file)
            else:
                filename = random.choice(os.listdir(self.img_path))
                file = discord.File(f"{self.img_path}/{filename}", filename=filename)
                embed = discord.Embed(color=0xB22222, title=f"{name}님의 남은 복무일", description=f'복무기간은 {service_day.days}일이네요.\n그리고... **{remain_day_str}**이나 남았네요. ㅅㄱㄹ\n복무비율 : `{round((service_day.days / total_day.days)*100, 2)}%`\n전역날짜 : {exit_date.strftime("%Y년 %m월 %d일")}', timestamp=ctx.message.created_at)
                embed.set_thumbnail(url=f"attachment://{filename}")
                await ctx.reply(file=file, embed=embed, mention_author=False)

    @commands.command(name="버터쿠키")
    async def 버터쿠키(self, ctx, *input):
        if ctx.guild.id in [631471244088311840]:
            join_date = datetime.datetime(2022,5,30)
            exit_date = datetime.datetime(2024,2,29)
            await self.create_card(ctx, "버터쿠키", join_date, exit_date)
    
    @commands.command(name="뮤")
    async def 뮤(self, ctx, *input):
        if ctx.guild.id in [631471244088311840]:
            join_date = datetime.datetime(2022,10,11)
            exit_date = datetime.datetime(2024,4,10)
            await self.create_card(ctx, "뮤", join_date, exit_date)
    
    @commands.command(name="공나물")
    async def 공나물(self, ctx, *input):
        if ctx.guild.id in [631471244088311840]:
            join_date = datetime.datetime(2023,1,9)
            exit_date = datetime.datetime(2024,10,7)
            await self.create_card(ctx, "공나물", join_date, exit_date)


async def setup(bot):
    await bot.add_cog(ArmyCard(bot))
