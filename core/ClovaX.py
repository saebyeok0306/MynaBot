from collections import defaultdict

import aiohttp
import json
from discord.ext import commands
from dotenv import dotenv_values

import utils.Utility as util


class Chat:
    def __init__(self):
        self.runtime = False
        self.channel = None  # channel
        self.userdata = None  # ctx.author


class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id, msg):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id
        self._msg = msg
        self._tokens = ""

    async def execute(self, completion_request):
        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }

        async with aiohttp.ClientSession() as session:
            event_type = "start"
            cnt = 0
            async with session.post(self._host + '/testapp/v1/chat-completions/HCX-003',
                                    headers=headers, json=completion_request) as response:
                async for line in response.content:
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith("event"):
                            event_type = line.split(":")[1]
                        elif event_type.startswith("token") and line.startswith("data"):
                            data = json.loads(line[len("data:"):])
                            self._tokens += data['message']['content']
                            cnt += 1
                            if cnt > 16:
                                cnt = 0
                                await self._msg.edit(content=self._tokens)
                                
        # 마지막에 한번더 업데이트하기
        await self._msg.edit(content=self._tokens)


class ClovaX(commands.Cog):
    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.chat_room = defaultdict(Chat)  # runtime, channel
        self.system_msg = [
            {"role": "system", "content": "디스코드 서버 운영을 도와주기 위한 봇이다.\n- 이름은 `마이나`라고 한다.\n- 디스코드 서버의 이름은 `유즈맵 제작공간`이다.\n- 항상 답변은 여성스러운 존댓말을 사용한다.\n- 봇 명령어에 대한 도움이 필요하면, `!도움말` 이라고 채팅을 입력하면 된다고 안내하기.\n- 봇 명령어를 잘 모르겠다면, `!도움말`이라고 채팅을 입력하면 된다고 안내하기.\n- 문의는 `갈대`에게 하면 된다."}
        ]

    def cog_unload(self):
        pass

    @staticmethod
    def create_key(id, guild_id):
        return id + guild_id

    def create_chat_unique_key(self, author):
        id = author.id
        guild_id = author.guild.id

        return self.create_key(id, guild_id)

    async def run_clovax(self, ctx, msg, prompt):
        config = dotenv_values('.env')
        completion_executor = CompletionExecutor(
            host='https://clovastudio.stream.ntruss.com',
            api_key=config["CLOVA_API_KEY"],
            api_key_primary_val=config["CLOVA_API_KEY_PRIMARY_VAL"],
            request_id=config["CLOVA_REQUEST_ID"],
            msg=msg
        )

        request_data = {
            'messages': prompt,
            'topP': 0.8,
            'topK': 0,
            'maxTokens': 256,
            'temperature': 0.5,
            'repeatPenalty': 5.0,
            'stopBefore': [],
            'includeAiFilters': True,
            'seed': 0
        }

        await completion_executor.execute(request_data)

    @commands.command(name="클로바야", aliases=["clova"])
    async def 클로바야(self, ctx, *input):
        allowed_user = util.is_allow_user(ctx, util.ROLE_TYPE.CLOVAX)
            
        if allowed_user is False:
            msg = await ctx.reply(f"관리자가 허용한 유저만 CLOVA X 명령어를 사용할 수 있어요.", mention_author=True)
            await msg.delete(delay=5)
            await ctx.message.delete(delay=5)
            return
            
        if util.is_allow_channel(self.bot, ctx) is False:
            await util.is_not_allow_channel(ctx, util.current_function_name())
            return

        await ctx.defer()  # 오래걸리는 함수작동과 관련된 듯
        key = self.create_chat_unique_key(ctx.author)

        if key not in self.chat_room:
            # 대화 기록이 없을 때
            self.chat_room[key].userdata = ctx.author

        if self.chat_room[key].runtime is True:
            msg = await ctx.reply("죄송합니다, 질문은 하나씩만 답변가능해요.\n이전 질문에 대한 답변이 완료되었을 때 시도해주세요.", mention_author=True)
            await msg.delete(delay=5)
            await ctx.message.delete(delay=5)
            return False

        self.chat_room[key].channel = ctx.channel
        self.chat_room[key].runtime = True

        text = " ".join(input)
        request_msg = {"role": "user", "content": text}

        prompt = self.system_msg + [
            {"role": "system", "content": f"너와 대화 중인 유저의 이름은 '{ctx.author.display_name}'이다."},
            request_msg]
        msg = await ctx.channel.send("네, 잠시만 기다려주세요...")

        # Run Clova X
        await self.run_clovax(ctx=ctx, msg=msg, prompt=prompt)
        self.chat_room[key].runtime = False


async def setup(bot):
    await bot.add_cog(ClovaX(bot))
