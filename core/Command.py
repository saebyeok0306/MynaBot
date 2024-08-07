import asyncio
from enum import Enum
from typing import Literal

import discord
import itertools
import random

from discord import app_commands, Interaction
from discord.ext import commands
from sqlalchemy import and_

import utils.Logs as logs
import utils.Utility as util
from main import MynaBot
from utils.Timeout import timeout
from utils.database.Database import SessionContext
from utils.database.model.exp import Exp
from utils.database.model.status import Status


class AuthorType(Enum):
    ANY = 0
    USER = 1
    GUILD = 2


class Guide:
    def __init__(self, name, value, active=True, user_role=None, guild_role=None):
        self.name = name
        self.value = value
        self.active = active
        self.user_role = user_role
        self.guild_role = guild_role

    def __call__(self, ctx):
        if self.active is False:
            return None, None

        author_type = AuthorType.ANY
        is_skip = False
        if self.user_role is not None:
            if util.is_allow_user(ctx, self.user_role) is False:
                author_type = AuthorType.USER
            else:
                is_skip = True
        if is_skip is False and self.guild_role is not None and util.is_allow_guild(ctx, self.guild_role) is False:
            author_type = AuthorType.GUILD

        from copy import copy
        _guide = copy(self.__dict__)
        del _guide["active"]
        del _guide["user_role"]
        del _guide["guild_role"]
        return _guide, author_type

