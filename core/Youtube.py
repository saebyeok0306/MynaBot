from googleapiclient.discovery import build
import xml.etree.ElementTree as elemTree
import discord, asyncio
from discord.ext import commands

class Youtube(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.list_count = 10
        self.sel_emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    def search_videos(self, youtube, keyword):
        request = youtube.search().list(
            q=keyword,
            type='video',
            part='id,snippet',
            maxResults=self.list_count
        )
        response = request.execute()
        return response.get('items', [])

    @staticmethod
    def get_video_url(video_id):
        return f'https://www.youtube.com/watch?v={video_id}'
    
    @staticmethod
    async def select_video(ctx, keyword, video):
        _, video_url, video_info = video
        await ctx.channel.send(f"### [ 🔮유튜브 검색완료 ]\n\n**{keyword} 의 검색 결과입니다.**\n{video_info}\n{video_url}")
    
    @commands.command(name="유튜브", aliases=["유튜브검색"])
    async def 유튜브(self, ctx, *input):
        tree = elemTree.parse('./keys.xml')
        SECRETKEY = tree.find('string[@name="YoutubeKey"]').text
        youtube = build('youtube', 'v3', developerKey=SECRETKEY)

        keyword = " ".join(input)
        url = f"https://www.youtube.com/results?search_query={keyword}"

        embed = discord.Embed(color=0xB22222, title="[ 🪄유튜브 검색중 ]", description=f"잠시만 기다려주세요!\n정보를 수집 중이므로 다소 시간이 걸릴 수 있습니다.")
        embed.set_footer(text = f"{ctx.author.display_name}", icon_url = ctx.author.display_avatar)
        msg = await ctx.channel.send(embed=embed)

        try:
            videos = self.search_videos(youtube, keyword)
        except Exception as e:
            embed = discord.Embed(color=0xB22222, title="[ 🚨유튜브 검색 오류 ]", description=f"유튜브 API에 문제가 발생했어요.\n`{e}`")
            embed.set_footer(text = f"{ctx.author.display_name}", icon_url = ctx.author.display_avatar)
            await msg.edit(embed=embed)

        result = []
        result_text = ""
        for idx, video in enumerate(videos):
            video_id = video['id']['videoId']
            title = video['snippet']['title']
            channelTitle = video['snippet']['channelTitle']
            video_url = self.get_video_url(video_id)

            video_info = f"{title} | {channelTitle}"
            result.append((video_id, video_url, video_info))
            result_text += f"{idx+1}번 {video_info}\n"
        
        embed = discord.Embed(color=0xB22222, title="[ 🪄유튜브 검색중 ]", description=f"**{keyword} 의 검색 결과입니다.**\n\n{result_text}")
        embed.set_footer(text = f"{ctx.author.display_name}", icon_url = ctx.author.display_avatar)
        await msg.edit(embed=embed)
        for i in range(self.list_count):
            await msg.add_reaction(self.sel_emoji[i])

        try:
            def check(reaction, user):
                return str(reaction) in self.sel_emoji and \
                user == ctx.author and reaction.message.id == msg.id
            reaction, user = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)

            for i in range(self.list_count):
                if str(reaction) == self.sel_emoji[i]:
                    await msg.delete()
                    await self.select_video(ctx, keyword, result[i])
                    break
        except asyncio.TimeoutError:
            await msg.delete()
            await self.select_video(ctx, keyword, result[0])
    

async def setup(bot):
    await bot.add_cog(Youtube(bot))