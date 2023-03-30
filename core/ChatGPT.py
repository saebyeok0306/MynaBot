import discord, asyncio
import openai
import data.Functions as fun
from discord.ext import commands, tasks
import xml.etree.ElementTree as elemTree
import typing, functools
from datetime import datetime, timedelta

systemMsg = [
    {"role":"system", "content":"You are a chatbot named '마이나'."}, {"role":"system", "content":"Your developer is '갈대'."}, {"role":"system", "content":"You must answer in Korean only."}, {"role":"system", "content":"The place you are at is a Discord server called '유즈맵 제작공간'."},
]
#{"role":"system", "content":"You should always put '냥' at the end of your words."}

def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper
    
class ChatGPT(commands.Cog):
    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.runtime = False
        self.expired = None
        self.history = None
        self.channel = None
        self.talking = False
        self.delta = timedelta(minutes=5)
        tree = elemTree.parse('./keys.xml')
        SECRETKEY = tree.find('string[@name="chatSecret"]').text
        openai.api_key = SECRETKEY
        self.Timer.start()
    
    def cog_unload(self):
        self.Timer.cancel()
    
    @tasks.loop(seconds=60)
    async def Timer(self):
        if self.runtime is True and self.expired+self.delta < datetime.now():
            try:
                await self.channel.send(f"`ChatGPT`: 대화기록이 삭제되었습니다.")
                with open('text.txt', 'w', encoding='utf-8') as l:
                    l.write("대화내역")
                    for line in self.history[len(systemMsg):]:
                        l.write(f"\n{'User' if line['role'] == 'user' else 'Bot'} : {line['content']}")
                file = discord.File("text.txt")
                await self.channel.send(file=file)
            except: pass

            self.runtime = False
            self.expired = None
            self.history = None
            self.channel = None
    
    @to_thread
    def requestOpenAPI(self, prompt, model_engine, max_tokens):
        competion = openai.ChatCompletion.create(
            model=model_engine,
            messages=prompt,
            # max_tokens=max_tokens,
            # temperature=0.3,
            # top_p=1,
            # frequency_penalty=0,
            # presence_penalty=0
        )
        return competion['choices'][0]['message']['content']
        # return competion.choices[0].message.content.strip()

    @commands.command(name="마이나야", aliases=["검색"])
    async def 마이나야(self, ctx, *input):
        if ctx.guild.id in [966942556078354502, 631471244088311840]:
            if(ctx.channel.id in fun.getBotChannel(self.bot, ctx)):
                if self.talking is True:
                    msg = await ctx.reply("죄송합니다, 질문은 하나씩만 답변가능해요.\n이전 질문에 대한 답변이후에 다시 시도해주세요.", mention_author=True)
                    await msg.delete(delay=5)
                    return False
                
                if self.runtime is False:
                    self.runtime = True

                self.talking = True
                self.expired = datetime.now()
                self.channel = ctx.channel

                text = " ".join(input)
                prompt = [{"role":"user", "content":text}]
                if self.history: prompt = self.history + prompt
                else: prompt = systemMsg + prompt
                msg = await self.channel.send("네, 잠시만 기다려주세요...")
                model_engine = "gpt-3.5-turbo"
                max_tokens = 1024

                try:
                    response = await self.requestOpenAPI(prompt, model_engine, max_tokens)
                    self.history = prompt + [{"role":"assistant", "content":response}]
                    await ctx.reply(response, mention_author=False)
                except Exception as e:
                    await ctx.reply(f"죄송합니다, 처리 중에 오류가 발생했어요.\n{e}", mention_author=True)
                await msg.delete()
                self.talking = False
            else:
                msg = await ctx.reply(f"ChatGPT 명령은 `봇명령` 채널에서만 가능해요.")
                await msg.delete(delay=5)
                await ctx.message.delete(delay=5)
    
    @commands.command(name="초기화", aliases=["리셋"])
    async def 초기화(self, ctx, *input):
        if ctx.guild.id in [966942556078354502, 631471244088311840]:
            if self.runtime is True:
                self.runtime = False
                self.history = None
                self.expired = None
                self.talking = None
                self.channel = None
                await ctx.channel.send("`ChatGPT`: 대화내역이 초기화되었어요.")
            else:
                msg = await ctx.channel.send("`ChatGPT`: 대화내역이 없어요.")
                await msg.delete(delay=5)

    
async def setup(bot):
    await bot.add_cog(ChatGPT(bot))