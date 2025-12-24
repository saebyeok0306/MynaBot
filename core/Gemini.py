import asyncio
import copy
import io
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands, Interaction
from discord.ext import commands
from dotenv import dotenv_values
from google import genai
from google.genai import types
from sqlalchemy import and_

import utils.Logs as logs
import utils.Utility as util
from main import MynaBot
from utils.database.Database import SessionContext
from utils.database.model.chats import Chats

through_prompt = """## 역할
당신은 사용자의 입력(Prompt)을 분석하여, 사용자가 '이미지 생성(Image Generation)'을 요청하는 것인지 아니면 '텍스트 응답(Text Response)'을 원하는 것인지 판별하는 분류기입니다.
만약 사용자의 의도가 불분명하다면(예: '사과가 뭐야?'), 기본적으로 TEXT_ONLY로 분류하십시오.

## 판단 기준
1. **이미지 생성 (IMAGE_GEN):**
   - "~ 그려줘", "~ 만들어줘", "~ 이미지 보여줘" 등의 직접적인 요청.
   - 스타일, 구도, 색상, 피사체 등 시각적 묘사가 구체적으로 포함된 경우.
   - 사진, 그림, 포스터, 로고, 캐릭터 등을 요구하는 경우.

2. **텍스트 응답 (TEXT_ONLY):**
   - 질문에 대한 답변, 설명, 요약, 번역 요청.
   - 코드 작성, 시 작성, 이메일 작성 등 텍스트 기반 결과물 요청.
   - 단순한 사실 확인이나 대화.

## 출력 형식
오직 아래의 JSON 형식으로만 답변하세요. 다른 설명은 생략합니다.
{
  "intent": "IMAGE_GEN" 또는 "TEXT_ONLY",
  "reason": "판단 근거 요약",
  "confidence": 0.0~1.0 (확신도)
}"""


class Chat:
    def __init__(self):
        self.runtime = False
        self.history = None  # list
        self.database = []
        self.channel = None  # channel
        self.userdata = None  # ctx.author
        self.dm = None  # channel

    def print(self):
        return f"Runtime : {self.runtime}\nHistory : {self.history}\nDatabase : {self.database}\nChannel : {self.channel}"

    def makeChatRecord(self) -> discord.File:
        with open('text.txt', 'w', encoding='utf-8') as l:
            l.write(f"{self.userdata.display_name}님과의 대화내역")
            for line in self.database:
                talk_name = self.userdata.display_name if line['role'] == 'user' else '마이나봇'
                talk_content = line['content']
                if isinstance(talk_content, list) and len(talk_content) > 1:
                    print(talk_content)
                    talk_content = util.merge_type_text(talk_content)
                l.write(
                    f"\n{talk_name} : {talk_content}")
        return discord.File("text.txt")


