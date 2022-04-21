import sqlite3, discord, asyncio, datetime, re
import data.Functions as fun
from discord.ext import commands, tasks

class GameService(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.title = '게임서비스'
    
    @commands.command()
    async def 회원가입(self, ctx):
        if(ctx.channel.id in fun.getBotChannel(ctx)):
            id = ctx.author.id
            check = fun.game_check(id)
            con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
            cur = con.cursor()
            now = datetime.datetime.now()
            nowDatetime = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
            if check == False:
                null = 'NULL'
                cur.execute("INSERT INTO User_Info VALUES(?, ?, ?, ?, ?, ?, ?)", (id, ctx.author.display_name, nowDatetime, 0, null, 0, 0))
                embed = discord.Embed(title = f':wave: {self.title} 가입', description = f'{ctx.author.mention} 성공적으로 갈대의 {self.title}에 가입되셨습니다.', color = 0xffc0cb)
                embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.avatar_url)
                await ctx.channel.send(embed = embed)
            elif check == True:
                embed = discord.Embed(title = f':wave: {self.title} 가입', description = f'{ctx.author.mention} 이미 {self.title}에 가입되어 있습니다.', color = 0xff0000)
                embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.avatar_url)
                await ctx.channel.send(embed = embed)
            con.close() #db 종료

    @commands.command()
    async def 회원탈퇴(self, ctx):
        if(ctx.channel.id in fun.getBotChannel(ctx)):
            id = ctx.author.id
            check = fun.game_check(id)
            con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
            cur = con.cursor()
            cur.execute("SELECT user_Date FROM User_Info WHERE user_ID = ?", (id,))
            userInfo = cur.fetchone()
            now = datetime.datetime.now()
            joindate = datetime.datetime.strptime(userInfo[0], '%Y-%m-%d %H:%M:%S')
            if now.day != joindate.day:
                if check == False:
                    embed = discord.Embed(title = f':heart: {self.title} 탈퇴', description = f'{ctx.author.mention} 갈대의 {self.title}에 가입되어 있지 않습니다.', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.avatar_url)
                    await ctx.channel.send(embed = embed)
                elif check == True:
                    cur.execute("DELETE FROM 'User_Info' WHERE user_ID = ?", (id,))
                    cur.execute("DELETE FROM 'Coin_Trade' WHERE trade_UserID = ?", (id,))
                    cur.execute("DELETE FROM 'Coin_NameList' WHERE user_ID = ?", (id,))
                    cur.execute("DELETE FROM 'Sword_Info' WHERE sword_UserID = ?", (id,))
                    embed = discord.Embed(title = f':heart: {self.title} 탈퇴', description = f'{ctx.author.mention} 성공적으로 {self.title}에서 탈퇴되셨습니다.', color = 0xffc0cb)
                    embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.avatar_url)
                    await ctx.channel.send(embed = embed)
            else:
                embed = discord.Embed(title = f':x: {self.title} 탈퇴불가능', description = f'{ctx.author.mention} 가입한 날로부터 하루가 지나야 합니다!\n가입날짜 `{joindate.year}년 {joindate.month}월 {joindate.day}일`', color = 0xff0000)
                embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.avatar_url)
                await ctx.channel.send(embed = embed)
            con.close() #db 종료
    
    @commands.command(name="내정보", aliases=["정보창", "내정보창", "상태창"])
    async def 내정보(self, ctx):
        if(ctx.channel.id in fun.getBotChannel(ctx)):
            id = ctx.author.id
            con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
            cur = con.cursor()
            cur.execute("SELECT user_Name, user_Money, slot_Betting, slot_Reward FROM User_Info WHERE user_ID = ?", (id,))
            userInfo = cur.fetchone()
            con.close() #db 종료
            myName, myMoney, myBetting, myReward = userInfo
            PMText = ['-', '+']
            moneyPercent = 0
            moneyPM, costMoney, currentValue = fun.game_coinValue(id)
            totalValue = currentValue+myMoney
            if costMoney:
                if currentValue < costMoney: moneyPercent = round(((costMoney-currentValue)/costMoney)*100, 2)
                else: moneyPercent = round(((currentValue-costMoney)/costMoney)*100, 2)
            
            slotPM,slotDiffMoney = 0,0
            if myBetting > myReward:
                slotPM = 0
                slotDiffMoney = myBetting-myReward
            else:
                slotPM = 1
                slotDiffMoney = myReward-myBetting

            embed = discord.Embed(title = f'{ctx.author.display_name}님의 정보창', description = f'디스코드 게임에서의 본인 정보입니다.\n현금 재산은 모든 게임에서 공유됩니다.', color = 0xffc0cb)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            if costMoney:
                embed.add_field(name = f'코인 재산', value = f':coin:`{fun.printN(currentValue)}원`\n　 `({PMText[moneyPM]}{moneyPercent}%)`')
            else:
                embed.add_field(name = f'코인 재산', value = f':coin:`0원`\n　 `(0%)`')
            embed.add_field(name = f'현금 재산', value = f':dollar:`{fun.printN(myMoney)}원`')
            embed.add_field(name = f'총 재산', value = f':money_with_wings:`{fun.printN(totalValue)}원`')

            embed.add_field(name = f'총 배팅액', value = f'`{fun.printN(myBetting)}원`')
            embed.add_field(name = f'총 당첨액', value = f'`{fun.printN(myReward)}원`')
            embed.add_field(name = f'손익률', value = f'`{PMText[slotPM]}{fun.printN(slotDiffMoney)}원`')

            userRank, userNumber = fun.coin_GetRank(id)
            if userRank == False:
                embed.add_field(name = f'재산 랭킹', value = f':white_small_square:`없음`')
            else:
                embed.add_field(name = f'재산 랭킹', value = f':white_small_square:`{userRank}/{userNumber}위`')
            await ctx.channel.send(embed = embed)
    
    @commands.command(name="순위", aliases=["랭킹","랭킹순위","순위표"])
    async def 순위(self, ctx):
        if(ctx.channel.id in fun.getBotChannel(ctx)):
            id = ctx.author.id
            userRanking_, userNumber = fun.coin_Ranking(1)
            embed = discord.Embed(title = f'디스코드 게임 순위', description = f'가입한 모든 유저의 랭킹입니다.', color = 0xffc0cb)
            rankIndex,rankSameMoney = 0,0

            for rank in userRanking_:
                if rankSameMoney != rank[1]: rankIndex += 1
                rankSameMoney = rank[1]
                embed.add_field(name = f'{rankIndex}위 {rank[0]}님', value = f'추정재산 `{fun.printN(rank[1])}원`')
            embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.avatar_url)
            await ctx.channel.send(embed = embed)
    
    @commands.command()
    async def 송금(self, ctx, *input):
        if(ctx.channel.id in fun.getBotChannel(ctx)):
            try:
                id = ctx.author.id
                a = input[1]
                userid = re.findall(r"[0-9]+", a)
                userid = userid[0]
                tradeMoney = int(input[2])
                con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                cur = con.cursor()
                cur.execute("SELECT user_Name, user_Money FROM User_Info WHERE user_ID = ?", (id,))
                myUser = cur.fetchone()
                myName, myMoney = myUser

                cur.execute("SELECT user_Name, user_Money FROM User_Info WHERE user_ID = ?", (userid,))
                targetUser = cur.fetchone()
                if not targetUser:
                    embed = discord.Embed(title = f':x: 송금 실패', description = f'입력하신 사용자는 가입하지 않은 유저입니다!', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.avatar_url)
                    await ctx.channel.send(embed = embed)
                    con.close() #db 종료
                    return 0
                if targetUser[0] == ctx.author.display_name:
                    embed = discord.Embed(title = f':x: 송금 실패', description = f'{ctx.author.mention} 자기 자신에게 송금할 수 없습니다!', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.avatar_url)
                    await ctx.channel.send(embed = embed)
                    con.close() #db 종료
                    return 0
                targetName = targetUser[0]      # 대상 이름
                targetMoney = targetUser[1]     # 대상이 가지고 있는 돈
                chargeMoney = tradeMoney // 10  # 지불할 수수료 10%
                if myMoney >= tradeMoney:
                    myMoney -= tradeMoney
                    targetMoney += tradeMoney-chargeMoney
                    cur.execute("UPDATE 'User_Info' SET user_Money = ? WHERE user_ID = ?", (myMoney, id,))
                    cur.execute("UPDATE 'User_Info' SET user_Money = ? WHERE user_ID = ?", (targetMoney, userid,))
                    embed = discord.Embed(title = f':page_with_curl: 송금 성공', description = f'{targetName}님에게 `{fun.printN(tradeMoney-chargeMoney)}원`을 송금했습니다!\n**수수료 {fun.printN(chargeMoney)}원** (10%) │ 남은재산 `{fun.printN(myMoney)}원` :money_with_wings:', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.avatar_url)
                    await ctx.channel.send(embed = embed)
                else:
                    embed = discord.Embed(title = f':exclamation: 송금 실패', description = f'{ctx.author.mention} 돈이 부족합니다. 보유재산 `{fun.printN(myMoney)}원` :money_with_wings:', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.avatar_url)
                    await ctx.channel.send(embed = embed)
                con.close() #db 종료
            except:
                embed = discord.Embed(title = f':x: 송금 실패', description = f'{ctx.author.mention} 명령어가 잘못되었습니다.\n**!코인 송금 [@유저] [금액]**의 형태로 입력해보세요.', color = 0xff0000)
                embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.avatar_url)
                await ctx.channel.send(embed = embed)
                return 0

    @commands.command(name="지원금", aliases=["지원"])
    async def 지원금(self, ctx):
        if(ctx.channel.id in fun.getBotChannel(ctx)):
            id = ctx.author.id
            con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
            cur = con.cursor()
            cur.execute("SELECT user_Money, user_Support FROM User_Info WHERE user_ID = ?", (id,))
            userInfo = cur.fetchone()
            userMoney = userInfo[0]
            now = datetime.datetime.now()
            passTicket = False
            fundtime = 0
            bonusMoney = 3000
            if userInfo[1] == 'NULL':
                passTicket = True
            else:
                fundtime = datetime.datetime.strptime(userInfo[1], '%Y-%m-%d %H:%M:%S')
                if now.day != fundtime.day:
                    passTicket = True
            if passTicket:
                nowDatetime = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
                cur.execute("UPDATE 'User_Info' SET user_Money = ?, user_Support = ? WHERE user_ID = ?", (userMoney+bonusMoney, nowDatetime, id))
                embed = discord.Embed(title = f':gift: {self.title} 지원금', description = f'{ctx.author.mention} 지원금을 받으셨습니다! `+{bonusMoney}원`\n＃지원금은 하루에 한번씩만 받으실 수 있습니다.', color = 0xffc0cb)
                embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.avatar_url)
                await ctx.channel.send(embed = embed)
            else:
                embed = discord.Embed(title = f':watch: {self.title} 지원금', description = f'{ctx.author.mention} 지원금은 하루에 한번 씩 받을 수 있습니다.\n- {fundtime.year}년 {fundtime.month}월 {fundtime.day}일에 지원금을 받았음.', color = 0xff0000)
                embed.set_footer(text = f"{ctx.author.display_name} | {self.title}", icon_url = ctx.author.avatar_url)
                await ctx.channel.send(embed = embed)
            con.close() #db 종료
    
def setup(bot):
    bot.add_cog(GameService(bot))