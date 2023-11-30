import urllib.request
import os, sys, discord, asyncio, json
import data.Functions as fun
from discord.ext import commands, tasks
from dotenv import dotenv_values

class Papago(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
    
    def TransText(self, langS, langT, Texts):
        config = dotenv_values('.env')
        client_id = config['Naver_Client_ID'] # 개발자센터에서 발급받은 Client ID 값
        client_secret = config['Naver_Client_Secret'] # 개발자센터에서 발급받은 Client Secret 값
        encText = urllib.parse.quote(Texts)
        data = f"source={langS}&target={langT}&text=" + encText
        url = "https://openapi.naver.com/v1/papago/n2mt"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id",client_id)
        request.add_header("X-Naver-Client-Secret",client_secret)
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        rescode = response.getcode()
        if(rescode==200):
            response_body = response.read()
            response_body = response_body.decode('utf-8')
            json_obj = json.loads(response_body)
            return True, json_obj["message"]["result"]["translatedText"]
        else:
            return False, rescode
    
    @commands.command(name="한영번역", aliases=[])
    async def 한영번역(self, ctx, *input):
        text = " ".join(input)
        if len(text) >= 500:
            embed = discord.Embed(color=0x2f3136)
            embed.set_author(name=f'너무 길어요. ({len(text)})')
            embed.set_thumbnail(url=self.bot.user.display_avatar)
            embed.add_field(name="결과", value=f'더 짧은 문장으로 작성해주세요.')
            await ctx.reply(embed=embed, mention_author=False)
            return False
        
        res, content = self.TransText("ko", "en", text)
        if res is True:
            embed = discord.Embed(color=0x2f3136)
            embed.set_author(name=f'파파고 번역 결과에요.')
            embed.set_thumbnail(url=self.bot.user.display_avatar)
            embed.add_field(name="원문", value=f'{text}')
            embed.add_field(name="결과", value=f'{content}')
            await ctx.reply(embed=embed, mention_author=False)
        else:
            print("Error Code:" + content)
            embed = discord.Embed(color=0x2f3136)
            embed.set_author(name=f'오늘 할당량이 끝났어요.')
            embed.set_thumbnail(url=self.bot.user.display_avatar)
            embed.add_field(name="결과", value=f'내일 다시 부탁드려요!')
            await ctx.reply(embed=embed, mention_author=False)
    
    @commands.command(name="영한번역", aliases=[])
    async def 영한번역(self, ctx, *input):
        text = " ".join(input)
        if len(text) >= 500:
            embed = discord.Embed(color=0x2f3136)
            embed.set_author(name=f'너무 길어요. ({len(text)})')
            embed.set_thumbnail(url=self.bot.user.display_avatar)
            embed.add_field(name="결과", value=f'더 짧은 문장으로 작성해주세요.')
            await ctx.reply(embed=embed, mention_author=False)
            return False
        
        res, content = self.TransText("en", "ko", text)
        if res is True:
            embed = discord.Embed(color=0x2f3136)
            embed.set_author(name=f'파파고 번역 결과에요.')
            embed.set_thumbnail(url=self.bot.user.display_avatar)
            embed.add_field(name="원문", value=f'{text}')
            embed.add_field(name="결과", value=f'{content}')
            await ctx.reply(embed=embed, mention_author=False)
        else:
            print("Error Code:" + content)
            embed = discord.Embed(color=0x2f3136)
            embed.set_author(name=f'오늘 할당량이 끝났어요.')
            embed.set_thumbnail(url=self.bot.user.display_avatar)
            embed.add_field(name="결과", value=f'내일 다시 부탁드려요!')
            await ctx.reply(embed=embed, mention_author=False)

async def setup(bot):
    await bot.add_cog(Papago(bot))