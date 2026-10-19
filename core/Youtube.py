import asyncio

import discord
from discord.ext import commands
from dotenv import dotenv_values
from googleapiclient.discovery import build

import utils.Logs as logs


class Youtube(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.title = "유튜브 검색"
        self.list_count = 10
        self.sel_emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", "⬅️", "➡️", "❌"]

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

    async def select_video(self, ctx, keyword, video):
        _, video_url, video_info, _ = video
        if ctx.author.voice and ctx.guild.voice_client and ctx.message.channel == ctx.guild.voice_client.channel:
            music_cog = self.bot.cogs["VoiceClient"]
            music_cog.playlist[ctx.guild.id].append({"title": video_info, "url": video_url, "author": ctx.author})
            music_cog.start_music(ctx.guild.id)
            await ctx.reply(f"### [ 🔮유튜브 검색완료 ]\n\n**{keyword} 의 검색 결과입니다.**\n`플레이리스트에 해당 곡이 추가되었습니다!`\n{video_info}\n{video_url}",
                            mention_author=False)
        else:
            await ctx.reply(f"### [ 🔮유튜브 검색완료 ]\n\n**{keyword} 의 검색 결과입니다.**\n{video_info}\n{video_url}",
                            mention_author=False)
    
    @commands.command(name="유튜브", aliases=["유튜브검색"])
    async def 유튜브(self, ctx, *input):
        keyword = " ".join(input)
        if keyword == "":
            embed = discord.Embed(color=0xB22222, title="[ 🚨유튜브 검색오류 ]", description=f"검색어를 입력하셔야 합니다!")
            embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.display_avatar)
            msg = await ctx.reply(embed=embed)
            await msg.delete(delay=10)
            await ctx.message.delete(delay=10)
            return
        
        elif len(keyword) > 50:
            embed = discord.Embed(color=0xB22222, title="[ 🚨유튜브 검색오류 ]", description=f"검색어는 50자 이내로 입력하셔야 합니다!\n현재 {len(keyword)}자를 입력하셨습니다.")
            embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.display_avatar)
            msg = await ctx.reply(embed=embed)
            await msg.delete(delay=10)
            await ctx.message.delete(delay=10)
            return

        config = dotenv_values('.env')
        youtube = build('youtube', 'v3', developerKey=config['Youtube_Secret'])

        embed = discord.Embed(color=0xB22222, title="[ 🪄유튜브 검색중 ]", description=f"잠시만 기다려주세요!\n정보를 수집 중이므로 다소 시간이 걸릴 수 있습니다.")
        embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.display_avatar)
        msg = await ctx.channel.send(embed=embed)

        result_count = self.list_count
        try:
            videos = self.search_videos(youtube, keyword)
            if len(videos) == 0:
                embed = discord.Embed(color=0xB22222, title="[ 🚨유튜브 검색완료 ]", description=f"{keyword}에 대한 검색 결과가 없습니다!")
                embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.display_avatar)
                await msg.edit(embed=embed)
                return
            elif len(videos) < 10:
                result_count = len(videos)
        except Exception as e:
            embed = discord.Embed(color=0xB22222, title="[ 🚨유튜브 검색오류 ]", description=f"유튜브 API에 문제가 발생했어요.\n`{e}`")
            embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.display_avatar)
            await msg.edit(embed=embed)

        result = []
        for idx, video in enumerate(videos):
            video_id = video['id']['videoId']
            title = video['snippet']['title']
            channelTitle = video['snippet']['channelTitle']
            video_url = self.get_video_url(video_id)
            thumbnail_url = video['snippet']['thumbnails']['high']['url']

            video_info = f"{title} | {channelTitle}"
            result.append((video_id, video_url, video_info, thumbnail_url))
        
        paging = 0
        half_count = self.list_count//2 # 5
        while True:
            # Youtube Search Texts
            result_text = ""
            for i in range(half_count) if paging == 0 else range(half_count, result_count):
                if i < result_count:
                    result_text += f"{i+1}번 {result[i][2]}\n"

            embed = discord.Embed(color=0xB22222, title="[ 🪄유튜브 검색중 ]", description=f"**{keyword} 의 검색 결과입니다.**\n`아래의 이모지를 클릭해서 선택할 수 있습니다.`\n\n{result_text}")
            embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.display_avatar)
            await msg.edit(embed=embed)

            # 1 ~ 10
            for i in range(half_count) if paging == 0 else range(half_count, self.list_count):
                if i <result_count:
                    await msg.add_reaction(self.sel_emoji[i])
            
            # Next, Prev, Cancle
            if paging == 0 and result_count > half_count: await msg.add_reaction(self.sel_emoji[-2]) # Next
            if paging == 1: await msg.add_reaction(self.sel_emoji[-3]) # Prev
            await msg.add_reaction(self.sel_emoji[-1]) # Cancle

            try:
                def check(reaction, user):
                    return str(reaction) in self.sel_emoji and \
                    user == ctx.author and reaction.message.id == msg.id
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

                for i in range(self.list_count):
                    if str(reaction) == self.sel_emoji[i]:
                        await msg.delete()
                        await self.select_video(ctx, keyword, result[i])

                        await logs.send_log(bot=self.bot, log_text=f"{ctx.guild.name}의 {ctx.author.display_name}님이 유튜브 명령어를 실행했습니다.")
                        return
                
                if str(reaction) == self.sel_emoji[-3]: # prev
                    paging = 0
                    await msg.clear_reactions()
                    continue
                
                elif str(reaction) == self.sel_emoji[-2]: # next
                    if result_count > half_count:
                        paging = 1
                        await msg.clear_reactions()
                        continue
                
                elif str(reaction) == self.sel_emoji[-1]:
                    await msg.delete()
                    embed = discord.Embed(color=0xB22222, title="[ 🪄유튜브 검색취소 ]", description=f"유튜브 검색을 취소했어요.")
                    embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.display_avatar)
                    msg2 = await ctx.reply(embed=embed)
                    await msg2.delete(delay=5)
                    await ctx.message.delete(delay=5)
                    return
                    
            except asyncio.TimeoutError:
                await msg.delete()
                await self.select_video(ctx, keyword, result[0])
                return
    

async def setup(bot):
    await bot.add_cog(Youtube(bot))