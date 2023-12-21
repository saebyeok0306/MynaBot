import discord, asyncio
import openai
import tiktoken
import data.Functions as fun
import data.Logs as logs
from copy import deepcopy
from collections import defaultdict
from discord.ext import commands, tasks
from dotenv import dotenv_values
from datetime import datetime, timedelta

class Chat:
    def __init__(self):
        self.runtime = False
        self.expired = None # datetime
        self.history = None # list
        self.database = []
        self.channel = None # channel
        self.userdata = None # ctx.author
        self.dm = None # channel
    
    def print(self):
        return f"Runtime : {self.runtime}\nDatetime : {self.expired}\nHistory : {self.history}\nDatabase : {self.database}\nChannel : {self.channel}"
    
    def makeChatRecord(self) -> discord.File:
        with open('text.txt', 'w', encoding='utf-8') as l:
            l.write(f"{self.userdata.display_name}님과의 대화내역")
            for line in self.database:
                l.write(f"\n{f'{self.userdata.display_name}' if line['role'] == 'user' else '마이나봇'} : {line['content']}")
        return discord.File("text.txt")
        
    
class ChatGPT(commands.Cog):
    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.chat_room = defaultdict(Chat) # runtime, expired, history, channel
        self.delta = timedelta(minutes=10)
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-16k")
        self.max_token = 14000
        self.input_cost = 0.0015 / 1000
        self.output_cost = 0.002 / 1000
        self.system_msg = [
            {"role":"system", "content":"You are a chatbot named '마이나'."},
            {"role":"system", "content":"Your developer is '갈대'."},
            {"role":"system", "content":"You must answer in Korean only."},
            {"role":"system", "content":"The place you are at is a Discord server called '유즈맵 제작공간'."},
        ]
        try:
            with open("system.message.txt", "r", encoding="UTF-8") as f:
                system_msgs = f.readlines()
                for system_msg in system_msgs:
                    self.system_msg.append(system_msg.rstrip())
        except: pass
        self.history_system_idx = len(self.system_msg)+1 # +1은 사용자 이름 관련 등록
        # self.Timer.start()
    
    def cog_unload(self):
        pass
        # self.Timer.cancel()
    
    def is_allow_guild(self, ctx):

        allow_guilds = {
            "유즈맵 제작공간" : 631471244088311840,
            "데이터베이스" : 966942556078354502
        }
        if ctx.guild.id in allow_guilds.values():
            return True
        
        return False
    
    def is_allow_command(self, ctx):
        if ctx.channel.id in fun.getBotChannel(self.bot, ctx) or\
           ctx.author.guild_permissions.administrator:
            return True
        
        return False

    
    # @tasks.loop(seconds=60)
    # async def Timer(self):
    #     nowTime = datetime.now()
    #     del_list = []
    #     for chater in self.chat_room:
    #         if self.chat_room[chater].expired + self.delta < nowTime:
    #             try:
    #                 if self.chat_room[chater].dm:
    #                     # dm이 있는 경우
    #                     await self.chat_room[chater].dm.send(f"{self.chat_room[chater].userdata.display_name}님과의 대화기록이 삭제되었습니다.")
    #                     await self.chat_room[chater].dm.send(file = self.chat_room[chater].makeChatRecord())
    #                 else:
    #                     # dm이 없는 경우
    #                     await self.chat_room[chater].channel.send(f"{self.chat_room[chater].userdata.display_name}님과의 대화기록이 삭제되었습니다.")
    #                     await self.chat_room[chater].channel.send(file = self.chat_room[chater].makeChatRecord())
    #             except: pass
    #             del_list.append(chater)
    #     for chater in del_list:
    #         del self.chat_room[chater]

    async def call_chat_gpt(self, ctx, msg, prompt):
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
                client = openai.AsyncOpenAI(api_key=config["ChatGPT_Secret"])
                competion = await client.chat.completions.create(
                    model=model_engine,
                    messages=prompt,
                    temperature=0.4,
                    stream=True,
                    # request_timeout=60,
                )

                cnt = 0
                async for chunk in competion:
                    cnt += 1
                    try:
                        chunk_message = chunk.choices[0].delta.content or ""
                        collected_message += chunk_message
                        if isLong is False:
                            if len(collected_message) >= 2000:
                                isLong = True
                                await msg.edit(content="답변이 너무 길어서 파일로 올릴게요.")
                            if(cnt > 12):
                                cnt = 0
                                await msg.edit(content=collected_message)
                    except: pass
                return True
            
            request_task = asyncio.create_task(requestOpenAPI(prompt, "gpt-3.5-turbo-16k"))
            timeout_task = asyncio.create_task(timeout(timeout_sec, request_task))
            await asyncio.gather(timeout_task, request_task)

            input_token = len(self.encoding.encode(prompt[-1]["content"]))
            output_token = len(self.encoding.encode(collected_message))
            total_token = input_token + output_token
            input_dolar = round(self.input_cost * input_token, 4)
            output_dolar = round(self.output_cost * output_token, 4)
            total_dolar = round(input_dolar + output_dolar, 4)
            used_record_text = f"\n> `${total_dolar}를 사용했어요.`" # {input_token}+{output_token}({total_token})토큰, 

            if not isLong and len(collected_message + used_record_text) >= 2000:
                isLong = True
                await msg.edit(content="답변이 너무 길어서 파일로 올릴게요.")

            if isLong is False:
                await msg.edit(content=collected_message + used_record_text)
            else:
                with open('result.txt', 'w', encoding='utf-8') as l:
                    l.write(collected_message)
                file = discord.File("result.txt")
                await msg.reply(f"{ctx.author.display_name}님의 질문에 해당하는 답변이에요.{used_record_text}")
                await ctx.channel.send(file=file)
            
            return {
                "collected_message": collected_message,
                "input_token": input_token,
                "output_token": output_token,
                "total_token": total_token
            }

        except asyncio.CancelledError as e:
            await ctx.reply(f"죄송합니다, {timeout_sec}초 동안 응답이 없어서 종료했어요.\n명령을 다시 시도해주세요!", mention_author=True)
        except Exception as e:
            await ctx.reply(f"죄송합니다, 처리 중에 오류가 발생했어요.\n`!초기화` 명령어로 대화내역을 초기화해주세요!\n{e}", mention_author=True)
        
        return False
    
    def history_queue(self, ctx):
        room = self.chat_room[ctx.author.id]
        total_token = 0
        tokens = []
        rev_cnt = 0

        length = len(room.history)
        for idx in range(length):
            _token = len(self.encoding.encode(room.history[idx]["content"]))
            total_token += _token
            tokens.append(_token)

        while total_token > self.max_token and len(room.history) > self.history_system_idx:
            record = room.history.pop(self.history_system_idx)
            _token = tokens.pop(self.history_system_idx)
            total_token -= _token
            rev_cnt += 1
            print(f"기록이 삭제됩니다. {_token}토큰, {record}")

        return rev_cnt

    @commands.command(name="마이나야", aliases=["검색"])
    async def 마이나야(self, ctx, *input):
        if self.is_allow_guild(ctx) is False: return
        if self.is_allow_command(ctx) is False:
            msg = await ctx.reply(f"ChatGPT 관련 명령어는 `봇명령` 채널에서만 가능해요.")
            await msg.delete(delay=5)
            await ctx.message.delete(delay=5)
            return
        
        await ctx.defer() # 오래걸리는 함수작동과 관련된 듯
        chater = ctx.author.id
        if chater not in self.chat_room:
            # 대화 기록이 없으면, 유저와 dm 등록하기
            self.chat_room[chater].userdata = ctx.author
            try:
                self.chat_room[chater].dm = await ctx.author.create_dm()
            except:
                self.chat_room[chater].dm = False
        
        if self.chat_room[chater].runtime is True:
            msg = await ctx.reply("죄송합니다, 질문은 하나씩만 답변가능해요.\n이전 질문에 대한 답변이 완료되었을 때 시도해주세요.", mention_author=True)
            await msg.delete(delay=5)
            await ctx.message.delete(delay=5)
            return False

        self.chat_room[chater].expired = datetime.now()
        self.chat_room[chater].channel = ctx.channel
        self.chat_room[chater].runtime = True

        text = " ".join(input)
        request_msg = {"role":"user", "content":text}

        # History
        if self.chat_room[chater].history:
            _ = self.history_queue(ctx) # history가 max token을 넘기지 않도록 조절.
            prompt = self.chat_room[chater].history + [request_msg]
        else:
            prompt = self.system_msg + [{"role":"system", "content":f"The user you are talking to has the name '{ctx.author.display_name}'."}, request_msg]
        msg = await ctx.channel.send("네, 잠시만 기다려주세요...")

        # Run GPT
        res = await self.call_chat_gpt(ctx, msg, prompt)
        if res is False: return # 실패한 경우 return

        response_msg = {"role":"assistant", "content":res["collected_message"]}
        self.chat_room[chater].history = prompt + [response_msg]
        self.chat_room[chater].database.extend([request_msg, response_msg])
        self.chat_room[chater].runtime = False

        await logs.SendLog(bot=self.bot, log_text=f"{ctx.guild.name}의 {ctx.author.display_name}님이 ChatGPT 명령어를 실행했습니다.")
            
    
    @commands.command(name="초기화", aliases=["리셋"])
    async def 초기화(self, ctx, *input):
        if self.is_allow_guild(ctx) is False: return
        if self.is_allow_command(ctx) is False:
            msg = await ctx.reply(f"ChatGPT 관련 명령어는 `봇명령` 채널에서만 가능해요.")
            await msg.delete(delay=5)
            await ctx.message.delete(delay=5)
            return
        
        chater = ctx.author.id
        if chater in self.chat_room:
            room = self.chat_room[chater]
            if room.dm:
                # dm이 있는 경우
                try:
                    await room.dm.send(file = room.makeChatRecord())
                except:
                    # dm 전송에 실패한 경우
                    await room.channel.send(file = room.makeChatRecord())
            else:
                # dm이 없는 경우
                await room.channel.send(file = room.makeChatRecord())
            await ctx.reply(f"{ctx.author.display_name}님과의 대화내역이 초기화되었어요.")
            del self.chat_room[chater]
        else:
            msg = await ctx.reply(f"{ctx.author.display_name}님과의 대화내역이 없어요.")
            await msg.delete(delay=5)
            await ctx.message.delete(delay=5)
    
    @commands.command(name="대화목록", aliases=["대화리스트"])
    async def 대화목록(self, ctx, *input):
        if self.is_allow_guild(ctx) is False: return
        if self.is_allow_command(ctx) is False:
            msg = await ctx.reply(f"ChatGPT 관련 명령어는 `봇명령` 채널에서만 가능해요.")
            await msg.delete(delay=5)
            await ctx.message.delete(delay=5)
            return
        
        cnt = len(self.chat_room.keys())
        if cnt:
            text = f"현재 생성된 대화방은 "
            for idx, key in enumerate(self.chat_room):
                text += f"{self.chat_room[key].userdata.display_name}님"
                if idx != cnt-1: text += ", "
            text += f"이 있고 총 {cnt}개의 방이 있습니다."
            await ctx.reply(text)
        else:
            text = f"현재 생성된 대화방이 없습니다."
            msg = await ctx.reply(text)
            await msg.delete(delay=5)
            await ctx.message.delete(delay=5)
    
    @commands.command(name="대화내역", aliases=["대화기록", "대화내용"])
    async def 대화내역(self, ctx, *input):
        if self.is_allow_guild(ctx) is False: return
        if self.is_allow_command(ctx) is False:
            msg = await ctx.reply(f"ChatGPT 관련 명령어는 `봇명령` 채널에서만 가능해요.")
            await msg.delete(delay=5)
            await ctx.message.delete(delay=5)
            return
        
        if ctx.author.id not in self.chat_room:
            msg = await ctx.reply(f"마이나와 대화한 내역이 없어요!\n`!마이나야 [질문]`을 통해 말을 걸어보세요.")
            return
        
        room = self.chat_room[ctx.author.id]
        if room.dm:
            # dm이 있는 경우
            try:
                await room.dm.send(f"{ctx.author.display_name}님과의 대화기록입니다.")
                await room.dm.send(file = room.makeChatRecord())
                await ctx.reply(f"개인메시지로 대화기록을 전송했어요!", mention_author=False)
            except:
                room.dm = False
                await ctx.reply(f"{ctx.author.display_name}님과의 대화기록입니다.", mention_author=False)
                await room.channel.send(file = room.makeChatRecord())
        else:
            # dm이 없는 경우
            await ctx.reply(f"{ctx.author.display_name}님과의 대화기록입니다.", mention_author=False)
            await room.channel.send(file = room.makeChatRecord())

    
    @commands.command(name="GPT테스트")
    async def GPT테스트(self, ctx, *input):
        if self.is_allow_guild(ctx) is False: return
        if ctx.author.guild_permissions.administrator:
            room = self.chat_room[ctx.author.id]
            await ctx.reply(room.print(), mention_author=False)

async def setup(bot):
    await bot.add_cog(ChatGPT(bot))