class Command(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.title = "마이나"
        self.guides = {
            "기본적인 명령어": [
                Guide(name=f'/프로필', value=f'재미로 보는 프로필이에요. 레벨은 여러가지 요소를 기준으로 상승해요.'),
                Guide(name=f'!프로필2', value=f'이전 방식으로 프로필을 보여줘요.'),
                Guide(name=f'!유튜브 `검색어`', value=f'유튜브 영상을 검색할 수 있어요. 반응 버튼으로 영상을 선택할 수 있어요.'),
                Guide(name='!주사위 `값(기본값 100)`', value=f'주사위를 굴립니다. 범위:1~100  값을 입력하면 1~값까지'),
                Guide(name='!청소 `값(기본값 5)`', value=f'내가 작성한 메시지 N개를 삭제합니다. **！최대 20개**'),
                Guide(name='!골라줘 `대상1` `대상2` ...', value=f'스페이스바 간격으로 구분된 대상들 중에서 하나를 선택해줘요!'),
                Guide(name=f'!색상변경 `색상`', value=f'닉네임 색상을 변경할 수 있어요!'),
                Guide(name=f'!번역 `내용`', value=f'언어를 인식해서 한국어는 영어로, 한국어가 아닌 언어는 한국어로 번역해줘요!', active=False),
                Guide(name=f'!한영번역 `내용`', value=f'한국어를 영어로 번역해줘요!', active=False),
                Guide(name=f'!영한번역 `내용`', value=f'영어를 한국어로 번역해줘요!', active=False),
                Guide(name=f'!흑이', value=f'노나메님의 ~~납치~~하고 싶은 흑이사진이 나와요!',
                      guild_role=util.GUILD_COMMAND_TYPE.BLACKCAT, user_role=util.ROLE_TYPE.BLACKCAT),
                Guide(name=f'/서버상태', value=f'현재 서버의 상태를 확인할 수 있어요.'),
                Guide(name='!마크', value='디코방에서 운영되고 있는 서버주소를 알려줘요!', active=False),
                Guide(name='/문의', value='봇 개발자에게 버그나 문의사항을 보낼 수 있어요!'),
            ],
            "유즈맵 제작 도구모음": [
                Guide(name='/계산 `코드`', value=f'코드를 작성해서 넣으면, {self.bot.user.name}가 계산해서 알려줘요!'),
                Guide(name=f'/스위치 `갯수` or `이름1 이름2 이름3 ...`', value=f'스위치를 N개 사용했을 때\n나올 수 있는 경우의 수를 표기합니다.'),
            ],
            "마이나(ChatGPT)": [
                Guide(name=f'!마이나야 `질문`', value=f'ChatGPT를 활용해서 질문에 대한 답변을 해줘요!',
                      guild_role=util.GUILD_COMMAND_TYPE.CHATGPT, user_role=util.ROLE_TYPE.CHATGPT),
                Guide(name=f'!대화내용', value=f'마이나와 대화한 기록을 확인할 수 있어요.',
                      guild_role=util.GUILD_COMMAND_TYPE.CHATGPT, user_role=util.ROLE_TYPE.CHATGPT),
                Guide(name=f'!초기화', value=f'마이나에게 질문한 대화기록을 초기화해요.',
                      guild_role=util.GUILD_COMMAND_TYPE.CHATGPT, user_role=util.ROLE_TYPE.CHATGPT),
                Guide(name=f'!대화목록', value=f'마이나와 대화중인 방목록을 보여줘요.',
                      guild_role=util.GUILD_COMMAND_TYPE.CHATGPT, user_role=util.ROLE_TYPE.CHATGPT),
                Guide(name=f'GPT-4 사용방법', value=f'질문을 작성할 때 `gpt4`를 포함해서 작성해보세요.',
                      guild_role=util.GUILD_COMMAND_TYPE.CHATGPT, user_role=util.ROLE_TYPE.GPT4),
                Guide(name=f'!클로바야 `질문`', value=f'네이버의 CLOVA X를 활용해서 질문에 대한 답변을 해줘요!', user_role=util.ROLE_TYPE.CLOVAX),
            ],
            "음성채팅 관련 명령어": [
                Guide(name=f'!입장',
                      value=f'음성채팅에 참여한 상태에서 사용하면 마이나의 TTS 기능이 활성화돼요. 이 상태에서 음성채팅채널에서 채팅하면 음성으로 들을 수 있어요.'),
                Guide(name=f'!이동', value=f'마이나를 다른 음성채팅으로 옮길 때 사용해요.'),
                Guide(name=f'!흑이체', value=f'TTS 기능으로 텍스트를 음성으로 변환할 때 야옹이체로 바뀝니다.'),
                Guide(name=f'!남성', value=f'TTS 기능으로 텍스트를 음성으로 변환할 때 남성목소리로 바뀝니다.'),
                Guide(name=f'!여성', value=f'TTS 기능으로 텍스트를 음성으로 변환할 때 여성목소리로 바뀝니다.'),
            ],
            "음악재생 관련 명령어": [
                Guide(name=f'!입장',
                      value=f'먼저 봇이 음성채팅에 참여해야 해요. 이 기능은 내가 있는 음성채팅에 마이나를 초대해요.'),
                Guide(name=f'!이동', value=f'마이나를 다른 음성채팅으로 옮길 때 사용해요.'),
                Guide(name=f'!볼륨 `값`', value=f'마이나가 재생하는 노래의 음량을 조절해요. ex. !볼륨 30'),
                Guide(name=f'!재생 `유튜브링크`', value=f'마이나가 링크의 음원을 플레이리스트에 추가해요.'),
                Guide(name=f'!유튜브 `검색어`', value=f'유튜브 영상을 검색하여 플레이리스트로 추가할 수 있어요.'),
                Guide(name=f'!정지', value=f'마이나가 현재 재생중인 음악을 정지합니다.'),
                Guide(name=f'!곡랜덤', value=f'플레이리스트의 음악을 랜덤하게 섞습니다.'),
                Guide(name=f'!플레이리스트', value=f'현재 플레이리스트를 보여줘요.'),
                Guide(name=f'!음악삭제 `번호`', value=f'플레이리스트에서 `번호`에 해당하는 음악을 삭제해요.'),
                Guide(name=f'!음악모두삭제', value=f'플레이리스트에 등록된 모든 음악을 삭제해요.'),
                Guide(name=f'!음악정보', value=f'현재 재생 중인 음악의 정보를 확인해요.'),
            ],
            "관리자 명령어": [
                Guide(name=f'!관리자청소 `값(기본값 5)`', value=f'어떤 메시지든 N개를 삭제합니다.\n**！제한은 없으나 너무 큰 값은 디코서버에 무리를 줍니다.**'),
            ]
        }

    @commands.command(name="도움말", aliases=["도움", "설명"])
    async def 도움말(self, ctx):
        sel_emoji = ["↩️", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        sel_key = None
        embed = discord.Embed(color=0xB22222, title=":scroll: 도움말", description=f'{self.bot.user.name}에게 있는 명령어을 알려드려요.')
        embed.set_footer(text=f"{ctx.author} | 도움말", icon_url=ctx.author.display_avatar)
        msg = await ctx.channel.send(embed=embed)
        await logs.send_log(bot=self.bot, log_text=f"{ctx.guild.name}의 {ctx.author.display_name}님이 도움말 명령어를 실행했습니다.")

        while True:
            description = f'{self.bot.user.name}에게 있는 명령어을 알려드려요.'
            guide_list = self.guides.keys()
            if sel_key is None:
                description += "\n"
                for i, key in enumerate(guide_list):
                    description += f"\n{i+1}. {key}"
            else:
                description = f"`{key}`에 대한 명령어에요."

            embed = discord.Embed(color=0xB22222, title=":scroll: 도움말", description=description)
            embed.set_footer(text=f"{ctx.author} | 도움말", icon_url=ctx.author.display_avatar)

            if sel_key is not None:
                sel_guides = self.guides[sel_key]
                for guide in sel_guides:
                    item, author_type = guide(ctx=ctx)
                    if item is None:
                        continue

                    if author_type == AuthorType.USER:
                        item["value"] += f"\n**개발자가 허락한 유저만 사용이 가능합니다.**"
                    if author_type == AuthorType.GUILD:
                        item["value"] += f"\n**개발자가 허락한 서버만 사용이 가능합니다.**"
                    if author_type != AuthorType.ANY:
                        item["name"] = f'~~{item["name"]}~~'
                    embed.add_field(**item)
            await msg.edit(embed=embed)

            if sel_key is None:
                for i in range(len(guide_list)):
                    await msg.add_reaction(sel_emoji[i+1])
            else:
                await msg.add_reaction(sel_emoji[0])

            try:
                def check(reaction, user):
                    return str(reaction) in sel_emoji and \
                    user == ctx.author and reaction.message.id == msg.id
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

                if sel_key is None:
                    for i, key in enumerate(guide_list):
                        if str(reaction) == sel_emoji[i+1]:
                            sel_key = key
                            await msg.clear_reactions()
                            break
                else:
                    if str(reaction) == sel_emoji[0]:
                        sel_key = None
                        await msg.clear_reactions()
                        continue

            except asyncio.TimeoutError:
                await msg.clear_reactions()
                return

    @commands.command(name="주사위", aliases=["다이스"])
    async def 주사위(self, ctx, *input):
        value = 100  # input이 없는 경우
        try:
            if input and int(input[0]) > 1: value = int(input[0])
        except:
            pass

        r = random.randint(1, value)
        await ctx.channel.send(f'주사위를 굴립니다...\n두둥! `{r}`입니다!')
        await logs.send_log(bot=self.bot, log_text=f"{ctx.guild.name}의 {ctx.author.display_name}님이 주사위 명령어를 실행했습니다.")

    @commands.command(name="청소", aliases=["메시지청소", "삭제", "메시지삭제", "제거", "메시지제거", "지우기", "메시지지우기"])
    async def 청소(self, ctx, *input):
        remove = 6
        if len(input) >= 1 and input[0].isdigit():
            remove = int(input[0]) + 1

        text = ''
        if remove > 21:
            remove = 21
            text += f'메시지는 최대 20개까지만 지울 수 있어요.\n'

        text += f'**{remove - 1}개**의 메시지를 삭제했어요!'

        async for message in ctx.channel.history(limit=None):
            if remove:
                if message.author == ctx.author:
                    await message.delete()
                    remove -= 1
            else:
                break

        # def is_me(message): return message.author == ctx.author
        # await ctx.channel.purge(limit=remove+1, check=is_me)
        msg = await ctx.channel.send(content=text)
        await msg.delete(delay=5)
        await logs.send_log(bot=self.bot, log_text=f"{ctx.guild.name}의 {ctx.author.display_name}님이 청소 명령어를 실행했습니다.")

    @commands.command()
    async def 핑(self, ctx):
        embed = discord.Embed(color=0x2f3136)
        embed.set_author(name=f'{self.bot.user.name}봇의 지연시간(ms)')
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.add_field(name="지연시간(ping)", value=f'{round(self.bot.latency * 1000)}ms로 측정되요!')
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name='골라줘', aliases=['골라', '선택', '선택해줘'])
    async def 골라줘(self, ctx, *input):
        choice = random.choice(input)
        text = f'제 생각에는...\n**{choice}**, 이게 좋지 않을까요?!'
        await ctx.reply(content=text, mention_author=False)

        await logs.send_log(bot=self.bot, log_text=f"{ctx.guild.name}의 {ctx.author.display_name}님이 골라줘 명령어를 실행했습니다.")

    @app_commands.command(description='Python 문법으로 간단하게 코드을 실행할 수 있어요.')
    @app_commands.describe(code='Python 문법에 맞게 작성하면 코드를 실행해줘요.')
    async def 계산(self, interaction: Interaction[MynaBot], code: str):

        @timeout(1)
        def Calculate(_text_code_):
            for _check_excption_ in ('self', 'import', 'print', 'Quitter', '_', 'eval', 'exec', 'global', '_text_code_', '_check_excption_'):
                if _check_excption_ in _text_code_:
                    return False
            return str(eval(_text_code_))

        result = False
        try:
            result = Calculate(code)
        except Exception as e:
            if type(e).__name__ == 'TimeoutError':
                await interaction.response.send_message(f'연산시간이 1초를 넘겨서 정지시켰어요.\n입력값 : {code}', ephemeral=True)
                # await ctx.channel.send(f'연산시간이 1초를 넘겨서 정지시켰어요.\n입력값 : {code}')
            else:
                await interaction.response.send_message(f'수식에 오류가 있어요.\n에러 : {e}', ephemeral=True)
                # await ctx.channel.send(f'수식에 오류가 있어요.\n에러 : {e}')
            return

        if result is False:
            await interaction.response.send_message(f'수식에 오류가 있어요.\n에러 : {code}', ephemeral=True)
            # await ctx.channel.send(f'수식에 오류가 있어요.\n입력값 : {code}')
        else:
            # 결과 보내기
            if len(result) <= 1500:
                try:
                    result = f"{result} ({util.print_(int(result))})"
                except:
                    pass
                await interaction.response.send_message(f'```{result}```')
                # await ctx.channel.send(f'```{result}```')
            # 메시지의 길이가 1500을 넘기는 경우
            else:
                with open('text.txt', 'w', encoding='utf-8') as l:
                    l.write(result)
                file = discord.File("text.txt")
                # await ctx.channel.send(f'실행 결과가 너무 길어서 파일로 출력했어요.')
                # await ctx.channel.send(file=file)
                await interaction.response.send_message(f'실행 결과가 너무 길어서 파일로 출력했어요.', file=file)

        await logs.send_log(bot=self.bot, log_text=f"{interaction.guild.name}의 {interaction.user.display_name}님이 계산 명령어를 실행했습니다.")

    @staticmethod
    async def fetch_data(api_url):
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                return await response.text(), response.status

    @app_commands.command(description='귀여운 흑이를 볼 수 있어요.')
    async def 흑이(self, interaction: Interaction[MynaBot]):
        await interaction.response.defer()
        allowed_user = util.is_allow_user_interaction(interaction, util.ROLE_TYPE.BLACKCAT)
        allowed_guild = util.is_allow_guild_interaction(interaction, util.GUILD_COMMAND_TYPE.BLACKCAT)

        if allowed_user is False and allowed_guild is False:
            await interaction.followup.send(f"관리자가 허용한 서버만 흑이 명령어를 사용할 수 있어요.", ephemeral=True)
            return
        if util.is_allow_channel_interaction(self.bot, interaction) is False:
            await util.is_not_allow_channel_interaction(self.bot, interaction, util.current_function_name())
            return

        api_url = "http://ajwmain.iptime.org/7Z2R7J2064qUIOygleunkCDqt4Dsl6zsmrQg6rKA7J2AIOqzoOyWkeydtCEh/black_cat.php"
        data, status_code = await self.fetch_data(api_url)
        if status_code == 200:
            try:
                import urllib
                urllib.request.urlretrieve(data, "blackcat.png")
                file = discord.File("blackcat.png")
                await interaction.followup.send(file=file)
            except:
                await interaction.followup.send(data)

            with SessionContext() as session:
                user_exp = session.query(Exp).filter(
                    and_(Exp.id == interaction.user.id, Exp.guild_id == interaction.guild.id)).first()
                if user_exp is None:
                    user_exp = Exp(interaction.user.id, interaction.guild.id)
                user_exp.cat_count += 1
                session.add(user_exp)
                session.commit()
                return
        await interaction.followup.send("흑이를 소환하는데 실패했어요...")

    @app_commands.command(description='스위치 트리거를 사용했을 때 나올 수 있는 경우의 수를 표기합니다.')
    @app_commands.describe(switches='스위치의 갯수를 입력하거나 스위치의 이름을 입력해주세요. (이름은 `콤마,`를 기준으로 구분합니다.)',
                           flag='내 프로필 정보를 다른사람도 볼 수 있게 공개할지 선택합니다.')
    async def 스위치(self, interaction: Interaction[MynaBot], switches: str, flag: Literal['공개', '비공개'] = '비공개'):
        flag = False if flag == '공개' else True
        OPT = False
        IPT = []
        print_type = None
        try:
            switches = int(switches)
            if switches < 10:
                IPT = range(switches)
                print_type = "INT"
            else:
                OPT = True
        except:
            switches = list(map(lambda x : x.strip(), switches.split(',')))
            if len(switches) >= 10:
                OPT = True
                print_type = "STR"
            if len(switches) >= 2:
                IPT = switches
            else:
                OPT = True

        if OPT is True:
            embed = discord.Embed(title=f':x: 경우의 수 (스위치)',
                                  description=f'{interaction.user.mention} 사용할 스위치의 갯수를 입력해주세요.\n혹은 스위치 갯수가 10개이상이면 안됩니다.',
                                  color=0xffc0cb)
            embed.set_footer(text=f"{interaction.user.display_name} | 경우의 수", icon_url=interaction.user.display_avatar)
            await interaction.response.send_message(embed=embed, ephemeral=flag)
            return False

        res = []
        for c in list(itertools.chain.from_iterable(itertools.combinations(IPT, r) for r in range(len(IPT) + 1))):
            temp = ''
            for i in range(len(IPT)):
                le = IPT[i]
                if le not in c:
                    if print_type == "INT": temp += f'Switch({le}, Set);'
                    else: temp += f'Switch("{le}", Set);'
                else:
                    if print_type == "INT": temp += f'Switch({le}, Cleared);'
                    else: temp += f'Switch("{le}", Cleared);'
                if i != len(IPT) - 1:
                    temp += '\n'
            res.append(temp)
        await logs.send_log(
            bot=self.bot,
            log_text=f"{interaction.guild.name}의 {interaction.user.display_name}님이 스위치 명령어를 실행했습니다."
        )

        if len(res) > 16:
            embed = discord.Embed(title=f':gear: 경우의 수 (스위치)',
                                  description=f'{interaction.user.mention} 경우의 수입니다. 너무 많아서 텍스트파일로 업로드해요!\nTEP를 사용해서 조건에 붙여넣기해서 쓰시면 좋습니다.',
                                  color=0xffc0cb)
            embed.set_footer(text=f"{interaction.user.display_name} | 경우의 수", icon_url=interaction.user.display_avatar)
            with open('text.txt', 'w', encoding='utf-8') as l:
                for idx, _res in enumerate(res):
                    l.write(f"{idx + 1}번째\n{_res}\n\n")
            file = discord.File("text.txt")
            await interaction.response.send_message(embed=embed, file=file, ephemeral=flag)
        else:
            embed = discord.Embed(title=f':gear: 경우의 수 (스위치)',
                                  description=f'{interaction.user.mention} 경우의 수입니다.\nTEP를 사용해서 조건에 붙여넣기해서 쓰시면 좋습니다.',
                                  color=0xffc0cb)
            embed.set_footer(text=f"{interaction.user.display_name} | 경우의 수", icon_url=interaction.user.display_avatar)
            for idx, _res in enumerate(res):
                embed.add_field(name=f'{idx + 1}번째', value=f'{_res}')
            await interaction.response.send_message(embed=embed, ephemeral=flag)

    @app_commands.command(description='봇서버의 상태를 확인합니다.')
    @app_commands.describe(flag='내 프로필 정보를 다른사람도 볼 수 있게 공개할지 선택합니다.')
    async def 서버상태(self, interaction: Interaction[MynaBot], flag: Literal['공개', '비공개'] = '비공개') -> None:
        import psutil

        boot_time = ""
        with SessionContext() as session:
            status = session.query(Status).first()
            if status is not None:
                boot_time = f"{status.boot_time}에 부팅됨!"

        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_total = round(memory.total / (1024 ** 3), 2)
        memory_used = round(memory.used / (1024 ** 3), 2)
        memory_percent = memory.percent

        disk = psutil.disk_usage('/')
        dist_total = round(disk.total / (1024 ** 3), 2)
        dist_used = round(disk.used / (1024 ** 3), 2)
        dist_percent = disk.percent

        network = psutil.net_io_counters()
        bytes_sent = round(network.bytes_sent / (1024 ** 3), 2)
        bytes_received = round(network.bytes_recv / (1024 ** 3), 2)
        packets_sent = network.packets_sent
        packets_received = network.packets_recv

        embed = discord.Embed(title=f'🔍 서버 상태',
                              # description=f'현재 서버의 상태를 보여줘요.',
                              color=0x7ad380)
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.add_field(name="CPU", value=f'현재 CPU의 사용량은 `{cpu_percent}%`로 측정돼요!')
        embed.add_field(name="Memory", value=f'현재 RAM은 `{memory_total}GB` 중 `{memory_used}GB `({memory_percent}%)가 사용 중이에요.')
        embed.add_field(name="Disk", value=f'현재 Disk는 `{dist_total}GB` 중 `{dist_used}GB `({dist_percent}%)가 사용 중이에요.')
        embed.add_field(name="Network", value=f'현재 Network는 `{bytes_sent}GB`↑`{bytes_received}GB`↓ 전송/수신 했으며, 패킷수로는 {packets_sent}↑ {packets_received}↓으로 측정돼요!')
        embed.add_field(name="Bot", value=f"{len(self.bot.guilds)} 서버에 {self.bot.user.name}봇이 참여하고 있으며, 총 {sum(map(lambda x: x.member_count, self.bot.guilds))} 명이 이용 중이에요.")
        embed.set_footer(text=f"{boot_time}", icon_url=self.bot.user.display_avatar)

        flag = False if flag == '공개' else True
        await interaction.response.send_message(embed=embed, ephemeral=flag)

        await logs.send_log(bot=self.bot, log_text=f"{interaction.guild.name}의 {interaction.user.display_name}님이 서버상태 명령어를 실행했습니다.")


async def setup(bot):
    await bot.add_cog(Command(bot))
