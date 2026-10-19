import asyncio
import time

import discord
from discord.ext import commands, tasks

import utils.Logs as logs
import utils.Utility as util
from core.voice_client.Music import Music
from core.voice_client.TTS import TTS
from main import MynaBot


class VoiceClient(commands.Cog, TTS, Music):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        for parent_class in self.__class__.__bases__:
            if parent_class.__name__ == "Cog": continue
            print(f'{parent_class.__name__}가 로드되었습니다.')

        self.bot: MynaBot = bot
        self.delta = 0
        self.delete_state_list = []
        self.server_voice_client_state = {}
        TTS.__init__(self, self.bot)
        Music.__init__(self, self.bot)
        self.voice_client_processer.start()

    def cog_unload(self):
        self.voice_client_processer.stop()
        self.cleanup_all_tts()

    def tts_should_wait(self, guild):
        # 음악 대기열이 있으면 음악을 먼저 재생합니다.
        return self.exist_playlist(guild)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member == self.bot.user:
            if self.server_voice_client_state.get(member.guild.id):
                if before.channel is not None and after.channel is None:
                    try:
                        await before.channel.connect()
                        await logs.send_log(self.bot, f"{member.guild.name} 서버에서 음성채팅 재연결에 성공했습니다.")
                    except Exception as e:
                        await logs.send_log(self.bot, f"{member.guild.name} 서버에서 음성채팅 채널에 재연결하는데 실패했습니다.\n{e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.voice_client_processer.is_running():
            # voice_client_processer Loop가 죽은 경우, 다시 실행하기
            self.voice_client_processer.start()
        # if str(message.channel).startswith("Direct Message"): return
        if message.author.bot: return False

        if message.guild is None or self.current.get(message.guild.id): return False
        vc = message.guild.voice_client
        if vc is None: return False
        if message.author.voice is None: return False
        if message.author.voice.channel != vc.channel: return False
        if message.content.startswith("!"): return False
        if message.content.startswith("http://"): return False
        if message.content.startswith("https://"): return False
        if message.channel.id not in util.get_bot_channel(self.bot, message):
            if str(message.channel.type) != "voice": return False
            if vc.channel != message.channel: return False

        self.enqueue_tts(message)

    @tasks.loop(seconds=1)
    async def voice_client_processer(self):
        """1초마다 루프하면서 voice_client와 관련된 모든 동작을 수행합니다."""
        cur_time = time.time()
        if cur_time - self.delta < 1:
            return False

        self.delta = cur_time
        work_tasks = []
        for voice_client in self.bot.voice_clients:

            if len(voice_client.channel.members) == 1:
                self.delete_state_list.append(voice_client.guild.id)
                await logs.send_log(bot=self.bot, log_text=f"{voice_client.guild.name} 서버의 음성채팅에서 봇이 퇴장했습니다.")
                continue

            if voice_client.is_playing():
                continue

            guild = voice_client.guild

            # 플레이리스트에 음악이 존재하면
            if self.exist_playlist(guild):
                work_tasks.append(
                    asyncio.create_task(
                        self.play_music(guild, voice_client)
                    )
                )
                continue

            # TTS 메시지는 길드별 워커(TTS.enqueue_tts)가 이벤트 기반으로 처리합니다.

        for guild_id in self.delete_state_list:
            try:
                guild = self.bot.get_guild(guild_id)
                if guild.voice_client:
                    if self.server_voice_client_state.get(guild_id):
                        del self.server_voice_client_state[guild_id]
                    await guild.voice_client.disconnect()

                self.cleanup_msuic(guild_id)
                self.cleanup_tts(guild_id)

            except:
                pass
        self.delete_state_list = []
        await asyncio.gather(*work_tasks)

    @commands.command(name="입장", aliases=["음성채팅입장", "음성입력", "TTS입장"])
    async def 입장(self, ctx: commands.Context):

        if ctx.author.voice is None:
            embed = discord.Embed(color=0xB22222, title="[ 🚨음성채널 오류 ]", description=f"음성채팅 채널에 먼저 입장해야 합니다!")
            embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.display_avatar)
            msg = await ctx.reply(embed=embed)
            await msg.delete(delay=10)
            await ctx.message.delete(delay=10)
            return

        if ctx.guild.voice_client is not None and ctx.guild.voice_client.channel != ctx.author.voice.channel:
            embed = discord.Embed(color=0xB22222, title="[ 🚨음성채널 오류 ]", description=f"봇이 다른 음성채팅 채널에 입장한 상태입니다.")
            embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.display_avatar)
            msg = await ctx.reply(embed=embed)
            await msg.delete(delay=10)
            await ctx.message.delete(delay=10)
            return

        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()
        await ctx.author.voice.channel.connect()
        self.server_voice_client_state[ctx.guild.id] = True

        await logs.send_log(bot=self.bot, log_text=f"{ctx.guild.name}의 {ctx.author.display_name}님이 입장 명령어를 실행했습니다.")

    @commands.command(name="입장이동", aliases=["이동", "음성채널이동"])
    async def 입장이동(self, ctx):
        if ctx.author.voice is None:
            embed = discord.Embed(color=0xB22222, title="[ 🚨음성채널 오류 ]", description=f"음성채팅 채널에 먼저 입장해야 합니다!")
            embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.display_avatar)
            msg = await ctx.reply(embed=embed)
            await msg.delete(delay=10)
            await ctx.message.delete(delay=10)
            return

        if ctx.guild.voice_client is None:
            embed = discord.Embed(color=0xB22222, title="[ 🚨음성채널 오류 ]", description=f"봇이 음성채팅 채널에 참여한 상태가 아닙니다!")
            embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.display_avatar)
            msg = await ctx.reply(embed=embed)
            await msg.delete(delay=10)
            await ctx.message.delete(delay=10)
            return

        await ctx.guild.voice_client.disconnect()
        await ctx.author.voice.channel.connect()
        await logs.send_log(bot=self.bot,
                            log_text=f"{ctx.guild.name}의 {ctx.author.display_name}님이 입장이동 명령어를 실행했습니다.")

    @commands.command(name="퇴장")
    async def 퇴장(self, ctx: commands.Context):
        if not util.is_server_manager(ctx.author):
            return
        if ctx.guild.voice_client is None or ctx.author.voice is None:
            return
        if ctx.author.voice.channel != ctx.guild.voice_client.channel:
            return

        embed = discord.Embed(color=0xB22222, title="[ 관리자명령 ]", description=f"음성채팅 채널에서 {self.bot.user.display_name} 봇이 퇴장합니다.")
        embed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.display_avatar)
        await ctx.reply(embed=embed, mention_author=False)
        self.server_voice_client_state.pop(ctx.guild.id, None)
        self.cleanup_tts(ctx.guild.id)
        await ctx.guild.voice_client.disconnect()
        await logs.send_log(bot=self.bot, log_text=f"{ctx.guild.name} 서버의 음성채팅에서 봇이 퇴장했습니다.")


async def setup(bot):
    await bot.add_cog(VoiceClient(bot))
