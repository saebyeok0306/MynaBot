import discord, asyncio
import openai
import data.Functions as fun
from collections import defaultdict
from discord.ext import commands, tasks
import xml.etree.ElementTree as elemTree
import typing, functools
from datetime import datetime, timedelta

systemMsg = [
    {"role":"system", "content":"You are a chatbot named '마이나'."}, {"role":"system", "content":"Your developer is '갈대'."}, {"role":"system", "content":"You must answer in Korean only."}, {"role":"system", "content":"The place you are at is a Discord server called '유즈맵 제작공간'."},
]
# {"role":"system", "content":"You should always put '냥' at the end of your words."}

def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper

class Chat:
    def __init__(self):
        self.runtime = False
        self.expired = None
        self.history = None
        self.channel = None
        self.userdata = None
        self.dm = None
    
    def print(self):
        return f"{self.runtime}\n{self.expired}\n{self.history}\n{self.channel}"
    
    def makeChatRecord(self) -> discord.File:
        with open('text.txt', 'w', encoding='utf-8') as l:
            l.write(f"{self.userdata.display_name}님과의 대화내역")
            for line in self.history[len(systemMsg)+1:]:
                l.write(f"\n{f'{self.userdata.display_name}' if line['role'] == 'user' else '마이나봇'} : {line['content']}")
        return discord.File("text.txt")
        
    
class ChatGPT(commands.Cog):
    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.chatRoom = defaultdict(Chat) # runtime, expired, history, channel
        self.delta = timedelta(minutes=10)
        tree = elemTree.parse('./keys.xml')
        SECRETKEY = tree.find('string[@name="chatSecret"]').text
        openai.api_key = SECRETKEY
        self.Timer.start()
    
    def cog_unload(self):
        self.Timer.cancel()
    
    @tasks.loop(seconds=60)
    async def Timer(self):
        nowTime = datetime.now()
        del_list = []
        for chater in self.chatRoom:
            if self.chatRoom[chater].expired + self.delta < nowTime:
                await self.chatRoom[chater].channel.send(f"{self.chatRoom[chater].userdata.display_name}님과의 대화기록이 삭제되었습니다.")
                if self.chatRoom[chater].dm:
                    # dm이 있는 경우
                    await self.chatRoom[chater].dm.send(file = self.chatRoom[chater].makeChatRecord())
                else:
                    # dm이 없는 경우
                    await self.chatRoom[chater].channel.send(file = self.chatRoom[chater].makeChatRecord())
                del_list.append(chater)
        for chater in del_list:
            del self.chatRoom[chater]
    
    @to_thread
    def requestOpenAPI(self, prompt, model_engine):
        competion = openai.ChatCompletion.create(
            model=model_engine,
            messages=prompt
        )
        return competion['choices'][0]['message']['content']

    @commands.command(name="마이나야", aliases=["검색"])
    async def 마이나야(self, ctx, *input):
        if ctx.guild.id in [966942556078354502, 631471244088311840]:
            if(ctx.channel.id in fun.getBotChannel(self.bot, ctx)):
                chater = ctx.author.display_name + '#' + ctx.author.discriminator
                if chater not in self.chatRoom:
                    # 대화 기록이 없으면, 유저와 dm 등록하기
                    self.chatRoom[chater].userdata = ctx.author
                    try:
                        self.chatRoom[chater].dm = await ctx.author.create_dm()
                    except:
                        self.chatRoom[chater].dm = False
                
                if self.chatRoom[chater].runtime is True:
                    msg = await ctx.reply("죄송합니다, 질문은 하나씩만 답변가능해요.\n이전 질문에 대한 답변이 완료되었을 때 시도해주세요.", mention_author=True)
                    await msg.delete(delay=5)
                    await ctx.message.delete(delay=5)
                    return False

                self.chatRoom[chater].expired = datetime.now()
                self.chatRoom[chater].channel = ctx.channel
                self.chatRoom[chater].runtime = True

                text = " ".join(input)
                prompt = [{"role":"user", "content":text}]
                if self.chatRoom[chater].history: prompt = self.chatRoom[chater].history + prompt
                else: prompt = systemMsg + [{"role":"system", "content":f"The user`s name is '{ctx.author.display_name}'."}] + prompt
                msg = await ctx.reply("네, 잠시만 기다려주세요...")

                try:
                    response = await self.requestOpenAPI(prompt, "gpt-3.5-turbo")
                    self.chatRoom[chater].history = prompt + [{"role":"assistant", "content":response}]
                    if len(response) <= 2000: await ctx.reply(response, mention_author=False)
                    else:
                        with open('text.txt', 'w', encoding='utf-8') as l:
                            l.write(response)
                        file = discord.File("text.txt")
                        await ctx.channel.send(f'답변이 너무 길어서 파일로 올릴게요.')
                        await ctx.channel.send(file=file)
                except Exception as e:
                    await ctx.reply(f"죄송합니다, 처리 중에 오류가 발생했어요.\n`!초기화` 명령어로 대화내역을 초기화해주세요!\n{e}", mention_author=True)
                await msg.delete() # 기존 wait msg 삭제
                self.chatRoom[chater].runtime = False
            else:
                msg = await ctx.reply(f"ChatGPT 관련 명령어는 `봇명령` 채널에서만 가능해요.")
                await msg.delete(delay=5)
                await ctx.message.delete(delay=5)
    
    @commands.command(name="초기화", aliases=["리셋"])
    async def 초기화(self, ctx, *input):
        if ctx.guild.id in [966942556078354502, 631471244088311840]:
            if(ctx.channel.id in fun.getBotChannel(self.bot, ctx)):
                chater = ctx.author.display_name + '#' + ctx.author.discriminator
                if chater in self.chatRoom:
                    if self.chatRoom[chater].dm:
                        # dm이 있는 경우
                        await self.chatRoom[chater].dm.send(file = self.chatRoom[chater].makeChatRecord())
                    else:
                        # dm이 없는 경우
                        await self.chatRoom[chater].channel.send(file = self.chatRoom[chater].makeChatRecord())
                    await ctx.reply(f"{ctx.author.display_name}님과의 대화내역이 초기화되었어요.")
                    del self.chatRoom[chater]
                else:
                    msg = await ctx.reply(f"{ctx.author.display_name}님과의 대화내역이 없어요.")
                    await msg.delete(delay=5)
                    await ctx.message.delete(delay=5)
            else:
                msg = await ctx.reply(f"ChatGPT 관련 명령어는 `봇명령` 채널에서만 가능해요.")
                await msg.delete(delay=5)
                await ctx.message.delete(delay=5)
    
    @commands.command(name="대화내역", aliases=["대화리스트"])
    async def 대화내역(self, ctx, *input):
        if ctx.guild.id in [966942556078354502, 631471244088311840]:
            if(ctx.channel.id in fun.getBotChannel(self.bot, ctx)):
                cnt = len(self.chatRoom.keys())
                if cnt:
                    text = f"현재 생성된 대화방은 "
                    for idx, name in enumerate(self.chatRoom):
                        text += f"{name}님"
                        if idx != cnt-1: text += ", "
                    text += f"이 있고 총 {cnt}개의 방이 있습니다."
                    await ctx.reply(text)
            else:
                msg = await ctx.reply(f"ChatGPT 관련 명령어는 `봇명령` 채널에서만 가능해요.")
                await msg.delete(delay=5)
                await ctx.message.delete(delay=5)

async def setup(bot):
    await bot.add_cog(ChatGPT(bot))