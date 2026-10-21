import asyncio
import io
import random
import re
from enum import Enum

import discord
from discord.ext import commands
from emoji import core as emoji_core
from sqlalchemy import and_

import utils.Logs as logs
from utils.database.Database import SessionContext
from utils.database.model.users import Users


class VoiceType(Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    CAT = "BLACKCAT"


# 길드별로 쌓아둘 수 있는 최대 메시지 수 (도배 시 밀린 메시지가 끝없이 읽히는 것을 방지)
MAX_QUEUE_SIZE = 20
# 최대 길이를 200으로 지정 (지나치게 길어지면 에러 발생)
MAX_TEXT_LENGTH = 200
# 재생이 끝났다는 신호가 오지 않을 때 다음 메시지로 넘어가기까지 기다리는 시간(초)
PLAY_TIMEOUT = 60

VOICE_PRESETS = {
    VoiceType.MALE.value: {"name": "ko-KR-Neural2-C", "ssml_gender": "MALE", "pitch": 1.2},
    VoiceType.FEMALE.value: {"name": "ko-KR-Neural2-A", "ssml_gender": "FEMALE", "pitch": 2.0},
}
TEXT_SPEED = [(10, 1.1), (20, 1.2), (40, 1.4)]
DEFAULT_SPEED = 1.5

DISCORD_EMOJI_PATTERN = re.compile(r'<(.*?)>')
# 같은 음성채널에 이름에 이 키워드가 들어간 봇이 있으면 TTS를 비활성화합니다. (TTS가 겹쳐서 두 번 읽히는 것을 방지)
OTHER_TTS_BOT_KEYWORD = "tts"


class TTSError(Exception):
    pass


def parse_voice_type(voice_type):
    """DB의 voice_type 문자열을 (목소리, 흑이체 여부)로 나눕니다. ex) BLACKCATFEMALE -> (FEMALE, True)"""
    if not voice_type:
        return VoiceType.MALE.value, False

    is_cat = voice_type.startswith(VoiceType.CAT.value)
    gender = voice_type[len(VoiceType.CAT.value):] if is_cat else voice_type
    if gender not in VOICE_PRESETS:
        gender = VoiceType.MALE.value
    return gender, is_cat


class TTS:

    def __init__(self, bot):
        self.bot = bot
        self.message_queue: dict[int, asyncio.Queue] = {}
        self.tts_workers: dict[int, asyncio.Task] = {}
        self._tts_client = None

    # ---------- 큐 / 워커 ----------

    def enqueue_tts(self, message):
        """메시지를 길드 큐에 넣고, 해당 길드의 워커가 없으면 시작합니다."""
        guild_id = message.guild.id
        queue = self.message_queue.get(guild_id)
        if queue is None:
            queue = self.message_queue[guild_id] = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)

        worker = self.tts_workers.get(guild_id)
        if worker is None or worker.done():
            self.tts_workers[guild_id] = asyncio.create_task(self._tts_worker(message.guild, queue))

        try:
            queue.put_nowait(message)
        except asyncio.QueueFull:
            pass  # 큐가 가득 차면 새 메시지는 읽지 않습니다.

    def cleanup_tts(self, guild_id):
        worker = self.tts_workers.pop(guild_id, None)
        if worker is not None:
            worker.cancel()
        self.message_queue.pop(guild_id, None)

    def cleanup_all_tts(self):
        for guild_id in list(self.tts_workers):
            self.cleanup_tts(guild_id)

    def has_other_tts_bot(self, channel):
        """음성채널에 이름에 TTS가 들어간 다른 봇이 있으면 True."""
        for member in channel.members:
            if not member.bot or member.id == self.bot.user.id:
                continue
            names = (member.name, member.display_name)
            if any(OTHER_TTS_BOT_KEYWORD in name.lower() for name in names if name):
                return True
        return False

    def tts_should_wait(self, guild):
        """TTS보다 우선하는 작업(ex. 음악 대기열)이 있으면 True. 필요한 쪽에서 오버라이드합니다."""
        return False

    async def _tts_worker(self, guild, queue):
        """큐에 메시지가 들어오는 즉시 깨어나, 한 개씩 합성하고 재생이 끝날 때까지 기다립니다."""
        while True:
            message = await queue.get()
            try:
                audio = await self._synthesize(message)
                if audio is not None:
                    await self._play_audio(guild, audio)
            except asyncio.CancelledError:
                raise
            except TTSError as e:
                await self._send_tts_error(guild, e)
            except Exception as e:
                await logs.send_log(bot=self.bot, log_text=f"{guild.name}에서 {message.content}를 재생 하는데 실패했습니다.\nError: {e}")

    async def _play_audio(self, guild, audio):
        # 음악이 재생 중이거나 대기 중이면 끝날 때까지 기다립니다.
        while True:
            voice_client = guild.voice_client
            if voice_client is None or not voice_client.is_connected():
                return
            # 기다리는 동안 다른 TTS 봇이 들어왔다면 밀린 메시지는 읽지 않습니다.
            if self.has_other_tts_bot(voice_client.channel):
                return
            if not voice_client.is_playing() and not self.tts_should_wait(guild):
                break
            await asyncio.sleep(0.5)

        loop = asyncio.get_running_loop()
        finished = asyncio.Event()

        def after(error):
            # 오디오 스레드에서 호출되므로 이벤트 루프로 넘겨서 set 합니다.
            if error:
                print(f"TTS 재생 오류 : {error}")
            loop.call_soon_threadsafe(finished.set)

        # 임시 파일 없이 메모리의 mp3 바이트를 ffmpeg stdin으로 바로 넘깁니다.
        voice_client.play(discord.FFmpegPCMAudio(io.BytesIO(audio), pipe=True), after=after)
        try:
            await asyncio.wait_for(finished.wait(), timeout=PLAY_TIMEOUT)
        except asyncio.TimeoutError:
            if voice_client.is_playing():
                voice_client.stop()

    async def _send_tts_error(self, guild, error):
        voice_client = guild.voice_client
        if voice_client is None:
            return
        embed = discord.Embed(
            color=0xB22222, title="[ 🚨TTS 오류 ]",
            description=f"아래의 오류가 발생했습니다.\n{error}"
        )
        embed.set_footer(text=f"{self.bot.user.name}", icon_url=self.bot.user.display_avatar)
        await voice_client.channel.send(embed=embed)

    # ---------- 음성 합성 ----------

    async def _synthesize(self, message):
        """메시지를 mp3 바이트로 변환합니다. 읽을 내용이 없으면 None."""
        with SessionContext() as session:
            user = session.query(Users).filter(
                and_(Users.id == message.author.id, Users.guild_id == message.guild.id)).first()
            voice_type = user.voice_type if user is not None else None

        gender, is_cat = parse_voice_type(voice_type)
        text = self.preprocess_text(is_cat, message.content)
        if not text or len(text) > MAX_TEXT_LENGTH:
            return None

        # Google TTS 호출은 네트워크 I/O라 이벤트 루프를 막지 않도록 스레드에서 실행합니다.
        return await asyncio.to_thread(self._request_tts, text, gender)

    def _get_tts_client(self):
        if self._tts_client is None:
            from google.cloud import texttospeech
            self._tts_client = texttospeech.TextToSpeechClient()
        return self._tts_client

    def _request_tts(self, text, gender):
        from google.cloud import texttospeech

        preset = VOICE_PRESETS[gender]
        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name=preset["name"],
            ssml_gender=texttospeech.SsmlVoiceGender[preset["ssml_gender"]],
        )

        speed = DEFAULT_SPEED
        for length, sp in TEXT_SPEED:
            if len(text) <= length:
                speed = sp
                break

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speed,
            pitch=preset["pitch"]
        )

        try:
            response = self._get_tts_client().synthesize_speech(
                request={"input": texttospeech.SynthesisInput(text=text), "voice": voice, "audio_config": audio_config}
            )
        except Exception as e:
            raise TTSError(e) from e
        return response.audio_content

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

                for _ in range(l - 1):
                    l -= 1
                    res += "오"

                res += "옹"
            trans_text.append(res)
        return " ".join(trans_text)

    def preprocess_text(self, is_cat, text):
        # 1. 이모지를 먼저 제거합니다.
        text = emoji_core.replace_emoji(text, replace="")

        # 2. 남은 텍스트에서 디스코드 이모지 문자열 <:이모지:> 을 제거합니다.
        text = DISCORD_EMOJI_PATTERN.sub("", text).strip()

        # 모두 제거 후, 문자열이 공백이면 읽지 않습니다.
        if text == "":
            return None

        # 흑이체 사용할 대상
        if is_cat:
            text = self.cat_speech(text)

        return text

    # ---------- 명령어 ----------

    @staticmethod
    def _get_or_create_user(session, member):
        user = session.query(Users).filter(
            and_(Users.id == member.id, Users.guild_id == member.guild.id)).first()
        if user is None:
            user = Users(_id=member.id, guild_id=member.guild.id, username=member.display_name)
            session.add(user)
        return user

    async def _set_voice(self, ctx, gender):
        if ctx.author.voice is None:
            return False

        with SessionContext() as session:
            user = self._get_or_create_user(session, ctx.author)
            _, is_cat = parse_voice_type(user.voice_type)
            # 목소리만 바꾸고 흑이체 설정은 유지합니다.
            user.voice_type = f"{VoiceType.CAT.value}{gender}" if is_cat else gender
            session.commit()
        return True

    @commands.command(name="남자", aliases=["남성", "남성TTS"])
    async def 남자TTS(self, ctx):
        if await self._set_voice(ctx, VoiceType.MALE.value):
            await ctx.reply(f"TTS 목소리를 남성으로 변경합니다.", mention_author=False)

    @commands.command(name="여자", aliases=["여성", "여성TTS"])
    async def 여자TTS(self, ctx):
        if await self._set_voice(ctx, VoiceType.FEMALE.value):
            await ctx.reply(f"TTS 목소리를 여성으로 변경합니다.", mention_author=False)

    @commands.command(name="흑이체")
    async def 흑이체(self, ctx):
        if ctx.author.voice is None:
            return

        with SessionContext() as session:
            user = self._get_or_create_user(session, ctx.author)
            gender, is_cat = parse_voice_type(user.voice_type)
            is_active = not is_cat
            user.voice_type = f"{VoiceType.CAT.value}{gender}" if is_active else gender
            session.commit()

        await ctx.reply(f"흑이체를 {'활성화' if is_active else '비활성화'}합니다.", mention_author=False)
