import discord, random, asyncio
from data.Timeout import timeout
from discord.ext import commands, tasks

class Command(commands.Cog):

    def __init__(self, bot):
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
        remove = 5
        if len(input) >= 1 and input[0].isdigit():
            remove = int(input[0])
        
        text = ''
        if remove > 20:
            remove = 20
            text += f'메시지는 최대 20개까지만 지울 수 있어요.\n'

        text += f'**{remove}개**의 메시지를 삭제했어요!'

        def is_me(message): return message.author == ctx.author
        await ctx.channel.purge(limit=remove+1, check=is_me)
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
            if 'self' in text or 'import' in text or 'print' in text: return False
            return str(eval(text))
        
        try: result = Calculate(text)
        except Exception as e:
            if e == 'Timer expired': await ctx.channel.send(f'너무 `무리한 연산`을 요구하지 말아주세요..!!\n입력값 : {text}')
            else: await ctx.channel.send(f'수식에 오류가 있어요.\n입력값 : {text}')
        if result is False:
            await ctx.channel.send(f'수식에 오류가 있어요.\n입력값 : {text}')
        else:
            if len(result) <= 1500: await ctx.channel.send(f'```{result}```')
            else:
                with open('text.txt', 'w', encoding='utf-8') as l:
                    l.write(result)
                file = discord.File("text.txt")
                await ctx.channel.send(f'계산결과가 너무 길어서 파일로 출력했어요.')
                await ctx.channel.send(file=file)
        

    

def setup(bot):
    bot.add_cog(Command(bot))