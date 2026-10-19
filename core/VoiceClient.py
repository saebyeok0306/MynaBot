import discord
from discord.ext import commands

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
        self.server_voice_client_state = {}
        TTS.__init__(self, self.bot)
        Music.__init__(self, self.bot)

    def cog_unload(self):
        self.cleanup_all_tts()

    def tts_should_wait(self, guild):
        # 음악 대기열이 있거나 곡을 내려받는 중이면 음악을 먼저 재생합니다.
        return self.exist_playlist(guild) or guild.id in self.music_loading

    def cleanup_voice(self, guild_id):
        self.cleanup_msuic(guild_id)
        self.cleanup_tts(guild_id)

    async def leave_voice(self, guild):
        # 상태를 먼저 지워야 on_voice_state_update에서 자동 재연결하지 않습니다.
        self.server_voice_client_state.pop(guild.id, None)
        self.cleanup_voice(guild.id)
        if guild.voice_client:
            await guild.voice_client.disconnect()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = member.guild

        if member == self.bot.user:
            if before.channel is None or after.channel is not None:
                return
            # 봇이 음성채널에서 끊긴 경우
            if not self.server_voice_client_state.get(guild.id):
                self.cleanup_voice(guild.id)
                return
            try:
                await before.channel.connect()
                await logs.send_log(self.bot, f"{guild.name} 서버에서 음성채팅 재연결에 성공했습니다.")
                self.start_music(guild.id)
            except Exception as e:
                await logs.send_log(self.bot, f"{guild.name} 서버에서 음성채팅 채널에 재연결하는데 실패했습니다.\n{e}")
            return

        # 다른 유저가 봇이 있는 채널에서 나간 경우, 사람이 남아있지 않으면 퇴장합니다.
        voice_client = guild.voice_client
        if voice_client is None or before.channel is None or before.channel == after.channel:
            return
        if voice_client.channel != before.channel:
            return
        if any(not m.bot for m in voice_client.channel.members):
            return

        await self.leave_voice(guild)
        await logs.send_log(bot=self.bot, log_text=f"{guild.name} 서버의 음성채팅에서 봇이 퇴장했습니다.")

    @commands.Cog.listener()
    async def on_message(self, message):
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
        await self.leave_voice(ctx.guild)
        await logs.send_log(bot=self.bot, log_text=f"{ctx.guild.name} 서버의 음성채팅에서 봇이 퇴장했습니다.")


async def setup(bot):
    await bot.add_cog(VoiceClient(bot))
