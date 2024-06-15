from collections import defaultdict

import discord, datetime
import utils.Utility as util
from discord.ext import commands

import utils.Logs as logs


class Administrator(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.suggest = defaultdict(int)
        self.timeout = defaultdict(int)

    @commands.command(name="관리자청소", aliases=["관리자삭제", "관리자제거", "관리자지우기"])
    async def 관리자청소(self, ctx, *input):
        if ctx.message.author.guild_permissions.administrator:
            remove = 5
            if len(input) >= 1 and input[0].isdigit():
                remove = int(input[0])

            await ctx.channel.purge(limit=remove + 1)
            msg = await ctx.channel.send(content=f'**{remove}개**의 메시지를 삭제했어요!')
            await msg.delete(delay=1)
            await logs.send_log(bot=self.bot,
                                log_text=f"{ctx.guild.name}의 {ctx.author.display_name}님이 관리자청소 명령어를 실행했습니다.")

    @commands.command(name="로그보기", aliases=["에러로그", "에러로그보기"])
    async def 로그보기(self, ctx, *input):
        if ctx.message.author.id == 383483844218585108:
            showPage = 9
            if len(input) == 1:
                if input[0] == 'all' or input[0] == 'All':
                    showPage = 0
                else:
                    try:
                        showPage = int(input[0])
                    except:
                        pass

            content = []
            with open('log/error.txt', 'r', encoding='utf-8') as l:
                header = ''
                _temp = ''
                while True:
                    text = l.readline()
                    if text == '': break
                    if text.startswith('user :'):
                        header = text.replace('\n', '').replace('user : ', '')
                        continue

                    if text == '\n':
                        _temp += text
                        _temp = _temp.replace('\n\n', '')
                        content.append([header, _temp])
                        _temp = ''
                    else:
                        _temp += text

            content.reverse()
            if showPage != 0:
                content = content[:showPage]

            embed = discord.Embed(color=0xFFA1A1, title=":scroll: 에러로그", description=f'에러를 기록한 로그를 취합합니다.')
            embed.set_footer(text=f"{ctx.author.display_name} | 에러로그", icon_url=ctx.author.display_avatar)
            for text in content:
                embed.add_field(name=f'{text[0]}', value=f'{text[1]}')
            await ctx.channel.send(embed=embed)
            await logs.send_log(bot=self.bot,
                                log_text=f"{ctx.guild.name}의 {ctx.author.display_name}님이 로그보기 명령어를 실행했습니다.")

    @commands.command(name="로그삭제", aliases=["로그지우기"])
    async def 로그삭제(self, ctx):
        if ctx.message.author.guild_permissions.administrator:
            with open('log/error.txt', 'w', encoding='utf-8') as l:
                l.write('')
            await ctx.channel.send(f'로그를 전부 지웠어요!')
            await logs.send_log(bot=self.bot,
                                log_text=f"{ctx.guild.name}의 {ctx.author.display_name}님이 로그삭제 명령어를 실행했습니다.")

    @commands.command(name="코드")
    async def 코드(self, ctx, *input):
        if ctx.message.author.id == 383483844218585108:
            text = " ".join(input)

            # @timeout(2, error_message='TimeoutError')
            def Calculate(self, ctx, text):
                return str(eval(text))

            result = False
            try:
                result = Calculate(self, ctx, text)
            except Exception as e:
                if type(e).__name__ == 'TimeoutError':
                    await ctx.channel.send(f'연산시간이 2초를 넘겨서 정지시켰어요.\n입력값 : {text}')
                else:
                    await ctx.channel.send(f'수식에 오류가 있어요.\n에러 : {e}')
                return 0

            if result is False:
                await ctx.channel.send(f'수식에 오류가 있어요.\n입력값 : {text}')
            else:
                # 결과 보내기
                if len(result) <= 1500:
                    await ctx.channel.send(f'```{result}```')
                # 메시지의 길이가 1500을 넘기는 경우
                else:
                    with open('text.txt', 'w', encoding='utf-8') as l:
                        l.write(result)
                    file = discord.File("text.txt")
                    await ctx.channel.send(f'실행 결과가 너무 길어서 파일로 출력했어요.')
                    await ctx.channel.send(file=file)

    @commands.command(name="SQL")
    async def SQL(self, ctx, *input):
        # if ctx.message.author.guild_permissions.administrator:
        if ctx.message.author.id == 383483844218585108:
            text = " ".join(input)

            # @timeout(2, error_message='TimeoutError')
            def Calculate(self, ctx, text):
                import sqlite3
                con = sqlite3.connect(r'data/DiscordDB.db', isolation_level=None)  # db 접속
                cur = con.cursor()
                cur.execute(text)

                if text.startswith('select') or text.startswith('SELECT'):
                    data = cur.fetchall()
                    con.close()  # db 종료
                    return data
                else:
                    con.close()  # db 종료
                    return text

            result = False
            try:
                result = Calculate(self, ctx, text)
            except Exception as e:
                if type(e).__name__ == 'TimeoutError':
                    await ctx.channel.send(f'연산시간이 2초를 넘겨서 정지시켰어요.\n입력값 : {text}')
                else:
                    await ctx.channel.send(f'SQL에 오류가 있어요.\n에러 : {e}')
                return 0

            if result is False:
                await ctx.channel.send(f'SQL에 오류가 있어요.\n입력값 : {text}')
            else:
                # 결과 보내기
                if len(result) <= 1500:
                    await ctx.channel.send(f'```{result}```')
                # 메시지의 길이가 1500을 넘기는 경우
                else:
                    with open('text.txt', 'w', encoding='utf-8') as l:
                        l.write(result)
                    file = discord.File("text.txt")
                    await ctx.channel.send(f'실행 결과가 너무 길어서 파일로 출력했어요.')
                    await ctx.channel.send(file=file)

    def AnnouncementEmbed(self, ctx, input):
        text = " ".join(input).replace("\\n", "\n")
        embed = discord.Embed(
            color=0xFFA1A1,
            title="[ 📢 마이나 공지사항 안내 ]",
            description=text
        )
        embed.set_footer(text=f"{ctx.author.display_name} | {datetime.datetime.now().strftime('%Y.%m.%d %H:%M')}",
                         icon_url=ctx.author.display_avatar)
        return embed

    @commands.command(name="공지사항테스트")
    async def 공지사항테스트(self, ctx, *input):
        if ctx.message.author.id == 383483844218585108:
            embed = self.AnnouncementEmbed(ctx, input)
            await ctx.channel.send(embed=embed)

    @commands.command(name="공지사항")
    async def 공지사항(self, ctx, *input):
        if ctx.message.author.id == 383483844218585108:
            embed = self.AnnouncementEmbed(ctx, input)

            guild_channels = util.get_bot_channel_guild(self.bot)
            for guild in guild_channels.keys():
                for channel in guild_channels[guild]:
                    await channel.send(embed=embed)

    @commands.command(name="건의", aliases=["제보", "버그"])
    async def 건의(self, ctx, *input):
        import time

        timestamp = int(time.time())
        if self.timeout.get(ctx.author.id):
            expired = self.timeout.get(ctx.author.id)
            if timestamp < expired:
                await ctx.reply(f"{expired-timestamp}초 뒤에 다시 시도해주세요.\n악용을 방지하기 위해서 시간을 제한했습니다.")
                return

        me = self.bot.get_user(383483844218585108)
        dm = await me.create_dm()
        text = " ".join(input)
        guild_name = ctx.guild.name if ctx.guild else "dm"
        embed = discord.Embed(
            color=0x1e1f22,
            title=f"[ {ctx.author.display_name}님 ]",
            description=text
        )
        embed.set_footer(text=f"{ctx.author.display_name} | {guild_name} |  {datetime.datetime.now().strftime('%Y.%m.%d %H:%M')}",
                         icon_url=ctx.author.display_avatar)

        await dm.send(embed=embed, mention_author=False)
        expired = self.timeout.get(ctx.author.id)
        if expired is None:
            expired = timestamp

        if expired-timestamp < 60*60*24:
            self.suggest[ctx.author.id] += 1
            self.timeout[ctx.author.id] = timestamp + pow(2, self.suggest[ctx.author.id]+3)

        await ctx.reply(f"갈대님에게 메시지를 전송했어요!")
        await logs.send_log(bot=self.bot,
                            log_text=f"{guild_name}의 {ctx.author.display_name}님이 건의 명령어를 실행했습니다.")


async def setup(bot):
    await bot.add_cog(Administrator(bot))
