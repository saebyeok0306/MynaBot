import discord, random
import data.Functions as fun
import data.Logs as logs
from pathlib import Path
import openai
from discord.ext import commands, tasks
from collections import deque, defaultdict
from dotenv import dotenv_values


class TTS(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')

        self.bot = bot
        self.voice_channel = {}
        self.is_cat = defaultdict(bool)
        self.message_queue = deque()
        self.file_path = "./data"
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
                file = f"{id}.mp3"
                res = self.synthesize_text(file, message)
                # res = self.openai_tts(file, message)
                if res is True:
                    vc.play(discord.FFmpegPCMAudio(source=f"{self.file_path}/{file}"), after= lambda x: os.remove(f"{self.file_path}/{file}"))
                    self.voice_channel[id] = 0
            
            else:
                for id in self.voice_channel.keys():
                    self.voice_channel[id] += 1

                    guild = self.bot.get_guild(id)
                    channel = guild.voice_client.channel
                    if guild.voice_client is not None and len(channel.members) == 1:
                        await guild.voice_client.disconnect()
                        del self.voice_channel[id]
                        print(f"{guild.name} 서버의 음성채팅에서 봇이 자동으로 퇴장했습니다.")

                    if self.voice_channel[id] > 600:
                        if guild.voice_client is not None:
                            await guild.voice_client.disconnect()
                        del self.voice_channel[id]
                        print(f"{guild.name} 서버의 음성채팅에서 봇이 자동으로 퇴장했습니다.")

        except:
            pass
            
    @commands.Cog.listener()
    async def on_message(self, message):
        # if str(message.channel).startswith("Direct Message"): return
        if message.author.bot: return None
        if message.guild.id not in [631471244088311840]: return

        vc = message.guild.voice_client
        if vc is None: return
        if message.author.voice is None: return
        if message.author.voice.channel != vc.channel: return
        if message.content.startswith("!"): return
        if not message.channel.id in fun.getBotChannel(self.bot, message):
            if str(message.channel.type) != "voice": return
            if vc.channel != message.channel: return

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

        if ctx.guild.id not in self.voice_channel.keys():
            self.voice_channel[ctx.guild.id] = 0
        
        await logs.SendLog(bot=self.bot, log_text=f"{ctx.guild.name}의 {ctx.author.display_name}님이 TTS 명령어를 실행했습니다.")

    
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

    @commands.command(name="흑이체")
    async def 흑이체(self, ctx):
        if ctx.author.voice is None:
            return
        
        author_id = ctx.author.id
        self.is_cat[author_id] = not self.is_cat[author_id]

        await ctx.reply(f"흑이체를 {'활성화' if self.is_cat[author_id] else '비활성화'}합니다.", mention_author=False)

    # @commands.command(name="퇴장")
    # async def 퇴장(self, ctx):
    #     if ctx.voice_client is not None:
    #         await ctx.voice_client.disconnect()
    
    @staticmethod
    def cat_speech(text):
        sentences = text.split(" ")

        trans_text = []
        for sentence in sentences:
            l = len(sentence)
            res = ""
            if l == 1:
                res = "냥"
            else:
                # 애옹, 야옹
                l -= 1
                res += random.choice(["애", "야", "먀"])

                for _ in range(l-1):
                    l -= 1
                    res += "오"
                
                res += "옹"
            trans_text.append(res)
        return " ".join(trans_text)
                
    def openai_tts(self, file, message):
        import re
        from emoji import core
        try:

            text = message.content
            author = message.author
            print(f"synthesize_text : {text}")

            # 1. 이모지를 먼저 제거합니다.
            text = core.replace_emoji(text, replace="")

            # 2. 남은 텍스트에서 디스코드 이모지 문자열 <:이모지:> 을 검사해서 제거합니다.
            pattern = r'<(.*?)>'
            matches = re.findall(pattern, text)
            if matches:
                for pat in matches:
                    text = text.replace(f"<{pat}>", "")
            
            text = text.strip()
            
            # 모두 제거 후, 문자열이 공백이면 return 합니다.
            if text == "": return False

            # 흑이체 사용할 대상
            if self.is_cat[author.id]:
                text = self.cat_speech(text)

            text_length = len(text)
            speed = 2.0
            text_speed = [(10, 1.1), (20, 1.3), (30, 1.5), (40, 1.7)]
            for le, sp in text_speed:
                if text_length <= le:
                    speed = sp
                    break

            config = dotenv_values('.env')
            client = openai.OpenAI(api_key=config['OpenAI_Secret'])
            speech_file_path = Path(self.file_path) / f"{file}"
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text,
                speed=speed
            )

            response.stream_to_file(speech_file_path)
            return True
        except Exception as e:
            print(e)
            return False
    
    def synthesize_text(self, file, message):
        # "texttospeech import"
        from google.cloud import texttospeech
        import re
        from emoji import core

        text = message.content
        author = message.author
        print(f"synthesize_text : {text}")

        # 1. 이모지를 먼저 제거합니다.
        text = core.replace_emoji(text, replace="")

        # 2. 남은 텍스트에서 디스코드 이모지 문자열 <:이모지:> 을 검사해서 제거합니다.
        pattern = r'<(.*?)>'
        matches = re.findall(pattern, text)
        if matches:
            for pat in matches:
                text = text.replace(f"<{pat}>", "")
        
        text = text.strip()
        
        # 모두 제거 후, 문자열이 공백이면 return 합니다.
        if text == "": return False
        
        client = texttospeech.TextToSpeechClient()
        text_length = len(text)
        # 최대 길이를 200으로 지정 (지나치게 길어지면 에러 발생)
        max_length = 200

        # 문자열의 길이가 최대 길이보다 크면 return 합니다.
        if  text_length > max_length: return False

        # 흑이체 사용할 대상
        if self.is_cat[author.id]:
            text = self.cat_speech(text)


        # 텍스트 변환
        input_text = texttospeech.SynthesisInput(text=text)

        # gender = [
        #     ("ko-KR-Neural2-C", texttospeech.SsmlVoiceGender.MALE),
        #     ("ko-KR-Neural2-B", texttospeech.SsmlVoiceGender.FEMALE)
        # ]
        gender = {"name": "ko-KR-Neural2-C", "ssml_gender": texttospeech.SsmlVoiceGender.MALE}


        # JOKE
        if author.id in [298824090171736074, 369723279167979520, 413315617270136832, 389327234827288576]:
            gender["name"] = "ko-KR-Neural2-B"
            gender["ssml_gender"] = texttospeech.SsmlVoiceGender.FEMALE


        # 오디오 설정 (예제에서는 한국어, 남성C)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name=gender["name"],
            ssml_gender=gender["ssml_gender"],
        )

        speed = 2.0
        text_speed = [(10, 1.1), (20, 1.3), (30, 1.5), (40, 1.7)]
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
        
        # audio 폴더 안에 output.mp3라는 이름으로 파일 생성
        with open(f"{self.file_path}/{file}", "wb") as out:
            out.write(response.audio_content)
        
        return True
    

async def setup(bot):
    await bot.add_cog(TTS(bot))