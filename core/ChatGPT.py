import discord, asyncio
import openai
from discord.ext import commands, tasks
import xml.etree.ElementTree as elemTree
import typing, functools

def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper
class ChatGPT(commands.Cog):
    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        tree = elemTree.parse('./keys.xml')
        SECRETKEY = tree.find('string[@name="chatSecret"]').text
        openai.api_key = SECRETKEY
    
    @to_thread
    def requestOpenAPI(self, prompt, model_engine, max_tokens):
        competion = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.3,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return competion.choices[0].text.strip()

    @commands.command(name="마이나야", aliases=["검색"])
    async def 마이나야(self, ctx, *input):
        text = " ".join(input)
        msg = await ctx.channel.send("네, 잠시만 기다려주세요...")
        model_engine = "text-davinci-003"
        max_tokens = 1024

        try:
            response = await self.requestOpenAPI(text, model_engine, max_tokens)
            print(response)
            for i in range(len(response) // 1500 + 1):
                await ctx.reply(response[i*1500:(i+1)*1500], mention_author=False)
        except Exception as e:
            await ctx.reply(f"죄송합니다, 처리 중에 오류가 발생했어요.\n{e}", mention_author=True)
        await msg.delete()
    
async def setup(bot):
    await bot.add_cog(ChatGPT(bot))