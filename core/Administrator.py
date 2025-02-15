from collections import defaultdict
from typing import Literal, Optional

import discord, datetime
from discord import app_commands, Interaction
from discord.ext.commands import Context

import utils.Utility as util
from discord.ext import commands

import utils.Logs as logs
from main import MynaBot


class Administrator(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot: MynaBot = bot
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

        else:
            msg = await ctx.reply(f"관리자에게만 허용된 명령어에요.", mention_author=True)
            await msg.delete(delay=5)
            await ctx.message.delete(delay=5)
            return

    @commands.command(name="로그보기", aliases=["에러로그", "에러로그보기"])
    async def 로그보기(self, ctx, *input):
        if util.is_developer(ctx.author):
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
        if util.is_developer(ctx.author):
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
        if util.is_developer(ctx.author):
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
        if util.is_developer(ctx.author):
            embed = self.AnnouncementEmbed(ctx, input)
            await ctx.channel.send(embed=embed)

    @commands.command(name="공지사항")
    async def 공지사항(self, ctx, *input):
        if util.is_developer(ctx.author):
            embed = self.AnnouncementEmbed(ctx, input)

            guild_channels = util.get_bot_channel_guild(self.bot)
            for guild in guild_channels.keys():
                for channel in guild_channels[guild]:
                    await channel.send(embed=embed)

    # @commands.command(name="건의", aliases=["제보", "버그"])
    @app_commands.command(description='개발자에게 문의사항을 전달합니다.')
    @app_commands.describe(message='문의사항을 작성해주세요.')
    async def 문의(self, interaction: Interaction[MynaBot], message: str):
        import time

        timestamp = int(time.time())
        if self.timeout.get(interaction.user.id):
            expired = self.timeout.get(interaction.user.id)
            if timestamp < expired:
                await interaction.response.send_message(f"{expired-timestamp}초 뒤에 다시 시도해주세요.\n악용을 방지하기 위해서 시간을 제한했습니다.", ephemeral=True)
                return

        me = self.bot.get_user(383483844218585108)
        dm = await me.create_dm()
        guild_name = interaction.guild.name if interaction.guild else "dm"
        embed = discord.Embed(
            color=0x1e1f22,
            title=f"[ {interaction.user.display_name}님 ]",
            description=message
        )
        embed.set_footer(text=f"{interaction.user.display_name} | {guild_name} |  {datetime.datetime.now().strftime('%Y.%m.%d %H:%M')}",
                         icon_url=interaction.user.display_avatar)

        await dm.send(embed=embed, mention_author=False)
        expired = self.timeout.get(interaction.user.id)
        if expired is None:
            expired = timestamp

        if expired-timestamp < 60*60*24:
            self.suggest[interaction.user.id] += 1
            self.timeout[interaction.user.id] = timestamp + pow(2, self.suggest[interaction.user.id]+3)

        await interaction.response.send_message(f"갈대님에게 메시지를 전송했어요!", ephemeral=True)
        await logs.send_log(bot=self.bot,
                            log_text=f"{guild_name}의 {interaction.user.display_name}님이 문의 명령어를 실행했습니다.")

    @commands.command()
    async def 싱크(self, ctx: commands.Context[MynaBot], sync_type: Literal['guild', 'global']):
        """Sync the application commands"""
        if not util.is_developer(ctx.author):
            return
        async with ctx.typing():
            if sync_type == 'guild':
                self.bot.tree.copy_global_to(guild=ctx.guild)  # type: ignore
                await self.bot.tree.sync(guild=ctx.guild)
                msg = await ctx.reply(f'{ctx.guild.name} 서버에서 명령어 동기화를 진행합니다.')
                await msg.delete(delay=5)
                return

            await self.bot.tree.sync()
            msg = await ctx.reply('전역 명령어 동기화를 진행합니다.')
            await msg.delete(delay=5)

    @commands.command()
    async def 언싱크(self, ctx: commands.Context[MynaBot], unsync_type: Literal['guild', 'global']) -> None:
        """Unsync the application commands"""
        if not util.is_developer(ctx.author):
            return
        async with ctx.typing():
            if unsync_type == 'guild':
                self.bot.tree.clear_commands(guild=ctx.guild)
                await self.bot.tree.sync(guild=ctx.guild)
                msg = await ctx.reply(f'{ctx.guild.name} 서버에서 명령어 동기화를 해제합니다.')
                await msg.delete(delay=5)
                return

            self.bot.tree.clear_commands()  # type: ignore
            await self.bot.tree.sync()
            msg = await ctx.reply('전역 명령어 동기화를 해제합니다.')
            await msg.delete(delay=5)

    @commands.command()
    async def 버엄령(self, ctx: commands.Context[MynaBot], ids: Optional[str] = None) -> None:
        if not util.is_developer(ctx.author):
            return

        flag = self.bot.BCFlag
        self.bot.BCFlag = not flag

        if flag:
            await ctx.reply("버엄령을 중지합니다.", mention_author=False)
        else:
            if ids:
                id_list = list(map(lambda x: x.strip(), ids.split(",")))
                with open('data/BC.txt', 'w', encoding='utf-8') as l:
                    l.write("\n".join(id_list))
            else:
                with open('data/BC.txt', 'r', encoding='utf-8') as f:
                    id_list = f.read().split('\n')
            self.bot.BC_LIST.clear()
            self.bot.BC_LIST.extend(id_list)
            msg = "버엄령을 시작합니다.\n대상은"
            for sid in id_list:
                target = ctx.guild.get_member(int(sid))
                msg += f" {target.display_name}"
            msg += "입니다."
            await ctx.reply(msg, mention_author=False)



async def setup(bot):
    await bot.add_cog(Administrator(bot))
