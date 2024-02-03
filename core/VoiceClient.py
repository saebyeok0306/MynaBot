import discord
import utils.Utility as util
import data.Logs as logs
from discord.ext import commands, tasks


class VoiceClient(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.voice_client_processer.start()

    def cog_unload(self):
        self.voice_client_processer.stop()

    async def voice_client_processer(self):
        pass

    @commands.Cog.listener()
    async def on_message(self, message):
        # if str(message.channel).startswith("Direct Message"): return
        if message.author.bot: return None

        vc = message.guild.voice_client
        if vc is None: return
        if message.author.voice is None: return
        if message.author.voice.channel != vc.channel: return
        if message.content.startswith("!"): return
        if message.content.startswith("http://"): return
        if message.content.startswith("https://"): return
        if message.channel.id not in util.get_bot_channel(self.bot, message):
            if str(message.channel.type) != "voice": return
            if vc.channel != message.channel: return
        # is_playing = db.GetMusicByGuild(message.guild)[1]
        # if is_playing: return

        self.tts_channel[message.guild.id].message_queue.append(message)
        if not self.message_queue_process.is_running():
            self.message_queue_process.start()

    @commands.command(name="입장", aliases=["음성채팅입장", "음성입력", "TTS입장"])
    async def 입장(self, ctx):

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

        await logs.SendLog(bot=self.bot, log_text=f"{ctx.guild.name}의 {ctx.author.display_name}님이 입장 명령어를 실행했습니다.")

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


async def setup(bot):
    await bot.add_cog(VoiceClient(bot))
