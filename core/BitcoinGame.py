import sqlite3, discord, asyncio, datetime, random, re
import data.Functions as fun
from collections import defaultdict
from discord.ext import commands, tasks

gameName  = "가상코인"
coinList  = ["도지코인", "냥냥펀치코인", "람쥐썬더코인", "벌크여우코인", "머슬고래코인", "비트코인", "스팀코인", "사과코인", "삼성코인", "페페코인"]
# coinEmoji = [':thuglifedog:', ':jjag2:', '🐿️', '🦊', '🐳', ':coin:', '🎮', '🍎', '🏢', ':Pepegood:']

async def game_createChart(bot, channels):
    chartList = []
    for channel in channels:
        messageList = [message async for message in channel.history()]
        for idx, message in enumerate(messageList):
            if message.author.id == bot.user.id and message.content.endswith('마이나차트```'):
                chartList.append(message)
                del messageList[idx]
                break
        else:
            print(f'봇의 차트메시지가 없습니다.')
            newMessage = await channel.send('차트정보가 없으므로, 새로 생성합니다.')
            chartList.append(newMessage)
        
        # chartMessage 이외에 전부 삭제하기
        for message in messageList:
            await message.delete()
    
    return chartList

async def changeBitCoin(guild, coin):
    now = datetime.datetime.now()
    for c in coin:
        if c[2] == 1: #폐지여부
            con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
            cur = con.cursor()
            
            moneyType = 0
            if c[6] == 0:
                rand = random.randint(0,99)
                if rand < 40:
                    moneyType = 1
            else:
                rand = random.randint(0,99)
                if rand < 60:
                    moneyType = 1
            moneyRange = int(c[4]*(random.randint(0, int(c[3]*100))/1000))
            moneyPower = random.randint(0,99)
            if moneyPower < 5:
                moneyRange = int(moneyRange*1.5)
            prePrice = c[4]
            cur.execute("UPDATE 'Coin_Info' SET coin_Updown = ? WHERE coin_ID = ?", (moneyType, c[0]))
            if moneyType == 0:
                if prePrice > moneyRange:
                    curPrice = prePrice-moneyRange
                else:
                    curPrice = 0
            else:
                if prePrice < 200:
                    rand = random.randint(0,99)
                    if rand < 5: #상장폐지 극복
                        moneyRange += random.randint(100,200)
                if prePrice+moneyRange < 100000:
                    curPrice = prePrice+moneyRange
                else:
                    curPrice = 100000
            if curPrice <= 50:
                exitN = c[9]+1
                if exitN >= 10:
                    nowDatetime = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
                    cur.execute("UPDATE 'Coin_Info' SET coin_Open = 0, coin_DeleteDate = ? WHERE coin_ID = ?", (nowDatetime, c[0]))
                    cur.execute("SELECT trade_UserName, trade_CoinNum, trade_CoinCost FROM Coin_Trade WHERE trade_CoinID = ?", (c[0],))
                    lostCoin = cur.fetchall()
                    cur.execute("DELETE FROM 'Coin_Trade' WHERE trade_CoinID = ?", (c[0],))
                    embed = discord.Embed(title = f':x: {c[1]} 상장폐지', description = f"{c[1]}이 결국 상장폐지되었습니다.", color = 0xffc0cb)
                    lostSumMoney = 0
                    for lc in lostCoin:
                        lostSumMoney += lc[2]
                        embed.add_field(name = f'- {lc[0]}님', value = f'허공으로 증발한 `{lc[1]}코인`')
                    embed.set_footer(text = f"총 {fun.printN(lostSumMoney)}원 규모의 돈이 사라졌습니다. | {gameName}")
                    for channel in fun.getBotChannelGuild(guild):
                        await channel.send(embed = embed)
                else:
                    cur.execute("UPDATE 'Coin_Info' SET coin_Exit = ? WHERE coin_ID = ?", (exitN, c[0]))
            else:
                cur.execute("UPDATE 'Coin_Info' SET coin_Exit = ? WHERE coin_ID = ?", (0, c[0]))
            cur.execute("UPDATE 'Coin_Info' SET coin_Price1 = ?, coin_Price2 = ? WHERE coin_ID = ?", (curPrice, prePrice, c[0]))
            con.close() #db 종료

        else: #폐지됨
            exittime = datetime.datetime.strptime(c[8], '%Y-%m-%d %H:%M:%S')
            if(now - exittime).seconds > 60:
                con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                cur = con.cursor()
                cur.execute("SELECT coin_Name FROM Coin_NameList")
                allCoinName = list(map(list, cur.fetchall()))
                # 코인이름을 무작위로 가져오기
                coinName = ''
                coinNameList = coinList
                for name in allCoinName:
                    coinNameList.append(name[0])
                while(True):
                    rand = random.randint(0,len(coinNameList)-1)
                    nonPass = 0
                    cur.execute("SELECT coin_Name FROM Coin_Info")
                    nameList = cur.fetchall()
                    for i in nameList:
                        if i[0] == coinNameList[rand]:
                            nonPass = 1
                            break
                    if nonPass == 0:
                        coinName = coinNameList[rand]
                        break
                coinRange = random.randint(110,250)/100
                coinPrice = random.randint(200,2000)
                nowDatetime = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
                cur.execute("UPDATE 'Coin_Info' SET coin_Name = ?, coin_Open = ?, coin_Range = ?, coin_Price1 = ?, coin_Price2 = ?, coin_Updown = ?, coin_CreateDate = ?, coin_DeleteDate = ?, coin_Exit = ? WHERE coin_ID = ?", (coinName, 1, coinRange, coinPrice, coinPrice, 1, nowDatetime, '', 0, c[0]))
                embed = discord.Embed(title = f':receipt: {coinName} 등장', description = f"새롭게 {coinName}이 거래소에 올라왔습니다!\n이 친구는 시작거래가가 {fun.printN(coinPrice)}원이군요.", color = 0xffc0cb)
                for channel in fun.getBotChannelGuild(guild):
                    await channel.send(embed = embed)
                con.close() #db 종료

