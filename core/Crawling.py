import discord, asyncio
import requests
import data.Functions as fun
from bs4 import BeautifulSoup
from collections import OrderedDict
from urllib.parse import quote
from discord.ext import commands, tasks


# pip install beautifulsoup4
# pip install lxml

class Crawling(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.NaverCrawling.start()
    
    def cog_unload(self):
        self.NaverCrawling.cancel()

    # 네이버 블로그 카테고리의 글 제목과 글 번호, 썸네일, 링크 가져오기
    @tasks.loop(seconds=360)
    async def NaverCrawling(self):
        url = 'https://blog.naver.com/PostList.naver?blogId=algorithmjobs&from=postList&categoryNo=16'
        headers = {'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
        res = requests.get(url, headers=headers)
        res.raise_for_status() # 문제시 프로그램 종료
        soup = BeautifulSoup(res.text, "lxml")
        post_data = []

        posts = soup.find_all("li", attrs={"class":"item"})
        for post in posts:
            post_title = post.find("strong", attrs={"class":"title ell"}).get_text()
            post_link = post.find("a", attrs={"class":"link pcol2"})['href']
            post_links = 'https://blog.naver.com/' + post_link
            post_number = post_link[43:-51]
            post_icon = post.find("img", attrs={"class":"thumb"})['src']
            post_date = post.find("span", attrs={"class":"date"}).get_text()
            post_data.append(OrderedDict({'pid':int(post_number), 'title':post_title, 'link':post_links, 'icon':post_icon, 'date':post_date}))
        post_data.reverse()

        guilds = fun.getTopicChannel('#크롤링마이나')
        for guild in guilds.keys():
            channels = guilds[guild]
            for channel in channels:
                lastIdx = 0
                lastMsg = None
                async for message in channel.history(limit=1):
                    lastMsg = message
                    # Lastpid : 222720244322
                    if lastMsg.content.startswith('Lastpid'):
                        lastIdx = int(lastMsg.content[10:])

                lastPid = lastIdx
                for pd in post_data:
                    if pd['pid'] > lastIdx:
                        lastPid = pd['pid']
                        embed=discord.Embed(color=0x2f3136)
                        embed.set_author(name=f'{pd["title"]}', url=f'{pd["link"]}')
                        embed.add_field(name='게시날짜', value=f'{pd["date"]}')
                        embed.set_thumbnail(url=pd["icon"])

                        # embed=discord.Embed(title=f'{pd["title"]}',url=f'{pd["link"]}', color=0x2f3136)
                        # embed.set_footer(text=f'{self.bot.user} │ {pd["date"]}', icon_url=self.bot.user.display_avatar)
                        # embed.set_thumbnail(url=pd["icon"])
                        await channel.send(embed = embed)
                if lastIdx != lastPid:
                    if lastIdx != 0: await lastMsg.delete()
                    await channel.send(content = f'Lastpid : {lastPid}')


async def setup(bot):
    await bot.add_cog(Crawling(bot))