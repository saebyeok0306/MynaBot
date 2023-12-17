import discord
from discord.ext import commands, tasks
from collections import deque

class TTS(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')

        self.bot = bot
        self.voice_channel = {}
        self.message_queue = deque()
        self.read_message.start()
    
    def cog_unload(self):
        self.read_message.stop()
    
    @tasks.loop(seconds=1)
    async def read_message(self):
        import os
        
        try:
            if self.message_queue:
                vc = self.message_queue[0].guild.voice_client

                if vc.is_playing():
                    return

                message = self.message_queue.popleft()

                id = message.guild.id
                file = f"data/{id}.mp3"
                res = self.synthesize_text(file, message.content)
                if res is True:
                    vc.play(discord.FFmpegPCMAudio(source=file), after= lambda x: os.remove(file))
                    self.voice_channel[id] = 0
            
            else:
                for id in self.voice_channel.keys():
                    self.voice_channel[id] += 1

                    if self.voice_channel[id] > 60:
                        guild = self.bot.get_guild(id)
                        print(guild)
                        if guild.voice_client is not None:
                            await guild.voice_client.disconnect()
                        del self.voice_channel[id]
                        print(f"{guild.name} 서버의 음성채팅에서 봇이 자동으로 퇴장했습니다.")

        except:
            pass
            
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild.id not in [631471244088311840]: return

        vc = message.guild.voice_client
        if vc is None: return
        if str(message.channel.type) != "voice": return
        if vc.channel != message.channel: return
        if message.content.startswith("!"): return

        if message.content.strip() == "": return
        
        if message.guild.id not in self.voice_channel.keys():
            self.voice_channel[message.guild.id] = 0
        self.message_queue.append(message)

    @commands.command(name="TTS", aliases=["음성채팅입장", "음성입력", "TTS입장", "입장"])
    async def TTS(self, ctx, *input):
        if ctx.guild.id not in [631471244088311840]: return

        if ctx.author.voice is None:
            embed = discord.Embed(color=0xB22222, title="[ 🚨TTS 오류 ]", description=f"음성채팅 채널에 먼저 입장해야 합니다!")
            embed.set_footer(text = f"{ctx.author.display_name}", icon_url = ctx.author.display_avatar)
            msg = await ctx.reply(embed=embed)
            await msg.delete(delay=10)
            await ctx.message.delete(delay=10)
            return

        if ctx.voice_client is not None:
            embed = discord.Embed(color=0xB22222, title="[ 🚨TTS 오류 ]", description=f"봇이 다른 음성채팅 채널에 입장한 상태입니다.")
            embed.set_footer(text = f"{ctx.author.display_name}", icon_url = ctx.author.display_avatar)
            msg = await ctx.reply(embed=embed)
            await msg.delete(delay=10)
            await ctx.message.delete(delay=10)
            return

        voice_channel = ctx.author.voice.channel
        await voice_channel.connect()
    
    @commands.command(name="입장이동", aliases=["이동", "음성채널이동"])
    async def 입장이동(self, ctx, *input):
        if ctx.guild.id not in [631471244088311840]: return

        if ctx.author.voice is None:
            embed = discord.Embed(color=0xB22222, title="[ 🚨TTS 오류 ]", description=f"음성채팅 채널에 먼저 입장해야 합니다!")
            embed.set_footer(text = f"{ctx.author.display_name}", icon_url = ctx.author.display_avatar)
            msg = await ctx.reply(embed=embed)
            await msg.delete(delay=10)
            await ctx.message.delete(delay=10)
            return
        
        if ctx.voice_client is None:
            embed = discord.Embed(color=0xB22222, title="[ 🚨TTS 오류 ]", description=f"봇이 음성채팅 채널에 참여한 상태가 아닙니다!")
            embed.set_footer(text = f"{ctx.author.display_name}", icon_url = ctx.author.display_avatar)
            msg = await ctx.reply(embed=embed)
            await msg.delete(delay=10)
            await ctx.message.delete(delay=10)
            return

        await ctx.voice_client.disconnect()
        voice_channel = ctx.author.voice.channel
        await voice_channel.connect()

    # @commands.command(name="퇴장")
    # async def 퇴장(self, ctx):
    #     if ctx.voice_client is not None:
    #         await ctx.voice_client.disconnect()
    
    
    @staticmethod
    def synthesize_text(file, text):
        # "texttospeech import"
        from google.cloud import texttospeech
        import re

        client = texttospeech.TextToSpeechClient()

        print(f"synthesize_text : {text}")

        pattern = r'<(.*?)>'
        matches = re.findall(pattern, text)
        if matches:
            for pat in matches:
                text = text.replace(f"<{pat}>", "")
        
        if text.strip() == "": return False
        
        text_length = len(text)
        # 최대 길이를 200으로 지정 (지나치게 길어지면 에러 발생)
        max_length = 200
        # . 단위로 문장 분리
        words = text.split('. ')
        sentences = []
        current_sentence = ''
        for word in words:
            if len(current_sentence + word) <= max_length:
                current_sentence += word + ' '
            else:
                sentences.append(current_sentence.strip() + '.')
                current_sentence = word + ' '
        if current_sentence:
            sentences.append(current_sentence.strip() + '.')


        # 빈 배열 생성
        audio_data = []
        text_speed = [(10, 1.1), (20, 1.3), (30, 1.5), (40, 1.7)]

        # 문장 개수 단위로 텍스트 변환
        for sentence in sentences:
            input_text = texttospeech.SynthesisInput(text=sentence)

            gender = [
                ("ko-KR-Neural2-C", texttospeech.SsmlVoiceGender.MALE),
                ("ko-KR-Neural2-B", texttospeech.SsmlVoiceGender.FEMALE)
            ]

            # 오디오 설정 (예제에서는 한국어, 남성C)
            voice = texttospeech.VoiceSelectionParams(
                language_code="ko-KR",
                name=gender[0][0],
                ssml_gender=gender[0][1],
            )

            speed = 2.0
            for le, sp in text_speed:
                if text_length <= le:
                    speed = sp
                    break

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speed,
            )

            response = client.synthesize_speech(
                request={"input": input_text, "voice": voice, "audio_config": audio_config}
            )

            audio_data.append(response.audio_content)

        audio_data = b"".join(audio_data)
        
        
        # audio 폴더 안에 output.mp3라는 이름으로 파일 생성
        with open(file, "wb") as out:
            out.write(audio_data)
        
        return True
    

async def setup(bot):
    await bot.add_cog(TTS(bot))