async def bitcoinSystem(bot, guild, channels): # channel은 리스트형태임
    message = await game_createChart(bot, channels) # message도 리스트형태로 반환됨
    con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
    cur = con.cursor()
    cur.execute("SELECT coin_ID, coin_Name, coin_Open, coin_Range, coin_Price1, coin_Price2, coin_Updown, coin_CreateDate, coin_DeleteDate, coin_Exit FROM Coin_Info")
    coin = cur.fetchall()
    con.close() #db 종료

    # 비트코인 가격 변동
    await changeBitCoin(guild, coin)

    con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
    cur = con.cursor()
    cur.execute("SELECT coin_ID, coin_Name, coin_Open, coin_Range, coin_Price1, coin_Price2, coin_Updown, coin_CreateDate, coin_DeleteDate, coin_Exit FROM Coin_Info")
    coin = cur.fetchall()
    con.close() #db 종료

    now = datetime.datetime.now()
    nowDatetime = "{}년 {:02d}월 {:02d}일 {:02d}시 {:02d}분".format(now.year, now.month, now.day, now.hour, now.minute)
    coinNum = len(coin)
    chartText = "```diff\n  종목             현재가격         변동폭\n"
    chartText += "─────────────────────────────────────────\n"
    for c in coin:
        # chartText += "-----------------------------------------\n"
        if c[2] == 1:
            if c[4] > c[5]:
                chartText += "+ "
            elif c[4] < c[5]:
                chartText += "- "
            else:
                chartText += "# "
        else:
            chartText += "$ "
        space1 = 9-len(c[1])
        chartText += c[1]
        chartText += "  "*space1
        if c[2] == 1:
            space2 = 14-len(str(c[4]))
            chartText += str(c[4]) + "원"
            chartText += " "*space2
        else:
            space2 = 8-len("상장폐지됨")
            chartText += "상장폐지됨 "
            chartText += "  "*space2
        
        if c[2] == 1:
            updown = abs(c[4]-c[5])
            if c[4] > c[5]:
                chartText += str(updown) + "▲\n"
            elif c[4] < c[5]:
                chartText += str(updown) + "▼\n"
            else:
                chartText += str(updown) + "#\n"
        else:
            chartText += "0#\n"
        #print(c[0], c[1], c[2], c[3], c[4])
    chartText += "─────────────────────────────────────────\n"
    chartText += f'  LastUpdate {nowDatetime}\n+ 마이나차트```'
    for msg in message:
        await msg.edit(content=chartText)


