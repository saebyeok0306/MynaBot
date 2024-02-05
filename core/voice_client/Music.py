from collections import defaultdict

import asyncio
import discord
import os
import yt_dlp as youtube_dl
from discord import ClientException
from discord.ext import commands
from pytube import YouTube, Playlist

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'cachedir': '/data',
    'outtmpl': 'data/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.3):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        # if 'entries' in data:
        #     # take first item from a playlist
        #     data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music:

    def __init__(self, bot):
        self.bot = bot
        self.file_path = "./data"
        self.playlist = defaultdict(list)
        self.current = {}

    def exist_playlist(self, guild):
        if self.playlist[guild.id]:
            return True
        else:
            return False

    def cleanup_msuic(self, guild_id):
        if self.current.get(guild_id):
            del self.current[guild_id]
        if self.playlist.get(guild_id):
            del self.playlist[guild_id]

    async def play_music(self, guild, voice_client):
        if self.playlist[guild.id] and voice_client.is_playing() is False:
            music = self.playlist[guild.id].pop(0)
            player = await YTDLSource.from_url(music['url'], loop=self.bot.loop, stream=False)
            try:
                voice_client.play(
                    player,
                    after=lambda error: self.play_after(error, guild.id, ytdl.prepare_filename(player.data))
                )
                self.current[guild.id] = music

                await guild.voice_client.channel.send(f'**Now playing** ~🎶: `{player.title}`')
                return True
            except ClientException:
                self.playlist[guild.id].insert(0, music)
                return False
            except Exception as e:
                print(f"play_music에서 오류 발생 : {e}")
                return False

        else:
            return False

    def play_after(self, e, guild_id, filename):
        if e:
            return print(f'Player error: {e}')

        try:
            os.remove(f"{filename}")
            if self.current.get(guild_id):
                del self.current[guild_id]
        except Exception as e:
            print(f"파일 삭제 실패 : {e}")

    @staticmethod
    def parse_youtube_url(url):
        try:
            video = YouTube(url)
            return url, video
        except:
            # Playlist로 다시 체크
            pass

        try:
            video = []
            playlist = Playlist(url)
            for play_url in playlist:
                video.append(YouTube(play_url))
            return playlist, video
        except:
            return -1, -1

    async def add_music(self, ctx, url, video):
        """Music URL"""
        self.playlist[ctx.guild.id].append({"title": video.title, "url": url, "author": ctx.author})
        await ctx.send(f'플레이리스트에 추가되었어요!\n{video.title}')

    async def add_playlist(self, ctx, urls, videos):
        """Playlist URL"""
        for url, video in zip(urls, videos):
            self.playlist[ctx.guild.id].append({"title": video.title, "url": url, "author": ctx.author})
        await ctx.send(f'플레이리스트에 추가되었어요!\n{videos[0].title} 외 {len(urls) - 1}곡')

    @commands.command(name="재생", aliases=["play"])
    async def 재생(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        if ctx.author.voice is None:
            embed = discord.Embed(color=0xB22222, title="[ 🚨음악 재생 오류 ]", description=f"음성채팅 채널에 먼저 입장해야 합니다!")
            embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.display_avatar)
            return await ctx.reply(embed=embed)

        if ctx.guild.voice_client is None:
            embed = discord.Embed(color=0xB22222, title="[ 🚨음악 재생 오류 ]",
                                  description=f"봇이 음성채팅 채널에 먼저 입장해야 합니다!\n`!입장` 명령어를 사용하세요.")
            embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.display_avatar)
            return await ctx.reply(embed=embed)


        async with ctx.typing():
            # url을 통해 비디오 데이터를 획득합니다.
            url, video = self.parse_youtube_url(url)
            if url == video == -1:
                return await ctx.send(f'잘못된 URL 주소입니다!\n다른 주소로 다시 시도해주세요.')

            # 플레이리스트인 경우
            if type(video) is list:
                await self.add_playlist(ctx, url, video)

            # 아닌 경우
            else:
                await self.add_music(ctx, url, video)

    @commands.command(name="볼륨", aliases=["음량"])
    async def 볼륨(self, ctx, volume: int):
        """Changes the player's volume"""
        if ctx.author.voice is None: return
        if ctx.voice_client is None: return

        ctx.voice_client.source.volume = volume / 100
        await ctx.reply(f"### [ 🎚️ 음량 조절 ]\n\n**봇의 음량을 {volume}%로 변경했어요.**", mention_author=False)

    @commands.command(name="정지", aliases=["스킵", "skip", "중지"])
    async def 정지(self, ctx):
        """Stops and disconnects the bot from voice"""
        guild_id = ctx.guild.id
        if ctx.voice_client and ctx.voice_client.is_playing() and self.current.get(guild_id):
            if self.current[guild_id]["author"].id != ctx.author.id and \
                    not ctx.author.guild_permissions.administrator:
                embed = discord.Embed(
                    color=0xB22222, title="[ 권한 없음 ]",
                    description=f"해당 음악을 추가한 유저만 노래를 정지할 수 있어요!\n`{self.current[guild_id]['title']}` | **{self.current[guild_id]['author'].display_name}님**")
                embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.display_avatar)
                return await ctx.reply(embed=embed)

            await ctx.reply(f"### [ 음악 정지 ]\n\n**재생 중인 음악을 정지했어요.**", mention_author=False)
            ctx.voice_client.stop()
            del self.current[guild_id]

    @commands.command(name="곡랜덤", aliases=["곡셔플"])
    async def 곡랜덤(self, ctx):
        guild_id = ctx.guild.id

        if ctx.voice_client and self.playlist[guild_id]:
            from random import shuffle
            shuffle(self.playlist[guild_id])
            await ctx.reply(
                f"### [ 플레이리스트 ({len(self.playlist[guild_id])}곡) 🎶 ]\n\n**플레이리스트의 곡 순서를 랜덤하게 섞었어요!**",
                mention_author=False
            )

    @commands.command()
    async def 플레이리스트(self, ctx):
        guild_id = ctx.guild.id
        text = f"### [ 플레이리스트 ({len(self.playlist[guild_id])}곡) 🎶 ]\n\n"
        if not self.playlist[guild_id]:
            text += f"텅텅 비어있네요.\n`!유튜브 [검색]`나 `!재생 [유튜브 주소]`로 음악을 재생할 수 있어요."
            return await ctx.reply(text, mention_author=False)

        for idx, music in enumerate(self.playlist[guild_id]):
            text += f"{idx + 1}. {music['title']}\n"

        text += f"> `!음악삭제 [번호]`로 삭제 가능!"
        await ctx.reply(text, mention_author=False)

    @commands.command()
    async def 음악삭제(self, ctx, *, idx):
        idx = int(idx)
        guild_id = ctx.guild.id
        if not self.playlist[guild_id]:
            embed = discord.Embed(color=0xB22222, title="[ 🚨음악 삭제 오류 ]", description=f"플레이리스트가 비어있어요!")
            embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.display_avatar)
            return await ctx.reply(embed=embed)

        if idx == 0 or len(self.playlist[guild_id]) < idx:
            embed = discord.Embed(color=0xB22222, title="[ 🚨음악 삭제 오류 ]", description=f"플레이리스트에 없는 번호에요!")
            embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.display_avatar)
            return await ctx.reply(embed=embed)

        _idx = idx - 1
        music = self.playlist[guild_id][_idx]
        if music['author'].id != ctx.author.id and not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                color=0xB22222, title="[ 🚨음악 삭제 오류 ]",
                description=f"해당 음악을 추가한 유저만 삭제할 수 있어요!\n`{music['title']}` | **{music['author'].display_name}님**")
            embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.display_avatar)
            return await ctx.reply(embed=embed)

        del self.playlist[guild_id][_idx]
        embed = discord.Embed(
            color=0xB22222, title="[ 🚨음악 삭제 ]",
            description=f"플레이리스트에서 `{music['title']}`곡을 **삭제**했어요!"
        )
        embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.display_avatar)
        await ctx.reply(embed=embed)

    @commands.command(name="음악모두삭제", aliases=["음악전부삭제", "음악올삭제"])
    async def 음악모두삭제(self, ctx):
        guild_id = ctx.guild.id
        if not self.playlist[guild_id]:
            embed = discord.Embed(color=0xB22222, title="[ 🚨음악 삭제 오류 ]", description=f"플레이리스트가 비어있어요!")
            embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.display_avatar)
            return await ctx.reply(embed=embed)

        self.playlist[guild_id] = []
        embed = discord.Embed(
            color=0xB22222, title="[ 🚨음악 삭제 ]",
            description=f"플레이리스트에서 `모든` 곡을 **삭제**했어요!"
        )
        embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.display_avatar)
        await ctx.reply(embed=embed)
