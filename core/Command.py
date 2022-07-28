import discord, random, asyncio
from data.Timeout import timeout
from discord.ext import commands, tasks

class Command(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
    
    @commands.command(name="도움말", aliases=["도움", "설명"])
    async def 도움말(self, ctx):
        embed=discord.Embed(color=0xB22222, title="도움말:", description=f'{self.bot.user.name}에게 있는 명령어들을 알려드려요. By.갈대')
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        embed.add_field(name = '!주사위 `값(기본값 100)`', value = f'주사위를 굴립니다. 범위:1~100  값을 입력하면 1~값까지')
        embed.add_field(name = '!청소 `값(기본값 5)`', value = f'내가 작성한 메시지 N개를 삭제합니다. **！최대 20개**')
        embed.add_field(name = '!골라줘 `대상1` `대상2` ...', value = f'스페이스바 간격으로 구분된 대상들 중에서 하나를 선택해줘요!')
        embed.add_field(name = '!계산 `수식`', value = f'수식을 작성해서 넣으면, {self.bot.user.name}가 계산해서 알려줘요!')
        embed.add_field(name = f'!회원가입', value = f'서비스를 이용하려면, 가입이 필요해요.\n최종적으로 별명과 계정ID값만 사용해요.')
        embed.add_field(name = f'!회원탈퇴', value = f'회원가입이 있으면 회원탈퇴도 있는법.')
        embed.add_field(name = f'!서비스 도움말', value = f'회원가입하면 이용할 수 있는 명령어들을 모아뒀어요.')
        # embed.add_field(name = '!마크', value = '디코방에서 운영되고 있는 서버주소를 알려줘요!')
        await ctx.channel.send(embed=embed)
    
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
        await msg.delete(delay=2)
    
    @commands.command()
    async def 핑(self, ctx):
        embed = discord.Embed(color=0x2f3136)
        embed.set_author(name=f'{self.bot.user.name}봇의 지연시간(ms)')
        embed.set_thumbnail(url=self.bot.user.avatar_url)
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
        def Calculate(text):
            checkList = ['self', 'import', 'print']
            for check in checkList:
                if check in text:
                    return False
            return str(eval(text))
        
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
            if len(result) <= 1500: await ctx.channel.send(f'```{result}```')
            # 메시지의 길이가 1500을 넘기는 경우
            else:
                with open('text.txt', 'w', encoding='utf-8') as l:
                    l.write(result)
                file = discord.File("text.txt")
                await ctx.channel.send(f'실행 결과가 너무 길어서 파일로 출력했어요.')
                await ctx.channel.send(file=file)

    @commands.command(name="마크", aliases=['마인크래프트', '마크서버'])
    async def 마크(self, ctx, *input):
        embed=discord.Embed(color=0xB22222, title="산업모드서버", description="`갈대`의 1.18.2 포지서버", timestamp=ctx.message.created_at)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.add_field(name = '서버주소', value = 'westreed.kro.kr')
        embed.add_field(name = '서버문의', value = '@갈대#2519 에게 연락하세요!')
        embed.add_field(name = '서버모드', value = 'https://drive.google.com/drive/folders/1oT2hivIlCF9Cm5TIsFr3pK-vkvnw1zaT?usp=sharing')
        embed.add_field(name = '상세정보', value = '상세한 설명은 "!갈대서버"를 입력하세요.')
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=embed)
    
    @commands.command(name="갈대서버")
    async def 갈대서버(self, ctx, *input):
        embed=discord.Embed(color=0xB22222, title="갈대서버 상세설명", description="모드파일 : https://drive.google.com/drive/folders/1oT2hivIlCF9Cm5TIsFr3pK-vkvnw1zaT?usp=sharing\n넣는경로 : C:\\Users\\\계정명\\AppData\\Roaming\\\.minecraft\\mods", timestamp=ctx.message.created_at)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        embed.add_field(name = '설치순서1', value = '다운받은 파일 중, forge-1.18.2-40.1.0-installer.jar을 실행하여 1.18.2 포지를 설치한다.')
        embed.add_field(name = '설치순서2', value = 'userMods.zip을 마인크래프트 모드폴더에 풀어놓는다.')
        embed.add_field(name = '설치순서3', value = '마크런처에서 설치된 1.18.2 포지를 켜서, westreed.kro.kr 주소로 서버 접속하기.')
        await ctx.channel.send(embed=embed)
        

    

def setup(bot):
    bot.add_cog(Command(bot))