class BitcoinGame(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.run.start()
    
    def cog_unload(self):
        self.run.cancel()

    @tasks.loop(seconds=60)
    async def run(self):
        if fun.guildsList != []:
            guilds = fun.getChartChannel()
            for guild in guilds:
                await bitcoinSystem(self.bot, guild, guilds[guild])

    @commands.command()
    async def 코인(self, ctx, *input):
        if(ctx.channel.id in fun.getBotChannel(ctx)):
            # try:
            id = ctx.author.id
            check = fun.game_check(id)
            if check == 0:
                embed = discord.Embed(title = f':exclamation: {gameName} 미가입', description = f'{ctx.author.mention} {gameName} 게임에 가입하셔야 이용이 가능합니다. (!회원가입)', color = 0xff0000)
                embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                await ctx.channel.send(embed = embed)
                return 0

            fun.setUserName(id, ctx)

            if(input[0] == '도움말'):
                embed = discord.Embed(title = f':video_game: {gameName} 도움말', description = f'{ctx.author.mention} {gameName} 게임의 명령어입니다!', color = 0xffc0cb)
                # embed.add_field(name = f'!코인  지원금', value = f'하루에 한번 지원금으로 3000원을 드립니다!')
                # embed.add_field(name = f'!코인  내정보', value = f'보유한 재산이나 랭킹 순위를 볼 수 있어요.')
                embed.add_field(name = f'!코인  보유', value = f'내가 소유한 코인들의 현황을 볼 수 있어요.')
                embed.add_field(name = f'!코인  보유  `코인명`', value = f'해당 코인을 보유하고 있는 유저들을 볼 수 있어요.')
                embed.add_field(name = f'!코인  [매수│매도]  `코인명`  [`수량`│`퍼센트%`]', value = f'코인을 사고 팔 수 있습니다!\n퍼센트단위로 구매할 수도 있어요.')
                embed.add_field(name = f'!코인  [풀매수│풀매도]  `코인명`', value = f'귀찮게 하나씩 언제 처리하나요. 인생은 한방!')
                # embed.add_field(name = f'!코인  순위', value = f'코인게임을 플레이하고 있는 유저들의 순위를 볼 수 있어요.')
                # embed.add_field(name = f'!코인  송금  `@유저명`  `금액`', value = f'다른 유저에게 돈을 보낼 수 있어요. **수수료 10%**')
                embed.add_field(name = f'!코인  추천', value = f'추천까지만 쓰면, 내가 등록한 코인이름을 확인할 수 있어요.')
                embed.add_field(name = f'!코인  추천  `코인명`', value = f'직접 코인이름을 추천해주면, 해당 코인이 차트에서 등장할 수 있어요.')
                embed.add_field(name = f'!코인  추천삭제', value = f'내가 등록한 코인들을 전부 삭제해요.')
                embed.add_field(name = f'!코인  추천삭제 `코인명`', value = f'내가 등록한 특정코인을 삭제해요.')
                embed.add_field(name = f'꿀팁', value = f'코인이름을 쓸 땐, "코인"을 뺀 이름만 써도 되요.\n**ex.사과코인 == 사과**')
                embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                await ctx.channel.send(embed = embed)
            elif(input[0] == '추천'):
                con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                cur = con.cursor()
                cur.execute("SELECT coin_Name, coin_Date FROM Coin_NameList WHERE user_ID = ?", (id,))
                coinNameInfo = cur.fetchall()
                cur.execute("SELECT coin_Name FROM Coin_NameList")
                allCoinName = list(map(list, cur.fetchall()))
                con.close() #db 종료

                if len(input) == 1:
                    embed = discord.Embed(title = f':x: {gameName} 이름추천', description = f'{ctx.author.mention} 님이 등록하신 코인명 리스트입니다.', color = 0xffc0cb)
                    for name, date in coinNameInfo:
                        embed.add_field(name = f'{name}', value = f'{date}')
                    embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                    await ctx.channel.send(embed = embed)
                    return True

                # 추천한 코인 이름 갯수가 6개인 경우
                if len(coinNameInfo) >= 6:
                    embed = discord.Embed(title = f':x: {gameName} 이름추천', description = f'{ctx.author.mention} 코인 이름은 개인당 최대 6개까지 추천할 수 있습니다.', color = 0xffc0cb)
                    for name, date in coinNameInfo:
                        embed.add_field(name = f'{name}', value = f'{date}')
                    embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                    await ctx.channel.send(embed = embed)
                else:
                    _coinName = input[1]
                    if _coinName[-2:] == '코인':
                        _coinName = _coinName[:-2]
                    
                    pre = re.compile('[^가-힣]+')
                    NoText = pre.findall(_coinName)
                    _coinName = f'{_coinName}코인'
                    if NoText != []:
                        embed = discord.Embed(title = f':x: {gameName} 이름추천', description = f'{ctx.author.mention} {_coinName}에 불가능한 글자가 포함되어 있습니다.\n**코인이름은 한글만 가능합니다.**', color = 0xffc0cb)
                        for no in NoText:
                            embed.add_field(name = f'{no}', value = f'불가능')
                        embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                        msg = await ctx.channel.send(embed = embed)
                        await msg.delete(delay=10)
                        return False
                    
                    if len(_coinName) < 2:
                        embed = discord.Embed(title = f':x: {gameName} 이름추천', description = f'{ctx.author.mention} {_coinName}은 글자수가 **{len(_coinName)}** 입니다.\n코인이름은 최소 3글자이상 써주셔야 합니다.', color = 0xffc0cb)
                        embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                        msg = await ctx.channel.send(embed = embed)
                        await msg.delete(delay=10)
                        return False

                    if len(_coinName) > 6:
                        embed = discord.Embed(title = f':x: {gameName} 이름추천', description = f'{ctx.author.mention} {_coinName}은 글자수가 **{len(_coinName)}** 입니다.\n코인이름은 최대 6글자까지 가능합니다.', color = 0xffc0cb)
                        embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                        msg = await ctx.channel.send(embed = embed)
                        await msg.delete(delay=10)
                        return False
                    
                    if [_coinName] in allCoinName:
                        embed = discord.Embed(title = f':x: {gameName} 이름추천', description = f'{ctx.author.mention} {_coinName}은 이미 있는 이름입니다.', color = 0xffc0cb)
                        embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                        msg = await ctx.channel.send(embed = embed)
                        await msg.delete(delay=10)
                        return False
                    
                    now = datetime.datetime.now()
                    nowDatetime = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
                    con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                    cur = con.cursor()
                    cur.execute("INSERT INTO Coin_NameList VALUES(?, ?, ?, ?)", (id, ctx.author.display_name, _coinName, nowDatetime))
                    con.close() #db 종료
                    coinNameInfo.append((_coinName, nowDatetime))
                    embed = discord.Embed(title = f':x: {gameName} 이름추천', description = f'{ctx.author.mention} {_coinName}이 데이터베이스에 등록됩니다.\n내가 등록한 단어는 총 {len(coinNameInfo)}개 입니다. (최대 6개까지 가능)', color = 0xffc0cb)
                    for name, date in coinNameInfo:
                        embed.add_field(name = f'{name}', value = f'{date}')
                    embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                    await ctx.channel.send(embed = embed)
            
            elif(input[0] == '추천삭제'):
                con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                cur = con.cursor()
                cur.execute("SELECT coin_Name, coin_Date FROM Coin_NameList WHERE user_ID = ?", (id,))
                coinNameInfo = cur.fetchall()
                con.close() #db 종료

                # 전부 삭제
                if(len(input) == 1):
                    con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                    cur = con.cursor()
                    cur.execute("DELETE FROM 'Coin_NameList' WHERE user_ID = ?", (id,))
                    con.close() #db 종료
                    embed = discord.Embed(title = f':x: {gameName} 추천삭제', description = f'{ctx.author.mention} 님이 등록하신 코인을 전부 삭제했습니다.', color = 0xffc0cb)
                    for name, date in coinNameInfo:
                        embed.add_field(name = f'{name}', value = f'{date}')
                    embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                    await ctx.channel.send(embed = embed)
                    return True
                
                _coinName = input[1]
                if _coinName[-2:] != '코인':
                    _coinName = f'{_coinName}코인'
                
                con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                cur = con.cursor()
                cur.execute("SELECT coin_Name FROM Coin_NameList WHERE user_ID = ? AND coin_Name = ?", (id, _coinName))
                userCoinName = cur.fetchone()
                con.close() #db 종료

                if userCoinName == []:
                    embed = discord.Embed(title = f':x: {gameName} 추천삭제', description = f'{ctx.author.mention} 님, {_coinName}이라는 코인은 등록된 기록이 없습니다.\n**!코인 추천** 을 입력해서 등록한 코인들을 확인해보세요.', color = 0xffc0cb)
                    embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                    await ctx.channel.send(embed = embed)
                    return False
                
                con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                cur = con.cursor()
                cur.execute("DELETE FROM 'Coin_NameList' WHERE user_ID = ? AND coin_Name = ?", (id, _coinName))
                con.close() #db 종료

                embed = discord.Embed(title = f':x: {gameName} 추천삭제', description = f'{ctx.author.mention} {_coinName}을 삭제했습니다.\n차트에 이미 존재하는 코인인 경우, 상폐될 때까지 남아있습니다.', color = 0xffc0cb)
                embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                await ctx.channel.send(embed = embed)
                return False

            elif(input[0] == '보유' and len(input) == 1):
                con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                cur = con.cursor()
                cur.execute("SELECT trade_CoinID, trade_CoinName, trade_CoinNum, trade_CoinCost FROM Coin_Trade WHERE trade_UserID = ?", (id,))
                ownCoin = cur.fetchall()
                cur.execute("SELECT coin_ID, coin_Name, coin_Open, coin_Price1 FROM Coin_Info")
                coin = cur.fetchall()
                cur.execute("SELECT user_Name, user_Money FROM User_Info WHERE user_ID = ?", (id,))
                userInfo = cur.fetchone()
                con.close() #db 종료
                if not ownCoin:
                    embed = discord.Embed(title = f':exclamation: {ctx.author.display_name}님의 코인현황', description = f'{ctx.author.mention} 거래내역이 없습니다.\n**!코인 [매수│매도] [코인명] [수량│퍼센트%]**을 통해, 코인을 매수해보세요.', color = 0xffc0cb)
                    embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                    await ctx.channel.send(embed = embed)
                    return 0
                else:
                    embed = discord.Embed(title = f'{ctx.author.display_name}님의 코인현황', description = '보유 중인 코인들과 수익률을 보여줍니다.', color = 0xffc0cb)
                    embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                    #moneyPM, costMoney, currentValue = game_coinValue(id)
                    costMoney = 0
                    currentValue = 0
                    moneyPM = '+'
                    moneyPercent = 0
                    # 보유중인 코인을 표시하기
                    for own in ownCoin:
                        perPM, perCostMoney, perCurrentValue = fun.game_perCoinValue(id, own[0])
                        perMoneyPM = ['-', '+']
                        perMoneyPercent = 0
                        if perPM:
                            perMoneyPercent = round(((perCurrentValue-perCostMoney)/perCostMoney)*100, 2)
                        else:
                            perMoneyPercent = round(((perCostMoney-perCurrentValue)/perCostMoney)*100, 2)
                        costMoney += own[3] #구매비용 합
                        coinValue = 0
                        for c in coin:
                            if c[0] == own[0]:
                                coinValue = c[3]*own[2]
                                currentValue += coinValue
                                break
                        embed.add_field(name = f'{own[1]}', value = f'{own[2]}개 보유\n`{fun.printN(coinValue)}원` `({perMoneyPM[perPM]}{perMoneyPercent}%)`')
                    
                    if currentValue < costMoney:
                        moneyPM = '-'
                        moneyPercent = round(((costMoney-currentValue)/costMoney)*100, 2)
                    else:
                        moneyPercent = round(((currentValue-costMoney)/costMoney)*100, 2)
                    embed.add_field(name = f'코인재산', value = f'{fun.printN(currentValue)}원 `{moneyPM}{moneyPercent}%`')
                    embed.add_field(name = f'보유재산', value = f'{fun.printN(userInfo[1])}원')
                    await ctx.channel.send(embed = embed)
            else:
                con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                cur = con.cursor()
                cur.execute("SELECT coin_ID, coin_Name, coin_Open, coin_Price1, coin_Price2 FROM Coin_Info")
                coin = cur.fetchall()
                cur.execute("SELECT user_Name, user_Money FROM User_Info WHERE user_ID = ?", (id,))
                userInfo = cur.fetchone() #내정보
                con.close() #db 종료

                input_length = len(input)
                for c in coin:
                    if((input[1] == c[1] or input[1] == c[1][:-2]) and c[2] == 1): #c[2]는 활성화된 코인인지 판별여부
                        user_Money = userInfo[1]
                        if(input[0] == '매수'):
                            num = 0
                            if(input[2][-1] == '%'):
                                num = ((userInfo[1]//c[3])*int(input[2][0:-1])) // 100
                            else:
                                num = int(input[2])
                            coinCost = c[3]*num
                            if(num > 0 and user_Money > coinCost):
                                con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                                cur = con.cursor()
                                user_Money = user_Money - coinCost
                                cur.execute("UPDATE 'User_Info' SET user_Money = ? WHERE user_ID = ?", (user_Money, id))
                                cur.execute("SELECT trade_CoinNum, trade_CoinCost FROM Coin_Trade WHERE trade_UserID = ? AND trade_CoinID = ?", (id, c[0]))
                                ownCoin = cur.fetchone()
                                ownCoinN = 0
                                now = datetime.datetime.now()
                                nowDatetime = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
                                if not ownCoin:
                                    ownCoinN = num
                                    cur.execute("INSERT INTO Coin_Trade VALUES(?, ?, ?, ?, ?, ?, ?)", (id, c[0], ctx.author.display_name, c[1], num, coinCost, nowDatetime))
                                else:
                                    ownCoinN = ownCoin[0]+num
                                    cur.execute("UPDATE 'Coin_Trade' SET trade_CoinNum = ?, trade_CoinCost = ?, trade_Date = ? WHERE trade_UserID = ? AND trade_CoinID = ?", (ownCoinN, coinCost+ownCoin[1], nowDatetime, id, c[0]))
                                con.close() #db 종료
                                embed = discord.Embed(title = f'{c[1]} 매수', description = f"코인가격 `{fun.printN(c[3])}원`│`{num}개` 구매│`총 {ownCoinN}코인` 보유│잔액 `{fun.printN(user_Money)}원`", color = 0xffc0cb)
                                embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                                await ctx.channel.send(embed = embed)
                            else:
                                embed = discord.Embed(title = f'{c[1]} 매수실패', description = f'{c[1]}을 {num}개를 매수하는데 필요한 돈이 부족합니다.\n부족한 금액 : {fun.printN(coinCost-user_Money)}원', color = 0xff0000)
                                embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                                await ctx.channel.send(embed = embed)
                        elif(input[0] == '풀매수'):
                            num = user_Money // c[3]
                            coinCost = num*c[3]
                            if(num > 0):
                                con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                                cur = con.cursor()
                                user_Money = user_Money - coinCost
                                cur.execute("UPDATE 'User_Info' SET user_Money = ? WHERE user_ID = ?", (user_Money, id))
                                cur.execute("SELECT trade_CoinNum, trade_CoinCost FROM Coin_Trade WHERE trade_UserID = ? AND trade_CoinID = ?", (id, c[0]))
                                ownCoin = cur.fetchone()
                                ownCoinN = 0
                                now = datetime.datetime.now()
                                nowDatetime = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
                                if not ownCoin:
                                    ownCoinN = num
                                    cur.execute("INSERT INTO Coin_Trade VALUES(?, ?, ?, ?, ?, ?, ?)", (id, c[0], ctx.author.display_name, c[1], num, coinCost, nowDatetime))
                                else:
                                    ownCoinN = ownCoin[0]+num
                                    cur.execute("UPDATE 'Coin_Trade' SET trade_CoinNum = ?, trade_CoinCost = ?, trade_Date = ? WHERE trade_UserID = ? AND trade_CoinID = ?", (ownCoinN, coinCost+ownCoin[1], nowDatetime, id, c[0]))
                                con.close() #db 종료
                                embed = discord.Embed(title = f'{c[1]} 풀매수', description = f"코인가격 `{fun.printN(c[3])}원`│`{num}개` 구매│`총 {ownCoinN}코인` 보유│잔액 `{fun.printN(user_Money)}원`", color = 0xffc0cb)
                                embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                                await ctx.channel.send(embed = embed)
                        elif(input[0] == '매도'):
                            con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                            cur = con.cursor()
                            cur.execute("SELECT trade_CoinNum, trade_CoinCost, trade_Date FROM Coin_Trade WHERE trade_UserID = ? AND trade_CoinID = ?", (id, c[0]))
                            tradeLog = cur.fetchone()
                            con.close() #db 종료
                            if not tradeLog:
                                embed = discord.Embed(title = f'{c[1]} 매도실패', description = f'해당 코인을 구입한 기록이 없습니다.', color = 0xff0000)
                                embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                                await ctx.channel.send(embed = embed)
                                return False
                            coinNum = int(tradeLog[0])
                            # now = datetime.datetime.now()
                            # lastDate = datetime.datetime.strptime(tradeLog[2], '%Y-%m-%d %H:%M:%S')
                            # if (now - lastDate).seconds > 60*60*2:
                            con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                            cur = con.cursor()
                            num = 0
                            if(input[2][-1] == '%'):
                                num = (coinNum*int(input[2][0:-1])) // 100
                            else:
                                num = int(input[2])
                            if coinNum <= num:
                                num = coinNum
                                cur.execute("DELETE FROM 'Coin_Trade' WHERE trade_UserID = ? AND trade_CoinID = ?", (id, c[0]))
                            else:
                                cur.execute("UPDATE 'Coin_Trade' SET trade_CoinNum = ? WHERE trade_UserID = ? AND trade_CoinID = ?", (coinNum-num, id, c[0]))
                            coinCost = c[3]*num #매도금액
                            user_Money += coinCost #매도금액 추가
                            cur.execute("UPDATE 'User_Info' SET user_Money = ? WHERE user_ID = ?", (user_Money, id))
                            con.close() #db 종료
                            embed = discord.Embed(title = f'{c[1]} 매도', description = f"코인가격 `{fun.printN(c[3])}원`│`{num}개` 판매│`총 {fun.printN(coinCost)}원` 획득│보유재산 `{fun.printN(user_Money)}원`", color = 0xffc0cb)
                            embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                            await ctx.channel.send(embed = embed)
                            # else:
                            #     embed = discord.Embed(title = f'{c[1]} 매도실패', description = f'{c[1]}을 마지막으로 거래한 시각은 {lastDate} 입니다.\n매수한 시점으로부터 2시간 뒤에 매도가 가능합니다.', color = 0xff0000)
                            #     embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                            #     await ctx.channel.send(embed = embed)
                        elif(input[0] == '풀매도'):
                            con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                            cur = con.cursor()
                            cur.execute("SELECT trade_CoinNum, trade_CoinCost, trade_Date FROM Coin_Trade WHERE trade_UserID = ? AND trade_CoinID = ?", (id, c[0]))
                            tradeLog = cur.fetchone()
                            con.close() #db 종료
                            if not tradeLog: #구입기록 없음
                                embed = discord.Embed(title = f'{c[1]} 풀매도실패', description = f'해당 코인을 구입한 기록이 없습니다.', color = 0xff0000)
                                embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                                await ctx.channel.send(embed = embed)
                                return False
                            coinNum = int(tradeLog[0])
                            # now = datetime.datetime.now()
                            # lastDate = datetime.datetime.strptime(tradeLog[2], '%Y-%m-%d %H:%M:%S')
                            # if (now - lastDate).seconds > 60*60*2:
                            con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                            cur = con.cursor()
                            num = coinNum
                            cur.execute("DELETE FROM 'Coin_Trade' WHERE trade_UserID = ? AND trade_CoinID = ?", (id, c[0]))
                            coinCost = c[3]*num #매도금액
                            user_Money += coinCost #매도금액 추가
                            cur.execute("UPDATE 'User_Info' SET user_Money = ? WHERE user_ID = ?", (user_Money, id))
                            con.close() #db 종료
                            embed = discord.Embed(title = f'{c[1]} 풀매도', description = f"코인가격 `{fun.printN(c[3])}원`│`{num}개` 판매│`총 {fun.printN(coinCost)}원` 획득│보유재산 `{fun.printN(user_Money)}원`", color = 0xffc0cb)
                            embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                            await ctx.channel.send(embed = embed)
                            # else:
                            #     embed = discord.Embed(title = f'{c[1]} 풀매도실패', description = f'{c[1]}을 마지막으로 거래한 시각은 {lastDate} 입니다.\n매수한 시점으로부터 2시간 뒤에 매도가 가능합니다.', color = 0xff0000)
                            #     embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                            #     await ctx.channel.send(embed = embed)
                        elif(input[0] == '보유'):
                            con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                            cur = con.cursor()
                            # cur.execute("SELECT trade_UserID FROM Coin_Trade WHERE trade_CoinID = ?", (c[0],))
                            cur.execute("SELECT trade_UserID, trade_CoinID, trade_CoinName, trade_CoinNum, trade_CoinCost FROM Coin_Trade WHERE trade_CoinID = ?", (c[0],))
                            allCoin = cur.fetchall() #모든 유저의 해당코인 거래내역
                            con.close() #db 종료
                            if not allCoin:
                                embed = discord.Embed(title = f':exclamation: {c[1]} 보유현황', description = f'{ctx.author.mention} 해당 코인을 소유하고 있는 유저가 없습니다.', color = 0xff0000)
                                embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                                await ctx.channel.send(embed = embed)
                                return 0
                            else:
                                embed = discord.Embed(title = f'{c[1]} 보유현황', description = f'유저들이 보유 중인 {c[1]}의 현황을 보여줍니다.', color = 0xffc0cb)
                                embed.set_footer(text = f"{ctx.author.display_name} | {gameName}", icon_url = ctx.author.avatar_url)
                                for pcoin in allCoin:
                                    if pcoin:
                                        PM, costMoney, coinValue = fun.game_perCoinValue(pcoin[0], pcoin[1])
                                        moneyPM = ['-', '+']
                                        moneyPercent = 0
                                        if coinValue < costMoney:
                                            moneyPercent = round(((costMoney-coinValue)/costMoney)*100, 2)
                                        else:
                                            moneyPercent = round(((coinValue-costMoney)/costMoney)*100, 2)
                                        con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                                        cur = con.cursor()
                                        cur.execute("SELECT user_Name, user_Money FROM User_Info WHERE user_ID = ?", (pcoin[0],))
                                        pUser = cur.fetchone()
                                        con.close() #db 종료
                                        embed.add_field(name = f'{pUser[0]}', value = f'{pcoin[3]}개 보유\n`{fun.printN(coinValue)}원` (`{moneyPM[PM]}{moneyPercent}%)`')
                                await ctx.channel.send(embed = embed)
                        return 0
            # except BaseException as e:
            #     print(f'코인게임 {e}')
            #     pass

def setup(bot):
    bot.add_cog(BitcoinGame(bot))