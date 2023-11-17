import discord, random, asyncio, datetime, math, itertools
import data.Functions as fun
from data.Timeout import timeout
from discord.ext import commands, tasks

class Command(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.title = "마이나"
    
    @commands.command(name="도움말", aliases=["도움", "설명"])
    async def 도움말(self, ctx):
        embed=discord.Embed(color=0xB22222, title="도움말:", description=f'{self.bot.user.name}에게 있는 명령어들을 알려드려요. By.갈대')
        embed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
        embed.add_field(name = f'!회원가입', value = f'서비스를 이용하려면, 가입이 필요해요.\n최종적으로 별명과 계정ID값만 사용해요.')
        embed.add_field(name = f'!회원탈퇴', value = f'회원가입이 있으면 회원탈퇴도 있는법.')
        embed.add_field(name = '!주사위 `값(기본값 100)`', value = f'주사위를 굴립니다. 범위:1~100  값을 입력하면 1~값까지')
        embed.add_field(name = '!청소 `값(기본값 5)`', value = f'내가 작성한 메시지 N개를 삭제합니다. **！최대 20개**')
        embed.add_field(name = '!골라줘 `대상1` `대상2` ...', value = f'스페이스바 간격으로 구분된 대상들 중에서 하나를 선택해줘요!')
        embed.add_field(name = '!계산 `수식`', value = f'수식을 작성해서 넣으면, {self.bot.user.name}가 계산해서 알려줘요!')
        embed.add_field(name = f'!색상변경 `색상`', value = f'닉네임 색상을 변경할 수 있어요!')
        embed.add_field(name = f'!한영번역 `내용`', value = f'한국어를 영어로 번역해줘요!')
        embed.add_field(name = f'!영한번역 `내용`', value = f'영어를 한국어로 번역해줘요!')
        embed.add_field(name = f'!스위치 `갯수` or `이름1 이름2 이름3 ...`', value = f'스위치를 N개 사용했을 때\n나올 수 있는 경우의 수를 표기합니다.')
        embed.add_field(name = f'!마이나야 `질문`', value = f'ChatGPT를 활용해서 질문에 대한 답변을 해줘요!')
        embed.add_field(name = f'!초기화', value=f'마이나에게 질문한 대화내역을 초기화해요.')
        embed.add_field(name = f'!대화내역', value=f'마이나와 대화중인 방목록을 보여줘요.')
        # embed.add_field(name = f'!서비스 도움말', value = f'회원가입하면 이용할 수 있는 명령어들을 모아뒀어요.')
        # embed.add_field(name = '!마크', value = '디코방에서 운영되고 있는 서버주소를 알려줘요!')
        if ctx.guild.id in [631471244088311840]:
            embed.add_field(name = f'!흑이', value = f'노나메님의 ~~납치~~하고 싶은 흑이사진이 나와요!')
        await ctx.channel.send(embed=embed)
    
    @commands.command(name="가입명령", aliases=["가입", "회원가입"])
    async def 회원가입(self, ctx):
        import sqlite3
        if(ctx.channel.id in fun.getBotChannel(self.bot, ctx)):
            id = ctx.author.id
            if fun.game_check(id) is False:
                now = datetime.datetime.now()
                nowDatetime = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
                con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                cur = con.cursor()
                cur.execute("INSERT INTO User_Info VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (id, ctx.author.display_name, nowDatetime, 0, 'NULL', 0, 0, 'NULL'))
                con.close() #db 종료
                await fun.createUserRole(ctx.guild, ctx.author)
                embed = discord.Embed(title = f':wave: {self.title} 가입', description = f'{ctx.author.mention} 성공적으로 갈대의 {self.title}에 가입되셨습니다.\n수집되는 데이터는 유저의 별명과 사용자아이디(별명#0000)만 사용됩니다!', color = 0xffc0cb)
                embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.display_avatar)
                await ctx.channel.send(embed = embed)
            else:
                embed = discord.Embed(title = f':wave: {self.title} 가입', description = f'{ctx.author.mention} 이미 {self.title}에 가입되어 있습니다.', color = 0xff0000)
                embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.display_avatar)
                await ctx.channel.send(embed = embed)

    @commands.command(name="탈퇴명령", aliases=["탈퇴", "회원탈퇴"])
    async def 회원탈퇴(self, ctx):
        if(ctx.channel.id in fun.getBotChannel(self.bot, ctx)):
            id = ctx.author.id
            if fun.game_check(id) is False:
                embed = discord.Embed(title = f':heart: {self.title} 탈퇴', description = f'{ctx.author.mention} 갈대의 {self.title}에 가입되어 있지 않습니다.', color = 0xff0000)
                embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.display_avatar)
                await ctx.channel.send(embed = embed)
                return False

            nowdate = datetime.datetime.now()
            joindate = fun.returnJoinDate(id)
            if nowdate.day != joindate.day:
                await fun.deleteUserRole(ctx.guild, ctx.author) # delete role
                fun.removeUserDB(id) # db에서 데이터 삭제
                embed = discord.Embed(title = f':heart: {self.title} 탈퇴', description = f'{ctx.author.mention} 성공적으로 {self.title}에서 탈퇴되셨습니다.', color = 0xffc0cb)
                embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.display_avatar)
                await ctx.channel.send(embed = embed)
            else:
                embed = discord.Embed(title = f':x: {self.title} 탈퇴불가능', description = f'{ctx.author.mention} 가입한 날로부터 하루가 지나야 합니다!\n가입날짜 `{joindate.year}년 {joindate.month}월 {joindate.day}일`', color = 0xff0000)
                embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.display_avatar)
                await ctx.channel.send(embed = embed)
    
    @commands.command(name="주사위", aliases=["다이스"])
    async def 주사위(self, ctx, *input):
        value = 100 # input이 없는 경우
        try:
            if input and int(input[0]) > 1: value = int(input[0])
        except: pass
        
        r = random.randint(1, value)
        await ctx.channel.send(f'주사위를 굴립니다...\n두둥! `{r}`입니다!')
    
    @commands.command(name="청소", aliases=["메시지청소","삭제","메시지삭제","제거","메시지제거","지우기","메시지지우기"])
    async def 청소(self, ctx, *input):
        remove = 6
        if len(input) >= 1 and input[0].isdigit():
            remove = int(input[0])+1
        
        text = ''
        if remove > 21:
            remove = 21
            text += f'메시지는 최대 20개까지만 지울 수 있어요.\n'

        text += f'**{remove-1}개**의 메시지를 삭제했어요!'

        async for message in ctx.channel.history(limit=None):
            if remove:
                if message.author == ctx.author:
                    await message.delete()
                    remove -= 1
            else:
                break

        # def is_me(message): return message.author == ctx.author
        # await ctx.channel.purge(limit=remove+1, check=is_me)
        msg = await ctx.channel.send(content = text)
        await msg.delete(delay=5)
    
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
    
    @commands.command(name="계산기", aliases=['계산', '계산해줘'])
    async def 계산(self, ctx, *input):
        text = " ".join(input)

        @timeout(1)
        def Calculate(_text_):
            for _check_ in ['self', 'import', 'print', 'Quitter', '_', 'eval', 'exec']:
                if _check_ in _text_:
                    return False
            return str(eval(_text_))
        
        result = False
        try: result = Calculate(text)
        except Exception as e:
            if type(e).__name__ == 'TimeoutError':
                await ctx.channel.send(f'연산시간이 1초를 넘겨서 정지시켰어요.\n입력값 : {text}')
            else:
                await ctx.channel.send(f'수식에 오류가 있어요.\n에러 : {e}')
            return 0
        
        if result is False:
            await ctx.channel.send(f'수식에 오류가 있어요.\n입력값 : {text}')
        else:
            # 결과 보내기
            if len(result) <= 1500:
                try: result = f"{result} ({fun.printN(int(result))})"
                except: pass
                await ctx.channel.send(f'```{result}```')
            # 메시지의 길이가 1500을 넘기는 경우
            else:
                with open('text.txt', 'w', encoding='utf-8') as l:
                    l.write(result)
                file = discord.File("text.txt")
                await ctx.channel.send(f'실행 결과가 너무 길어서 파일로 출력했어요.')
                await ctx.channel.send(file=file)

    @commands.command(name="흑이", aliases=['흑', '냥나메', '노나메', '노냥메', 'noname01'])
    async def 흑이(self, ctx):
        if ctx.guild.id in [631471244088311840]:
            if(ctx.channel.id in fun.getBotChannel(self.bot, ctx)):
                import urllib.request
                api_url = "http://ajwmain.iptime.org/7Z2R7J2064qUIOygleunkCDqt4Dsl6zsmrQg6rKA7J2AIOqzoOyWkeydtCEh/black_cat.php"
                request = urllib.request.Request(api_url)
                response = urllib.request.urlopen(request)
                rescode = response.getcode()
                if(rescode==200):
                    response_body = response.read()
                    response_body = response_body.decode('utf-8')
                    try:
                        urllib.request.urlretrieve(response_body, "explain.png")
                        file = discord.File("explain.png")
                        await ctx.channel.send(file=file)
                    except:
                        await ctx.channel.send(response_body)
            else:
                msg = await ctx.reply(f"흑이 소환은 `봇명령` 채널에서만 가능해요.")
                await msg.delete(delay=5)
                await ctx.message.delete(delay=5)

    

    @commands.command(name="스위치", aliases=['경우의수'])
    async def 스위치(self, ctx, *input):
        OPT = False
        IPT = []
        if len(input) >= 10: OPT = True
        elif len(input) == 1 and input[0].isdigit():
            if int(input[0]) < 10:
                IPT = range(int(input[0]))
            else:
                OPT = True
        elif len(input) >= 2: IPT = input
        else: OPT = True
        
        if OPT is True:
            embed = discord.Embed(title = f':x: 경우의 수 (스위치)', description = f'{ctx.author.mention} 사용할 스위치의 갯수를 입력해주세요.\n혹은 스위치 갯수가 10개이상이면 안됩니다.', color = 0xffc0cb)
            embed.set_footer(text = f"{ctx.author.display_name} | 경우의 수", icon_url = ctx.author.display_avatar)
            await ctx.channel.send(embed = embed)
            return False
        res = []
        for c in list(itertools.chain.from_iterable(itertools.combinations(IPT, r) for r in range(len(IPT)+1))):
            temp = ''
            for i in range(len(IPT)):
                le = IPT[i]
                if le not in c:
                    temp += (f'Switch("{le}", Set);')
                else:
                    temp += (f'Switch("{le}", Cleared);')
                if i != len(IPT)-1: temp += '\n'
            res.append(temp)

        if len(res) > 16:
            embed = discord.Embed(title = f':gear: 경우의 수 (스위치)', description = f'{ctx.author.mention} 경우의 수입니다. 너무 많아서 텍스트파일로 업로드해요!\nTEP를 사용해서 조건에 붙여넣기해서 쓰시면 좋습니다.', color = 0xffc0cb)
            embed.set_footer(text = f"{ctx.author.display_name} | 경우의 수", icon_url = ctx.author.display_avatar)
            await ctx.channel.send(embed = embed)
            with open('text.txt', 'w', encoding='utf-8') as l:
                for idx, _res in enumerate(res):
                    l.write(f"{idx+1}번째\n{_res}\n\n")
            file = discord.File("text.txt")
            await ctx.channel.send(file=file)
        else:
            embed = discord.Embed(title = f':gear: 경우의 수 (스위치)', description = f'{ctx.author.mention} 경우의 수입니다.\nTEP를 사용해서 조건에 붙여넣기해서 쓰시면 좋습니다.', color = 0xffc0cb)
            embed.set_footer(text = f"{ctx.author.display_name} | 경우의 수", icon_url = ctx.author.display_avatar)
            for idx, _res in enumerate(res):
                embed.add_field(name = f'{idx+1}번째', value = f'{_res}')
            await ctx.channel.send(embed = embed)
    

async def setup(bot):
    await bot.add_cog(Command(bot))