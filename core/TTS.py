import discord, random, asyncio
import data.Functions as fun
import data.Logs as logs
from pathlib import Path
import openai
from discord.ext import commands, tasks
from collections import deque, defaultdict
from dotenv import dotenv_values

class Chat:
    def __init__(self):
        self.timer = 0
        self.message_queue = deque()
        self.voice_client = None
        self.voice_channel = None

class TTS(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')

        self.bot = bot
        self.tts_channel = defaultdict(Chat)
        self.is_cat = defaultdict(bool)
        # self.voice_channel = {}
        # self.message_queue = defaultdict(deque)
        self.file_path = "./data"
        self.message_queue_process.start()
    
    def cog_unload(self):
        self.message_queue_process.stop()

    async def read_message(self, guild_id):
        import os
        
        try:
            vc = self.tts_channel[guild_id].voice_client

            if vc.is_playing():
                return
            
            message = self.tts_channel[guild_id].message_queue.popleft()

            id = message.guild.id
            file = f"{id}.mp3"
            res = self.synthesize_text(file, message)
            # res = self.openai_tts(file, message)
            if res is True:
                vc.play(discord.FFmpegPCMAudio(source=f"{self.file_path}/{file}"), after= lambda x: os.remove(f"{self.file_path}/{file}"))
                self.tts_channel[id].timer = 0
        except:
            pass
    
    @tasks.loop(seconds=1)
    async def message_queue_process(self):
        message_tasks = []
        delete_tts_channel = []
        for guild_id in self.tts_channel.keys():
            if self.tts_channel[guild_id].message_queue:
                message_tasks.append(asyncio.create_task(self.read_message(guild_id)))

            else:
                self.tts_channel[guild_id].timer += 1
                guild = self.bot.get_guild(guild_id)

                # 변수에는 존재하는데 실제 봇은 입장을 안한 상태인 경우
                if guild.voice_client is None:
                    await self.tts_channel[guild_id].voice_channel.connect()

                channel = guild.voice_client.channel
                if len(channel.members) == 1:
                    await guild.voice_client.disconnect()
                    delete_tts_channel.append(guild_id)
                    print(f"{guild.name} 서버의 음성채팅에서 봇이 자동으로 퇴장했습니다.")

                elif self.tts_channel[guild_id].timer > 600:
                    await guild.voice_client.disconnect()
                    delete_tts_channel.append(guild_id)
                    print(f"{guild.name} 서버의 음성채팅에서 봇이 자동으로 퇴장했습니다.")

        await asyncio.gather(*message_tasks)

        for guild_id in delete_tts_channel:
            del self.tts_channel[guild_id]

    def is_allow_guild(self, ctx):

        allow_guilds = {
            "유즈맵 제작공간" : 631471244088311840,
            "데이터베이스" : 966942556078354502,
            "강화대전쟁" : 1171793482441039963,
            "마스에몽" : 948601885575741541,
        }
        if ctx.guild.id in allow_guilds.values():
            return True
        
        return False
            
    @commands.Cog.listener()
    async def on_message(self, message):
        # if str(message.channel).startswith("Direct Message"): return
        if message.author.bot: return None
        if self.is_allow_guild(message) is False: return

        vc = message.guild.voice_client
        if vc is None: return
        if message.author.voice is None: return
        if message.author.voice.channel != vc.channel: return
        if message.content.startswith("!"): return
        if message.content.startswith("http://"): return
        if message.content.startswith("https://"): return
        if not message.channel.id in fun.getBotChannel(self.bot, message):
            if str(message.channel.type) != "voice": return
            if vc.channel != message.channel: return

        self.tts_channel[message.guild.id].message_queue.append(message)

    @commands.command(name="TTS", aliases=["음성채팅입장", "음성입력", "TTS입장", "입장"])
    async def TTS(self, ctx, *input):
        if self.is_allow_guild(ctx) is False: return

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

        if ctx.guild.id not in self.tts_channel.keys():
            self.tts_channel[ctx.guild.id].voice_client = ctx.guild.voice_client
            self.tts_channel[ctx.guild.id].voice_channel = voice_channel
        
        await logs.SendLog(bot=self.bot, log_text=f"{ctx.guild.name}의 {ctx.author.display_name}님이 TTS 명령어를 실행했습니다.")

    
    @commands.command(name="입장이동", aliases=["이동", "음성채널이동"])
    async def 입장이동(self, ctx, *input):
        if self.is_allow_guild(ctx) is False: return

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

        self.tts_channel[ctx.guild.id].voice_client = ctx.guild.voice_client
        self.tts_channel[ctx.guild.id].voice_channel = voice_channel

    @commands.command(name="흑이체")
    async def 흑이체(self, ctx):
        if self.is_allow_guild(ctx) is False: return
        if ctx.author.voice is None:
            return
        
        author_id = ctx.author.id
        self.is_cat[author_id] = not self.is_cat[author_id]

        await ctx.reply(f"흑이체를 {'활성화' if self.is_cat[author_id] else '비활성화'}합니다.", mention_author=False)

    # @commands.command(name="퇴장")
    # async def 퇴장(self, ctx):
    #     if ctx.voice_client is not None:
    #         await ctx.voice_client.disconnect()

    # @staticmethod
    # def co_seong_che(text):
    #     text.replace("ㄹㅇㅋㅋ", "리얼키키").replace("ㅋㅋㄹㅃㅃ", "쿠쿠루삥뽕").replace("")

    def preprocess_text(self, author, text):
        import re
        from emoji import core

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

        return text
    
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
        try:
            author = message.author
            text = self.preprocess_text(author, message.content)

            text_length = len(text)
            max_length = 200

            # 문자열의 길이가 최대 길이보다 크면 return 합니다.
            if text_length > max_length: return False

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
        from google.cloud import texttospeech

        author = message.author
        text = self.preprocess_text(author, message.content)

        # text가 False이면 tts 취소하기
        if text is False: return False

        client = texttospeech.TextToSpeechClient()
        text_length = len(text)
        # 최대 길이를 200으로 지정 (지나치게 길어지면 에러 발생)
        max_length = 200

        # 문자열의 길이가 최대 길이보다 크면 return 합니다.
        if text_length > max_length: return False

        # 텍스트 변환
        input_text = texttospeech.SynthesisInput(text=text)

        # 성별 선택
        gender = "MALE"
        if author.id in [298824090171736074, 369723279167979520, 413315617270136832, 389327234827288576, 317960020912504832, 383483844218585108]:
            gender = "FEMALE"

        gender_info = {
            "MALE": {
                "name" : "ko-KR-Neural2-C",
                "ssml_gender": texttospeech.SsmlVoiceGender.MALE,
                "pitch": 1.2
            },
            "FEMALE": {
                "name" : "ko-KR-Neural2-A",
                "ssml_gender": texttospeech.SsmlVoiceGender.FEMALE,
                "pitch": 4.0
            }
        }

        # 오디오 설정 (예제에서는 한국어, 남성C)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name=gender_info[gender]["name"],
            ssml_gender=gender_info[gender]["ssml_gender"],
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
            pitch=gender_info[gender]["pitch"]
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