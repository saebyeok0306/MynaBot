import discord, random, asyncio
from discord.ext import commands, tasks

class Command(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="도움말", aliases=["도움", "설명"])
    async def 도움말(self, ctx, *input):
        embed=discord.Embed(color=0xB22222, title="도움말:", description="마이나에게 있는 명령어들을 알려드려요. By.갈대")
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        embed.add_field(name = '!주사위 `값(기본값 100)`', value = '주사위를 굴립니다. 범위:1~100  값을 입력하면 1~값까지')
        # embed.add_field(name = '!계산 `수식`', value = '수식을 계산해줍니다.')
        # embed.add_field(name = '!마크', value = '디코방에서 운영되고 있는 서버주소를 알려줘요!')
        embed.add_field(name = f'!회원가입', value = f'디코게임을 이용하려면, 가입이 필요해요.')
        embed.add_field(name = f'!회원탈퇴', value = f'회원가입이 있으면 회원탈퇴도 있는법.')
        embed.add_field(name = f'!지원금', value = f'하루에 한번 지원금으로 3000원을 드립니다!')
        embed.add_field(name = f'!내정보', value = f'내가 보유한 재산이나 랭킹 순위를 볼 수 있어요.')
        embed.add_field(name = f'!순위', value = f'디스코드게임을 플레이하고 있는 유저들의 순위를 볼 수 있어요.')
        embed.add_field(name = f'!송금  `@유저명`  `금액`', value = f'다른 유저에게 돈을 보낼 수 있어요. **수수료 10%**')
        embed.add_field(name = f'!코인 도움말', value = f'!코인게임\n명령어를 확인할 수 있어요.')
        embed.add_field(name = f'!강화 도움말', value = f'!강화게임\n명령어를 확인할 수 있어요.')
        embed.add_field(name = f'!소코반 도움말', value = f'!소코반게임\n명령어를 확인할 수 있어요.')
        embed.add_field(name = f'!슬롯 도움말', value = f'!슬롯게임\n명령어를 확인할 수 있어요.')
        embed.add_field(name = f'!블랙잭 도움말', value = f'!블랙잭\n명령어를 확인할 수 있어요.')
        await ctx.channel.send(embed=embed)
    
    @commands.command(name="주사위", aliases=["다이스"])
    async def 주사위(self, ctx, *input):
        value = 100 # input이 없는 경우
        try:
            if input and int(input[0]) > 1: value = int(input[0])
        except: pass
        
        r = random.randint(1, value)
        await ctx.channel.send(f'주사위를 굴립니다...\n두둥! `{r}`입니다!')

def setup(bot):
    bot.add_cog(Command(bot))