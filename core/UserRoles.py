import sqlite3, discord, asyncio, random, math
import data.Functions as fun
from discord.ext import commands

class UserRoles(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.title = '게임서비스'
    
    @commands.command(name="색상변경", aliases=['색상수정'])
    async def 색상변경(self, ctx, *input):
        if fun.game_check(ctx.author.id) is False:
            embed = discord.Embed(title = f':exclamation: {self.title} 미가입', description = f'{ctx.author.mention} {self.title} 게임에 가입하셔야 이용이 가능합니다. (!회원가입)', color = 0xff0000)
            embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.avatar_url)
            await ctx.channel.send(embed = embed)
            return False
        
        guild = ctx.guild
        user  = ctx.author

        con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
        cur = con.cursor()
        cur.execute("SELECT user_Money FROM User_Info WHERE user_ID = ?", (user.id,))
        myMoney = int(cur.fetchone()[0])
        con.close() #db 종료

        if myMoney < 1000000:
            embed = discord.Embed(title = f':moneybag: 돈부족', description = f'{ctx.author.mention} 닉네임 색상을 변경하시려면,\n`{fun.printN(1000000)}원`을 소지하고 계셔야 합니다.\n\n보유재산 `{fun.printN(myMoney)}원` :money_with_wings:', color = 0xff0000)
            embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.avatar_url)
            await ctx.channel.send(embed = embed)
            return False
        
        colorLists = {
            '빨강' : 'e97d7d',
            '주황' : 'e67e22',
            '노랑' : 'f1c40f',
            '핑크' : 'e91e63',
            '보라' : '9b59b6',
            '파랑' : '3498db',
            '연두' : '2ecc71',
            '민트' : '51ffc9'
        }

        if len(input) >= 1:
            colors = 0
            input_color = input[0]
            if input_color[:2] == '0x':
                colors = int(input_color, 16)
            elif colorLists.get(input_color):
                colors = int(colorLists[input_color], 16)
            else:
                embed = discord.Embed(title = f':tickets: 안내', description = f'{ctx.author.mention} 색상을 입력하실 땐, 색상코드(0x51FFC9)와 같이 입력하시거나 기본 색상이름을 쓰시면 됩니다.', color = 0x51ffc9)
                embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.avatar_url)
                await ctx.channel.send(embed = embed)
                return False

            roleName = fun.returnRoleName(user.id)
            if roleName is not None:
                for role in user.roles:
                    if role.name == roleName:
                        await role.edit(color=colors)

                        myMoney -= 1000000
                        con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                        cur = con.cursor()
                        cur.execute("UPDATE 'User_Info' SET user_Money = ? WHERE user_ID = ?", (str(myMoney), user.id))
                        con.close() #db 종료

                        embed = discord.Embed(title = f':star2: 닉네임 색상변경', description = f'{ctx.author.mention} 색상변경이 완료되었어요!\n남은재산 `{fun.printN(myMoney)}원` :money_with_wings:', color = colors)
                        embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.avatar_url)
                        await ctx.channel.send(embed = embed)
                        return True
            
            # return True 가 작동하지 않은 경우
            await fun.createUserRole(guild, user)
            embed = discord.Embed(title = f':tickets: 안내', description = f'{ctx.author.mention} 생성된 역할이 없어서, 새롭게 역할을 생성했습니다.\n다시 한번더 색상변경 명령어를 사용해주세요.', color = 0xFF0000)
            embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.avatar_url)
            await ctx.channel.send(embed = embed)

        else:
            return False

def setup(bot):
    bot.add_cog(UserRoles(bot))