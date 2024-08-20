from collections import defaultdict

import asyncio
import discord
import json
import openai
import tiktoken
from discord import app_commands, Interaction
from discord.ext import commands
from dotenv import dotenv_values
from sqlalchemy import and_

import utils.Logs as logs
import utils.Utility as util
from main import MynaBot
from utils.database.Database import SessionContext
from utils.database.model.chats import Chats


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
                l.write(
                    f"\n{f'{self.userdata.display_name}' if line['role'] == 'user' else '마이나봇'} : {line['content']}")
        return discord.File("text.txt")


class ChatGPT(commands.Cog):
    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.chat_room = defaultdict(Chat)  # runtime, history, channel
        self.support_image = ["png", "jpeg", "webp", "gif"]
        self.encoding = tiktoken.encoding_for_model("gpt-4o")
        self.max_token = 3500
        self.dolar_to_won = 1380
        self.cost = {
            "gpt-3.5-turbo": {
                "input": (0.5 * self.dolar_to_won) / 1000000,
                "output": (1.5 * self.dolar_to_won) / 1000000
            },
            "gpt-4o": {
                "input": (5.0 * self.dolar_to_won) / 1000000,
                "output": (15.0 * self.dolar_to_won) / 1000000
            },
            "gpt-4o-mini": {
                "input": (0.15 * self.dolar_to_won) / 1000000,
                "output": (0.6 * self.dolar_to_won) / 1000000
            },
            "gpt-4-turbo": {
                "input": (10.0 * self.dolar_to_won) / 1000000,
                "output": (30.0 * self.dolar_to_won) / 1000000
            }
        }
        self.system_msg = [
            {"role": "system", "content": "You are a chatbot named '마이나'."},
            {"role": "system", "content": "Your developer is '갈대'."},
            {"role": "system", "content": "You must answer in Korean only."},
        ]
        try:
            with open("system.message.txt", "r", encoding="UTF-8") as f:
                system_msgs = f.readlines()
                for system_msg in system_msgs:
                    msg = {"role": "system", "content": system_msg.rstrip()}
                    self.system_msg.append(msg)
        except:
            pass

        self.restore_chat_data()

    def cog_unload(self):
        pass

    def get_system_msg_index(self, interaction: Interaction[MynaBot], key=None):
        if key is None:
            key = self.create_chat_unique_key(interaction.user)
        room = self.chat_room[key]

        for idx, msg in enumerate(room.history):
            if msg["role"] != "system":
                return idx - 1

        return False

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

    def save_chat_data(self, interaction: Interaction[MynaBot], key=None):
        if key is None:
            key = self.create_chat_unique_key(interaction.user)
        room = self.chat_room[key]
        history = str(json.dumps({"data": room.history}, ensure_ascii=False))
        database = str(json.dumps({"data": room.database}, ensure_ascii=False))
        # db.SaveChatDB(ctx.author, history, database)
        # cur.execute("UPDATE Chat SET history=?, data=? WHERE id=? AND guild_id=? ", (history, database, *author_id))
        with SessionContext() as session:
            prev_chat = session.query(Chats).filter(
                and_(Chats.id == interaction.user.id, Chats.guild_id == interaction.user.guild.id)).first()
            if prev_chat:
                prev_chat.history = history
                prev_chat.data = database
                session.add(prev_chat)
            else:
                new_chat = Chats(_id=interaction.user.id, guild_id=interaction.user.guild.id, history=history, data=database)
                session.add(new_chat)
            session.commit()

    def restore_chat_data(self):
        with SessionContext() as session:
            res = session.query(Chats).all()
            if res is None: return False

        for _res in res:
            id = _res.id
            guild_id = _res.guild_id
            history = _res.history
            database = _res.data

            history = json.loads(history)
            database = json.loads(database)

            guild = self.bot.get_guild(guild_id)
            author = guild.get_member(id)

            key = self.create_key(id, guild_id)
            self.chat_room[key].userdata = author
            self.chat_room[key].history = history["data"]
            self.chat_room[key].database = database["data"]

    async def create_dm(self, interaction: Interaction[MynaBot], key=None):
        if key is None:
            key = self.create_chat_unique_key(interaction.user)

        can_dm = self.chat_room[key].dm
        if can_dm is None or can_dm is False:
            try:
                self.chat_room[key].dm = await interaction.user.create_dm()
            except:
                self.chat_room[key].dm = False

    async def call_chat_gpt(
            self, interaction: Interaction[MynaBot], msg, user_message, prompt, token=0, cnt=None, model="gpt-4o-mini",
            content_type=None, content=None):
        timeout_sec = 20
        isLong = False
        collected_message = ""

        try:
            async def timeout(sec, request_task):
                nonlocal msg, collected_message
                _sec = sec // 4
                for _ in range(4):
                    await asyncio.sleep(_sec)
                    if collected_message != "":
                        return True

                if collected_message == "":
                    request_task.cancel()
                    return False
                return True

            async def requestOpenAPI(prompt, model_engine):
                nonlocal msg, isLong, collected_message

                config = dotenv_values('.env')
                client = openai.AsyncOpenAI(api_key=config["OpenAI_Secret"])
                try:
                    completion = await client.chat.completions.create(
                        model=model_engine,
                        messages=prompt,
                        temperature=0.4,
                        stream=True,
                        # request_timeout=60,
                    )
                except Exception as e:
                    await logs.send_log(self.bot, f"ChatGPT API 요청 중 오류가 발생했습니다.\n{e}")
                    return False

                cnt = 0
                async for chunk in completion:
                    cnt += 1
                    try:
                        chunk_message = chunk.choices[0].delta.content or ""
                        collected_message += chunk_message
                        if isLong is False:
                            if len(collected_message) >= 2000:
                                isLong = True
                                await msg.edit(content="답변이 너무 길어서 파일로 올릴게요.")
                            if cnt > 16:
                                cnt = 0
                                await msg.edit(content=collected_message)
                    except Exception as e:
                        await logs.send_log(self.bot, f"ChatGPT API 요청 중 오류가 발생했습니다.\n{e}")
                        pass
                return True

            request_task = asyncio.create_task(requestOpenAPI(prompt, model))
            timeout_task = asyncio.create_task(timeout(timeout_sec, request_task))
            _, result = await asyncio.gather(timeout_task, request_task)

            if result is False:
                await msg.edit(content=f"죄송합니다, 처리 중에 오류가 발생했어요.\n`!초기화` 명령어로 대화내역을 초기화해주세요!")
                return False

            if content:
                if content_type.startswith("image"):
                    collected_message += f"\n{content.url}\n"

            input_token = len(self.encoding.encode(user_message)) + token
            output_token = len(self.encoding.encode(collected_message))
            total_token = input_token + output_token
            model_cost = self.cost[model]
            input_won = round(model_cost["input"] * input_token, 4)
            output_won = round(model_cost["output"] * output_token, 4)
            total_won = round(input_won + output_won, 4)
            used_record_text = f"\n> `{model}:{total_won}￦을 사용했어요."  # {input_token}+{output_token}({total_token})토큰,
            if cnt == 0:
                used_record_text += "`"
            else:
                used_record_text += f" (대화 {cnt}개 삭제됨)`"

            if not isLong and len(collected_message + used_record_text) >= 2000:
                isLong = True
                # await msg.edit(content="답변이 너무 길어서 파일로 올릴게요.")

            if isLong is False:
                # await interaction.response.send_message(f"{collected_message}{used_record_text}")
                await msg.edit(content=collected_message + used_record_text)
            else:
                with open('result.txt', 'w', encoding='utf-8') as l:
                    l.write(collected_message)
                file = discord.File("result.txt")
                await msg.edit(content=f"{interaction.user.display_name}님의 질문에 해당하는 답변이에요.{used_record_text}")
                await interaction.response.send_message(file=file)

            return {
                "collected_message": collected_message,
                "input_token": input_token,
                "output_token": output_token,
                "total_token": total_token
            }

        except asyncio.CancelledError as e:
            await msg.edit(content=f"죄송합니다, {timeout_sec}초 동안 응답이 없어서 종료했어요.\n명령을 다시 시도해주세요!")
        except Exception as e:
            await msg.edit(content=f"죄송합니다, 처리 중에 오류가 발생했어요.\n`!초기화` 명령어로 대화내역을 초기화해주세요!\n{e}")

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
                    # await ctx.reply(f"저장된 대화기록이 너무 많아서 초기화했어요!\n마이나와 대화 중인 내용은 여전히 유효해요.", mention_author=False)
                except:
                    room.dm = False
                    await interaction.followup.send(f"저장된 대화기록이 너무 많아서 초기화했어요!\n마이나와 대화 중인 내용은 여전히 유효해요.", ephemeral=True)
                    # await ctx.reply(
                    #     f"{ctx.author.display_name}님과의 대화기록입니다. 저장된 대화기록이 너무 많아서 초기화했어요!\n마이나와 대화 중인 내용은 여전히 유효해요.",
                    #     mention_author=False)
                    await room.channel.send(file=room.makeChatRecord())
            else:
                # dm이 없는 경우
                await interaction.followup.send(f"저장된 대화기록이 너무 많아서 초기화했어요!\n마이나와 대화 중인 내용은 여전히 유효해요.", ephemeral=True)
                # await ctx.reply(
                #     f"{ctx.author.display_name}님과의 대화기록입니다. 저장된 대화기록이 너무 많아서 초기화했어요!\n마이나와 대화 중인 내용은 여전히 유효해요.",
                #     mention_author=False)
                await room.channel.send(file=room.makeChatRecord())

            system_msg_count = self.get_system_msg_index(interaction, key=key) + 1
            history_count = len(room.history) - system_msg_count
            self.chat_room[key].database = room.database[-history_count:]

    def history_queue(self, interaction: Interaction[MynaBot], key=None):
        if key is None:
            key = self.create_chat_unique_key(interaction.user)
        room = self.chat_room[key]
        total_token = 0
        tokens = []
        rev_cnt = 0
        system_msg_idx = self.get_system_msg_index(interaction) + 1

        length = len(room.history)
        for idx in range(length):
            content = room.history[idx]["content"]
            _token = 0
            if isinstance(content, list):
                for c in content:
                    if c["type"] == "text":
                        _token = len(self.encoding.encode(c["text"]))
                        break
            else:
                _token = len(self.encoding.encode(room.history[idx]["content"]))
            total_token += _token
            tokens.append(_token)

        while total_token > self.max_token and len(room.history) > system_msg_idx:
            record = room.history.pop(system_msg_idx)
            _token = tokens.pop(system_msg_idx)
            total_token -= _token
            rev_cnt += 1
            print(f"기록이 삭제됩니다. {_token}토큰, {record}")

        return rev_cnt, total_token

    # @commands.command(name="마이나야", aliases=["검색"])
    @app_commands.command(description='ChatGPT를 활용하여 질문을 합니다.')
    @app_commands.describe(message="질문할 내용을 입력합니다.", file="파일도 함께 첨부하여 질문할 수 있습니다.")
    async def 마이나야(self, interaction: Interaction[MynaBot], message: str, file: discord.Attachment = None):
        allowed_user = util.is_allow_user_interaction(interaction, util.ROLE_TYPE.CHATGPT)
        allowed_guild = util.is_allow_guild_interaction(interaction, util.GUILD_COMMAND_TYPE.CHATGPT)

        if allowed_user is False and allowed_guild is False:
            await interaction.response.send_message(f"관리자가 허용한 서버만 ChatGPT 명령어를 사용할 수 있어요.", ephemeral=True)
            # msg = await ctx.reply(f"관리자가 허용한 서버만 ChatGPT 명령어를 사용할 수 있어요.", mention_author=True)
            # await msg.delete(delay=5)
            # await ctx.message.delete(delay=5)
            return

        if util.is_allow_channel_interaction(self.bot, interaction) is False:
            await util.is_not_allow_channel_interaction(interaction, util.current_function_name())
            return

        await interaction.response.defer()  # 오래걸리는 함수작동과 관련된 듯
        key = self.create_chat_unique_key(interaction.user)
        if key not in self.chat_room:
            # 대화 기록이 없을 때
            self.chat_room[key].userdata = interaction.user

        if self.chat_room[key].runtime is True:
            await interaction.followup.send("죄송합니다, 질문은 하나씩만 답변가능해요.\n이전 질문에 대한 답변이 완료되었을 때 시도해주세요.")
            # msg = await ctx.reply("죄송합니다, 질문은 하나씩만 답변가능해요.\n이전 질문에 대한 답변이 완료되었을 때 시도해주세요.", mention_author=True)
            # await msg.delete(delay=5)
            # await ctx.message.delete(delay=5)
            return False

        model = "gpt-4o-mini" # "gpt-3.5-turbo"
        if 'gpt4' in message and util.is_allow_user_interaction(interaction, util.ROLE_TYPE.GPT4):
            model = "gpt-4o"

        request_msg = {"role": "user", "content": message}
        total_token = 0
        remove_cnt = 0

        if file:
            request_msg["content"] = [
                {"type": "text", "text": f"{message}"},
            ]
            if file.content_type.startswith("image"):
                if file.content_type.split("/")[1] not in self.support_image:
                    await interaction.followup.send(f"현재 마이나는 {', '.join(self.support_image)} 확장자만 지원해요.")
                    return
                request_msg["content"].append({"type": "image_url", "image_url": {"url": f"{file.url}"}})
            else:
                await interaction.followup.send("현재 마이나는 이미지 파일 분석만 지원해요.")
                return

        self.chat_room[key].channel = interaction.channel
        self.chat_room[key].runtime = True

        # History
        if self.chat_room[key].history:
            remove_cnt, total_token = self.history_queue(interaction, key=key)  # history가 max token을 넘기지 않도록 조절.
            prompt = self.chat_room[key].history + [request_msg]
        else:
            prompt = self.system_msg + [
                {"role": "system", "content": f"The user you are talking to has the name '{interaction.user.display_name}'."}, request_msg]
        # msg = await ctx.channel.send("네, 잠시만 기다려주세요...")

        msg = await interaction.followup.send("네, 잠시만 기다려주세요...")

        # Run GPT
        try:
            res = await self.call_chat_gpt(
                interaction=interaction, msg=msg, user_message=message, prompt=prompt, token=total_token, cnt=remove_cnt,
                model=model, content_type=file.content_type if file else None, content=file if file else None)
            if res is False:
                self.chat_room[key].runtime = False
                return  # 실패한 경우 return
        except Exception as e:
            print("ChatGPT Running Error : ", e)
            self.chat_room[key].runtime = False
            await msg.edit(content=f"죄송합니다, 처리 중에 오류가 발생했어요.\n{e}")
            return

        response_msg = {"role": "assistant", "content": res["collected_message"]}
        self.chat_room[key].history = prompt + [response_msg]
        self.chat_room[key].database.extend([request_msg, response_msg])
        self.chat_room[key].runtime = False

        await self.clean_database(interaction, key=key)
        self.save_chat_data(interaction)

        await logs.send_log(bot=self.bot,
                            log_text=f"{interaction.guild.name}의 {interaction.user.display_name}님이 ChatGPT 명령어를 실행했습니다.")

    @commands.command(name="초기화", aliases=["리셋"])
    async def 초기화(self, ctx, *input):
        allowed_user = util.is_allow_user(ctx, util.ROLE_TYPE.CHATGPT)
        allowed_guild = util.is_allow_guild(ctx, util.GUILD_COMMAND_TYPE.CHATGPT)

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
        allowed_user = util.is_allow_user(ctx, util.ROLE_TYPE.CHATGPT)
        allowed_guild = util.is_allow_guild(ctx, util.GUILD_COMMAND_TYPE.CHATGPT)

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
        allowed_user = util.is_allow_user(ctx, util.ROLE_TYPE.CHATGPT)
        allowed_guild = util.is_allow_guild(ctx, util.GUILD_COMMAND_TYPE.CHATGPT)

        if allowed_user is False and allowed_guild is False:
            msg = await ctx.reply(f"관리자가 허용한 서버만 ChatGPT 명령어를 사용할 수 있어요.", mention_author=True)
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
    await bot.add_cog(ChatGPT(bot))