class Gemini(commands.Cog):
    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.chat_room = defaultdict(Chat)  # runtime, history, channel
        self.support_image = ["png", "jpeg", "jpg", "webp", "gif"]
        self.support_audio = ["wav", "mp3", "ogg", "aac"]
        self.support_video = ["mp4", "mpeg", "mov", "avi", "flv", "mpg", "webm", "wmv"]
        self.support_application = ["pdf", "json", "xml"]
        self.max_token = 10000
        self.dolar_to_won = 1450
        self.cost = {
            "gemini-3-flash-preview": {
                "input": (0.5 * self.dolar_to_won) / 1000000,
                "output": (3.0 * self.dolar_to_won) / 1000000
            },
            "gemini-2.5-flash-image": {
                "input": (0.3 * self.dolar_to_won) / 1000000,
                "output": (2.5 * self.dolar_to_won) / 1000000
            }
        }
        self.system_msg = "당신은 '마이나'라는 이름의 챗봇입니다. 당신의 개발자는 '갈대'입니다. 사용자의 요구가 따로 있는게 아니라면 존댓말을 사용합니다."
        self.through_msg = through_prompt

        self.usage_list = {}
        self.API_USER_LIMIT = 10
        self.API_DAILY_LIMIT = 1000
        try:
            with open("system.message.txt", "r", encoding="UTF-8") as f:
                system_msgs = f.readlines()
                for system_msg in system_msgs:
                    self.system_msg += f" {system_msg.rstrip()}"
        except:
            pass

    def cog_unload(self):
        pass

    @staticmethod
    def hide_string(input_string):
        # 입력 문자열의 길이를 확인합니다.
        length = len(input_string)

        # 문자열에서 원하는 비율 포인트를 계산합니다.
        point = int(length * 0.65)

        # '*'로 대체한 결과를 생성합니다.
        hidden_string = input_string[:length - point] + '*' * point

        return hidden_string

    @staticmethod
    def create_key(id, guild_id):
        return id + guild_id

    def create_chat_unique_key(self, author: discord.Member):
        id = author.id
        guild_id = author.guild.id

        return self.create_key(id, guild_id)

    async def create_dm(self, interaction: Interaction[MynaBot], key=None):
        if key is None:
            key = self.create_chat_unique_key(interaction.user)

        can_dm = self.chat_room[key].dm
        if can_dm is None or can_dm is False:
            try:
                self.chat_room[key].dm = await interaction.user.create_dm()
            except:
                self.chat_room[key].dm = False

    def check_usage(self, user_id: str) -> bool:
        user_usage = self.usage_list.get(user_id)
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst)

        if user_usage is None:
            self.usage_list[user_id] = {"cnt": 1, "date": now, "can_date": now + timedelta(hours=3)}
            return True

        can_date = user_usage["can_date"]
        if can_date >= now:
            if user_usage["cnt"] < self.API_USER_LIMIT:
                user_usage["cnt"] += 1
                return True
            else:
                return False
        else:
            self.usage_list[user_id] = {"cnt": 1, "date": now, "can_date": now + timedelta(hours=3)}
            return True

    def to_genai_content(self, content: list) -> list[types.Content]:
        result = []
        for c in content:
            parts = [types.Part.from_text(text=c["content"])]
            if c.get("file"):
                parts.append(types.Part.from_uri(file_uri=c["file"]["url"], mime_type=c["file"]["mime_type"]))
            result.append(types.Content(role=c["role"], parts=parts))

        return result

    def through_gemini(self, user_message, model="gemini-3-flash-preview"):
        config = dotenv_values('.env')
        client = genai.Client(api_key=config["GOOGLE_API_KEY"])

        response = client.models.generate_content(
            model=model,
            config=types.GenerateContentConfig(system_instruction=self.through_msg),
            contents=user_message
        )

        # usage = response.usage_metadata
        intent = "TEXT_ONLY"
        reason = ""

        try:
            result = json.loads(response.text)
            print(result)

            parse_intent = result.get("intent", "TEXT_ONLY")
            if parse_intent.startswith("IMAGE"):
                intent = "IMAGE_GEN"

            reason = result.get("reason", "")

        except Exception:
            pass

        return {"intent": intent, "reason": reason}

    def get_cost_message(self, model:str, usage_metadata: types.GenerateContentResponseUsageMetadata, remain_usage=None):
        input_token = 0
        output_token = 0

        if usage_metadata is not None:
            input_token = usage_metadata.prompt_token_count or 0
            candidates_token_count = usage_metadata.candidates_token_count or 0
            thoughts_token_count = usage_metadata.thoughts_token_count or 0
            output_token = (candidates_token_count + thoughts_token_count) or 0

        total_token = input_token + output_token

        model_cost = self.cost[model]
        input_won = round(model_cost["input"] * input_token, 4)
        output_won = round(model_cost["output"] * output_token, 4)
        total_won = round(input_won + output_won, 4)
        message = f"\n> -# {model}:{total_won}￦을 사용했어요."  # {input_token}+{output_token}({total_token})토큰,
        if model.find("image") != -1:
            message += " (이미지 생성 비용은 제외됨)"

        if remain_usage is not None:
            message += f"\n> -# 남은 사용량이 {remain_usage}회 남았습니다."

        return {
            "message": message,
            "input_token": input_token,
            "output_token": output_token,
            "total_token": total_token
        }


    async def call_nanobanana(self, interaction: Interaction[MynaBot], message: discord.Message, system_message, record_message,
                              deleted_record=None, remain_usage=None, model="gemini-2.5-flash-image"):
        try:
            config = dotenv_values('.env')
            client = genai.Client(api_key=config["GOOGLE_API_KEY"])

            response = client.models.generate_content(
                model=model,
                contents=record_message
            )

            usage_result = self.get_cost_message(model, response.usage_metadata, remain_usage)
            used_record_text = usage_result.get("message", "")
            if deleted_record:
                used_record_text += f" (대화 {deleted_record}개 삭제됨)"

            await message.edit(content=f"{interaction.user.display_name}님의 질문에 해당하는 답변이에요.{used_record_text}")

            image_url = None
            for part in response.parts:
                if part.text:
                    await message.edit(content=f"{part.text}{used_record_text}")

                if part.inline_data:
                    image_raw = part.inline_data.data
                    with io.BytesIO(image_raw) as image_binary:
                        # discord.File 객체 생성 (filename 확장자를 지정해야 디스코드에서 이미지로 인식함)
                        discord_file = discord.File(fp=image_binary, filename="generated_banana.png")

                        message2 = await interaction.followup.send(file=discord_file)
                        if message2.attachments:
                            image_url = message2.attachments[0].url

            return {
                "collected_message": f"{image_url} (디스코드의 보안 정책(Cdn 인증)으로 인해, 메시지 첨부파일의 URL은 일정 시간이 지나면 만료될 수 있습니다)",
                "input_token": usage_result.get("input_token", 0),
                "output_token": usage_result.get("output_token", 0),
                "total_token": usage_result.get("total_token", 0)
            }
        except Exception as e:
            await message.edit(content=f"죄송합니다, 처리 중에 오류가 발생했어요.\n{e}")
        return False

    async def call_gemini(self, interaction: Interaction[MynaBot], message: discord.Message, system_message, user_message,
                          deleted_record=None, model="gemini-3-flash-preview", content_type=None, content=None):
        timeout_sec = 20
        isLong = False
        collected_message = ""

        final_reason = None
        last_usage: types.GenerateContentResponseUsageMetadata = None

        try:
            async def timeout(sec, request_task):
                nonlocal collected_message
                _sec = sec // 4
                for _ in range(4):
                    await asyncio.sleep(_sec)
                    if collected_message != "":
                        return True

                if collected_message == "":
                    request_task.cancel()
                    return False
                return True

            async def call_gemini(_model: str, _config: types.GenerateContentConfig, _contents: list):
                nonlocal message, isLong, collected_message, final_reason, last_usage

                config = dotenv_values('.env')
                client = genai.Client(api_key=config["GOOGLE_API_KEY"])

                response = client.models.generate_content_stream(
                    model=_model,
                    config=_config,
                    contents=_contents
                )

                cnt = 0
                for chunk in response:
                    cnt += 1
                    try:
                        chunk_message = chunk.text or ""
                        collected_message += chunk_message
                        if isLong is False:
                            if len(collected_message) >= 2000:
                                isLong = True
                                await message.edit(content="답변이 너무 길어서 파일로 올릴게요.")
                            if cnt > 10:
                                cnt = 0
                                await message.edit(content=collected_message)
                    except Exception as e:
                        await logs.send_log(self.bot, f"Gemini API 요청 중 오류가 발생했습니다.\n{e}")
                        pass

                    if chunk.candidates:
                        final_reason = chunk.candidates[0].finish_reason
                    if chunk.usage_metadata:
                        last_usage = chunk.usage_metadata
                return True

            config = types.GenerateContentConfig(system_instruction=system_message)

            request_task = asyncio.create_task(call_gemini(model, config, user_message))
            timeout_task = asyncio.create_task(timeout(timeout_sec, request_task))
            _, result = await asyncio.gather(timeout_task, request_task)

            usage_result = self.get_cost_message(model, last_usage)

            used_record_text = usage_result.get("message", "")
            if deleted_record:
                used_record_text += f" (대화 {deleted_record}개 삭제됨)"

            if not isLong and len(collected_message + used_record_text) >= 2000:
                isLong = True
                # await msg.edit(content="답변이 너무 길어서 파일로 올릴게요.")

            if isLong is False:
                # await interaction.response.send_message(f"{collected_message}{used_record_text}")
                await message.edit(content=collected_message + used_record_text)
            else:
                with open('result.txt', 'w', encoding='utf-8') as l:
                    l.write(collected_message)
                file = discord.File("result.txt")
                await message.edit(content=f"{interaction.user.display_name}님의 질문에 해당하는 답변이에요.{used_record_text}")
                await interaction.followup.send(file=file)

            if content is not None:
                await interaction.followup.send(content=f"첨부해주셨던 파일입니다: {content.url}")

            return {
                "collected_message": collected_message,
                "input_token": usage_result.get("input_token", 0),
                "output_token": usage_result.get("output_token", 0),
                "total_token": usage_result.get("total_token", 0)
            }

        except asyncio.CancelledError as e:
            await message.edit(content=f"죄송합니다, {timeout_sec}초 동안 응답이 없어서 종료했어요.\n명령을 다시 시도해주세요!")

        except Exception as e:
            await message.edit(content=f"죄송합니다, 처리 중에 오류가 발생했어요.\n`!초기화` 명령어로 대화내역을 초기화해주세요!\n{e}")

        return False

    async def clean_database(self, interaction: Interaction[MynaBot], key=None):
        if key is None:
            key = self.create_chat_unique_key(interaction.user)
        room = self.chat_room[key]

        if len(room.database) >= 40:
            await self.create_dm(interaction, key=key)
            if room.dm:
                # dm이 있는 경우
                try:
                    await room.dm.send(f"{interaction.user.display_name}님과의 대화기록입니다.")
                    await room.dm.send(file=room.makeChatRecord())
                    await interaction.followup.send(f"저장된 대화기록이 너무 많아서 초기화했어요!\n마이나와 대화 중인 내용은 여전히 유효해요.", ephemeral=True)
                except:
                    room.dm = False
                    await interaction.followup.send(f"저장된 대화기록이 너무 많아서 초기화했어요!\n마이나와 대화 중인 내용은 여전히 유효해요.", ephemeral=True)
                    await room.channel.send(file=room.makeChatRecord())
            else:
                # dm이 없는 경우
                await interaction.followup.send(f"저장된 대화기록이 너무 많아서 초기화했어요!\n마이나와 대화 중인 내용은 여전히 유효해요.", ephemeral=True)
                await room.channel.send(file=room.makeChatRecord())

            history_count = len(room.history)
            self.chat_room[key].database = room.database[-history_count:]

    def history_queue(self, interaction: Interaction[MynaBot], key=None):
        if key is None:
            key = self.create_chat_unique_key(interaction.user)
        room = self.chat_room[key]
        total_token = 0
        tokens = []
        rev_cnt = 0

        length = len(room.history)
        for idx in range(length):
            content = room.history[idx]
            _token = content.get("token", 0)
            total_token += _token
            tokens.append(_token)

        while total_token > self.max_token and len(room.history) > 0:
            record = room.history.pop()
            _token = tokens.pop()
            total_token -= _token
            rev_cnt += 1
            print(f"기록이 삭제됩니다. {_token}토큰, {record}")

        return rev_cnt, total_token

    # @commands.command(name="마이나야", aliases=["검색"])
    @app_commands.command(description='Gemini를 활용하여 질문을 합니다.')
    @app_commands.describe(message="질문할 내용을 입력합니다.", file="파일도 함께 첨부하여 질문할 수 있습니다.")
    async def 마이나야(self, interaction: Interaction[MynaBot], message: str, file: discord.Attachment = None):
        allowed_user = util.is_allow_user_interaction(interaction, util.ROLE_TYPE.GEMINI)
        allowed_guild = util.is_allow_guild_interaction(interaction, util.GUILD_COMMAND_TYPE.GEMINI)

        if allowed_user is False and allowed_guild is False:
            await interaction.response.send_message(f"관리자가 허용한 서버만 Gemini 명령어를 사용할 수 있어요.", ephemeral=True)
            return

        if util.is_allow_channel_interaction(self.bot, interaction) is False:
            await util.is_not_allow_channel_interaction(interaction, util.current_function_name())
            return

        await interaction.response.defer()

        key = self.create_chat_unique_key(interaction.user)
        if key not in self.chat_room:
            # 대화 기록이 없을 때
            self.chat_room[key].userdata = interaction.user

        if self.chat_room[key].runtime is True:
            await interaction.followup.send("죄송합니다, 질문은 하나씩만 답변가능해요.\n이전 질문에 대한 답변이 완료되었을 때 시도해주세요.")
            return False

        model = "gemini-3-flash-preview"
        # if 'gpt4' in message and util.is_allow_user_interaction(interaction, util.ROLE_TYPE.GPT4):
        #     model = "gpt-4o"

        record_message = {"role": "user", "content": f"{message}"}
        request_parts = [types.Part.from_text(text=message)]
        total_token = 0
        remove_cnt = 0

        through_message = [types.Content(role="user", parts=copy.deepcopy(request_parts))]

        if file:
            print(file.content_type)
            content_type = file.content_type.split(";")[0]
            record_message["file"] = []
            if content_type.startswith("image"):
                if content_type.split("/")[1] not in self.support_image:
                    await interaction.followup.send(f"현재 마이나는 {', '.join(self.support_image)} 확장자만 지원해요.")
                    return
                request_parts.append(types.Part.from_uri(file_uri=file.url, mime_type=content_type))
                record_message["file"].append({"url": file.url, "mime_type": content_type})

            elif content_type.startswith("application"):
                if content_type.split("/")[1] not in self.support_application:
                    await interaction.followup.send(f"현재 마이나는 {', '.join(self.support_application)} 확장자만 지원해요.")
                    return
                request_parts.append(types.Part.from_uri(file_uri=file.url, mime_type=content_type))
                record_message["file"].append({"url": file.url, "mime_type": content_type})

            elif content_type.startswith("text"):
                request_parts.append(types.Part.from_uri(file_uri=file.url, mime_type=content_type))
                record_message["file"].append({"url": file.url, "mime_type": content_type})

            else:
                await interaction.followup.send(f"현재 마이나가 지원하는 확장자는 아래와 같습니다.\n-# {', '.join(self.support_image)}, {', '.join(self.support_application)}, txt 등")
                return

        request_message = types.Content(role="user", parts=request_parts)

        self.chat_room[key].channel = interaction.channel
        self.chat_room[key].runtime = True

        user_message = []

        # History
        if self.chat_room[key].history:
            remove_cnt, total_token = self.history_queue(interaction, key=key)
            user_message.extend(self.to_genai_content(self.chat_room[key].history))

        user_message.append(request_message)
        system_message = self.system_msg + f" 당신과 대화 중인 사람의 이름은 '{interaction.user.display_name}'입니다. 참고하세요."
        msg = await interaction.followup.send("네, 잠시만 기다려주세요...")


        through_result = self.through_gemini(through_message)
        through_intent = through_result.get("intent")
        through_reason = through_result.get("reason")
        await msg.edit(content=f"네, 잠시만 기다려주세요...\n-# 마이나가 해당 요청을 {'질문' if through_intent == 'TEXT_ONLY' else '이미지 생성'}으로 처리했어요.\n-# {through_reason}")

        # Run Gemini
        res = None
        if through_intent == "TEXT_ONLY":
            try:
                res = await self.call_gemini(
                    interaction=interaction, message=msg, user_message=user_message, system_message=system_message, deleted_record=remove_cnt,
                    model=model, content_type=file.content_type if file else None, content=file if file else None)
                if res is False:
                    self.chat_room[key].runtime = False
                    return

            except Exception as e:
                print("Gemini Running Error : ", e)
                self.chat_room[key].runtime = False
                await msg.edit(content=f"죄송합니다, 처리 중에 오류가 발생했어요.\n{e}")
                return
        elif through_intent == "IMAGE_GEN":
            is_usage = self.check_usage(key)
            user_usage = self.usage_list[key]
            can_date = user_usage["can_date"]

            if is_usage:
                remain_usage = self.API_USER_LIMIT - user_usage["cnt"]
                try:
                    res = await self.call_nanobanana(
                        interaction=interaction, message=msg, record_message=message, system_message=system_message,
                        deleted_record=remove_cnt, remain_usage=remain_usage)
                    if res is False:
                        self.chat_room[key].runtime = False
                        return

                except Exception as e:
                    print("NanoBanana Running Error : ", e)
                    self.chat_room[key].runtime = False
                    await msg.edit(content=f"죄송합니다, 처리 중에 오류가 발생했어요.\n{e}")
                    return
            else:
                await msg.edit(content=f"죄송합니다, {interaction.user.display_name}님에게 부여된 사용량이 모두 소진되었습니다.\n -# {can_date.strftime('%Y.%m.%d %H:%M:%S')}에 제한이 풀립니다.")

        record_message["token"] = res["input_token"]

        response_message = {"role": "model", "content": res["collected_message"], "token": res["output_token"]}
        if self.chat_room[key].history is None:
            self.chat_room[key].history = []
        self.chat_room[key].history.extend([record_message, response_message])
        self.chat_room[key].database.extend([record_message, response_message])
        self.chat_room[key].runtime = False

        await self.clean_database(interaction, key=key)
        # self.save_chat_data(interaction)

        await logs.send_log(bot=self.bot,
                            log_text=f"{interaction.guild.name}의 {interaction.user.display_name}님이 Gemini 명령어를 실행했습니다.")

    @commands.command(name="초기화", aliases=["리셋"])
    async def 초기화(self, ctx, *input):
        allowed_user = util.is_allow_user(ctx, util.ROLE_TYPE.GEMINI)
        allowed_guild = util.is_allow_guild(ctx, util.GUILD_COMMAND_TYPE.GEMINI)

        if allowed_user is False and allowed_guild is False:
            msg = await ctx.reply(f"관리자가 허용한 서버만 ChatGPT 명령어를 사용할 수 있어요.", mention_author=True)
            await msg.delete(delay=5)
            await ctx.message.delete(delay=5)
            return

        if util.is_allow_channel(self.bot, ctx) is False:
            await util.is_not_allow_channel(ctx, util.current_function_name())
            return

        key = self.create_chat_unique_key(ctx.author)
        if key in self.chat_room:
            await self.create_dm(ctx, key=key)
            room = self.chat_room[key]
            if room.channel is None: room.channel = ctx.channel
            if room.dm:
                # dm이 있는 경우
                try:
                    await room.dm.send(file=room.makeChatRecord())
                except:
                    # dm 전송에 실패한 경우
                    await room.channel.send(file=room.makeChatRecord())
            else:
                # dm이 없는 경우
                await room.channel.send(file=room.makeChatRecord())
            await ctx.reply(f"{ctx.author.display_name}님과의 대화내역이 초기화되었어요.")
            del self.chat_room[key]
            with SessionContext() as session:
                delete_chat = session.query(Chats).filter(
                    and_(Chats.id == ctx.author.id, Chats.guild_id == ctx.author.guild.id)).first()
                if delete_chat:
                    session.delete(delete_chat)
                    session.commit()
            # db.DeleteChatByAuthor(ctx.author)
        else:
            msg = await ctx.reply(f"{ctx.author.display_name}님과의 대화내역이 없어요.")
            await msg.delete(delay=5)
            await ctx.message.delete(delay=5)

    @commands.command(name="대화목록", aliases=["대화리스트"])
    async def 대화목록(self, ctx, *input):
        allowed_user = util.is_allow_user(ctx, util.ROLE_TYPE.GEMINI)
        allowed_guild = util.is_allow_guild(ctx, util.GUILD_COMMAND_TYPE.GEMINI)

        if allowed_user is False and allowed_guild is False:
            msg = await ctx.reply(f"관리자가 허용한 서버만 ChatGPT 명령어를 사용할 수 있어요.", mention_author=True)
            await msg.delete(delay=5)
            await ctx.message.delete(delay=5)
            return

        if util.is_allow_channel(self.bot, ctx) is False:
            await util.is_not_allow_channel(ctx, util.current_function_name())
            return

        cnt = len(self.chat_room.keys())
        if cnt:
            text = f"현재 생성된 대화방은 "
            for idx, key in enumerate(self.chat_room):
                text += f"{self.chat_room[key].userdata.display_name}(`{self.hide_string(self.chat_room[key].userdata.guild.name)}`)님"
                if idx != cnt - 1: text += ", "
            text += f"이 있고 총 {cnt}개의 방이 있습니다."
            await ctx.reply(text)
        else:
            text = f"현재 생성된 대화방이 없습니다."
            msg = await ctx.reply(text)
            await msg.delete(delay=5)
            await ctx.message.delete(delay=5)

    @commands.command(name="대화내역", aliases=["대화기록", "대화내용"])
    async def 대화내역(self, ctx, *input):
        allowed_user = util.is_allow_user(ctx, util.ROLE_TYPE.GEMINI)
        allowed_guild = util.is_allow_guild(ctx, util.GUILD_COMMAND_TYPE.GEMINI)

        if allowed_user is False and allowed_guild is False:
            msg = await ctx.reply(f"관리자가 허용한 서버만 Gemini 명령어를 사용할 수 있어요.", mention_author=True)
            await msg.delete(delay=5)
            await ctx.message.delete(delay=5)
            return

        if util.is_allow_channel(self.bot, ctx) is False:
            await util.is_not_allow_channel(ctx, util.current_function_name())
            return

        key = self.create_chat_unique_key(ctx.author)
        if key not in self.chat_room:
            msg = await ctx.reply(f"마이나와 대화한 내역이 없어요!\n`!마이나야 [질문]`을 통해 말을 걸어보세요.")
            return

        await self.create_dm(ctx, key=key)
        room = self.chat_room[key]
        if room.channel is None: room.channel = ctx.channel
        if room.dm:
            # dm이 있는 경우
            try:
                await room.dm.send(f"{ctx.author.display_name}님과의 대화기록입니다.")
                await room.dm.send(file=room.makeChatRecord())
                await ctx.reply(f"개인메시지로 대화기록을 전송했어요!", mention_author=False)
            except:
                room.dm = False
                await ctx.reply(f"{ctx.author.display_name}님과의 대화기록입니다.", mention_author=False)
                await room.channel.send(file=room.makeChatRecord())
        else:
            # dm이 없는 경우
            await ctx.reply(f"{ctx.author.display_name}님과의 대화기록입니다.", mention_author=False)
            await room.channel.send(file=room.makeChatRecord())


async def setup(bot):
    await bot.add_cog(Gemini(bot))
