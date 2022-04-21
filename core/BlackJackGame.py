import sqlite3, discord, asyncio, random
import data.Functions as fun
from discord.ext import commands, tasks

gameName4   = "블랙잭"
maxCard     = 4*13

cardNumber  = [
    '<:2_:964842141941649428>', '<:3_:964842141547380796>', '<:4_:964842141589311488>', '<:5_:964842141539008512>', '<:6_:964842141576724480>', '<:7_:964842141681602590>', '<:8_:964842141564170250>', '<:9_:964842141572546631>','<:10_:964863595580129280>', '<:kk:964851928087552040>', '<:jj:964851928154652692>', '<:qq:964851928188223538>', '<:aa:964864677748297819>'
]
cardPattern = ['<:cs:964844492303785994>', ':heart:', '<:ch:964846055248252979>', '<:cc:964844492345720892>']
cardValue   = [2,3,4,5,6,7,8,9,10,10,10,10,11]

blackJackPlay   = 0
blackJackJoin   = []
blackJackUser   = []

def newShuffledDeck(cardDeck):
    global maxCard
    for i in range(maxCard):
        cardDeck.append(i)

    for i in range(maxCard-1):
        rand = random.randint(i, maxCard-1)
        temp = cardDeck[i]
        cardDeck[i] = cardDeck[rand]
        cardDeck[rand] = temp

def printCard(card):
    global cardPattern, cardNumber
    cardNum = card % 13
    cardPat = card // 13
    return cardPattern[cardPat], cardNumber[cardNum]

def printCardList(cardList, show):
    patList = []
    numList = []
    for card in cardList:
        pat, num = printCard(card)
        patList.append(pat)
        numList.append(num)
    
    if show is False:
        patList[-1] = '❔'
        numList[-1] = '❔'
    
    return "  ".join(patList) + "\n" + "  ".join(numList)

def printCardValue(cardList, show):
    global cardValue
    score = []
    for card in cardList:
        cardNum = card % 13
        score.append(cardValue[cardNum])
    
    if show is False:
        score.pop()
    
    while sum(score) > 21:
        if 11 not in score: break
        for i in range(len(score)):
            if score[i] == 11:
                score[i] = 1
                break
    
    return sum(score)

def drawCard(cardDeck):
    card = cardDeck.pop()
    if cardDeck == []: newShuffledDeck(cardDeck)
    return card
    
async def addReaction(msg):
    await msg.add_reaction('▶️')
    await msg.add_reaction('⏹️')

class BlackJackGame(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def 블랙잭(self, ctx, *input):
        if(ctx.channel.id in fun.getBotChannel(ctx)):
            try:
                id = ctx.author.id
                if fun.game_check(id) is False: # 회원가입이 된 유저인지 체크
                    embed = discord.Embed(title = f':exclamation: {gameName4} 미가입', description = f'{ctx.author.mention} {gameName4} 게임에 가입하셔야 이용이 가능합니다. (!회원가입)', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.author.display_name} | {gameName4}", icon_url = ctx.author.avatar_url)
                    await ctx.channel.send(embed = embed)
                    return 0
                fun.setUserName(id, ctx)

                if input[0] == '도움말':
                    embed = discord.Embed(title = f':black_joker: {gameName4} 도움말', description = f'', color = 0x827397)
                    embed.set_footer(text = f"{ctx.author.display_name} | {gameName4}", icon_url = ctx.author.avatar_url)
                    embed.add_field(name=f'!블랙잭  [배팅금액]  [타이머]', value=f'타이머는 처음 명령어를 실행하는 유저만 사용하시면 됩니다.')
                    embed.add_field(name=f'블랙잭 룰', value=f'카드의 합이 21이하이고, 딜러보다 높을 때 승리합니다.')
                    embed.add_field(name=f'▶️ 버튼', value=f'카드를 추가로 더 받습니다.')
                    embed.add_field(name=f'⏹️ 버튼', value=f'카드를 그만 받고 턴을 넘깁니다.')
                    await ctx.channel.send(embed = embed)
                    return 0
                
                betting = 0
                try: betting = int(input[0])
                except: # 입력한 값이 숫자가 아닐 때
                    embed = discord.Embed(title = f':exclamation: {gameName4} 오류', description = f'{ctx.author.mention} 배팅하실 금액을 입력하셔야 합니다.\n!블랙잭 [배팅금액]', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.author.display_name} | {gameName4}", icon_url = ctx.author.avatar_url)
                    await ctx.channel.send(embed = embed)
                    return 0
                
                con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                cur = con.cursor()
                cur.execute("SELECT user_Money FROM User_Info WHERE user_ID = ?", (id,))
                myMoney = cur.fetchone()[0]
                con.close() #db 종료

                global blackJackPlay, blackJackJoin, blackJackUser

                if blackJackPlay == 2:
                    embed = discord.Embed(title = f':exclamation: {gameName4} 참가불가', description = f'{ctx.author.mention} 게임이 시작했어요..', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.author.display_name} | {gameName4}", icon_url = ctx.author.avatar_url)
                    await ctx.channel.send(embed = embed)
                    return 0

                if myMoney < betting: # 보유한 돈이 부족할때
                    embed = discord.Embed(title = f':exclamation: {gameName4} 금액부족', description = f'{ctx.author.mention} 보유하고 계시는 돈이 부족합니다.\n보유재산 `{fun.printN(myMoney)}원` :money_with_wings:', color = 0xff0000)
                    embed.set_footer(text = f"{ctx.author.display_name} | {gameName4}", icon_url = ctx.author.avatar_url)
                    await ctx.channel.send(embed = embed)
                    return 0


                if blackJackPlay == 1:
                    if id not in blackJackJoin:
                        myMoney -= betting
                        con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                        cur = con.cursor()
                        cur.execute("UPDATE 'User_Info' SET user_Money = ? WHERE user_ID = ?", (myMoney, id))
                        con.close() #db 종료

                        blackJackJoin.append(id)
                        blackJackUser.append([ctx.author.display_name, betting, ctx.author])
                        await ctx.delete(delay=1)
                    else:
                        author = await ctx.author.create_dm()
                        await author.send("이미 블랙잭게임에 참여하신 상태입니다.")
                        await ctx.delete(delay=1)
                
                elif blackJackPlay == 0:
                    
                    timer = 10
                    try: timer = int(input[1])
                    except: pass# 입력한 값이 숫자가 아닐 때

                    myMoney -= betting
                    con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                    cur = con.cursor()
                    cur.execute("UPDATE 'User_Info' SET user_Money = ? WHERE user_ID = ?", (myMoney, id))
                    con.close() #db 종료

                    blackJackPlay = 1
                    blackJackJoin.append(id)
                    blackJackUser.append([ctx.author.display_name, betting, ctx.author])

                    embed = discord.Embed(title = f':black_joker: 블랙잭 참여인원({len(blackJackJoin)}명)', description = f'{timer}초 후 블랙잭이 시작됩니다.\n바로 게임을 시작하시려면, ▶️ 반응을 눌러주세요.', color = 0x827397)
                    embed.set_footer(text = f"방장 {ctx.author.display_name} | {gameName4}", icon_url = ctx.author.avatar_url)
                    embed.add_field(name=f'{ctx.author.display_name}', value=f'배팅금액 : {fun.printN(betting)}원')
                    msg = await ctx.channel.send(embed = embed)
                    await msg.add_reaction('▶️')

                    while timer:
                        embed = discord.Embed(title = f':black_joker: 블랙잭 참여인원({len(blackJackJoin)}명)', description = f'{timer}초 후 블랙잭이 시작됩니다.\n바로 게임을 시작하시려면, ▶️ 반응을 눌러주세요.', color = 0x827397)
                        embed.set_footer(text = f"방장 {ctx.author.display_name} | {gameName4}", icon_url = ctx.author.avatar_url)
                        for user in blackJackUser:
                            embed.add_field(name=f'{user[0]}', value=f'배팅금액 : {fun.printN(user[1])}원')
                        await msg.edit(embed = embed)
                        try:
                            def check(reaction, user):
                                return str(reaction) in ['▶️'] and \
                                user == ctx.author and reaction.message.id == msg.id
                            reaction, user = await self.bot.wait_for('reaction_add', timeout=1.0, check=check)

                            if str(reaction) == '▶️':
                                timer = 0

                        except asyncio.TimeoutError:
                            timer -= 1
                            continue

                    await msg.clear_reactions()


                    # Setting
                    joinNum     = len(blackJackJoin)
                    cardDeck    = []
                    myHands     = [[] for _ in range(joinNum)]
                    dealerHands = []
                    myScore     = [0 for _ in range(joinNum)]
                    stopSign    = [0 for _ in range(joinNum)] # 0진행 1패배 2승리 3버스트 4블랙잭
                    dealerScore = 0
                    wdEmoji     = [0, '💸', '🏆', '☠️', '👑']
                    wdRate      = [0, 0, 1.5, 0, 2]

                    def printCardField(embed, titleText, logText, show):
                        embed = discord.Embed(title = titleText, description = logText, color = 0x827397)
                        embed.set_footer(text = f"방장 {ctx.author.display_name} | {gameName4}", icon_url = ctx.author.avatar_url)

                        for i in range(joinNum):
                            userBetting = blackJackUser[i][1]
                            nameText  = f'{blackJackUser[i][0]}님 ({myScore[i]})'
                            if stopSign[i] > 0: nameText += f' {wdEmoji[stopSign[i]]}'
                            valueText = f'{printCardList(myHands[i], True)}\n'
                            if stopSign[i] > 0: valueText += f'배팅 {fun.printN(userBetting)}원\n결과 {fun.printN(int(userBetting*wdRate[stopSign[i]]))}원\n'
                            else: valueText += f'배팅 {fun.printN(userBetting)}원\n'
                            embed.add_field(name=nameText, value=valueText)
                        
                        index = 1
                        while True:
                            if joinNum <= index*3:
                                index = index*3 - joinNum
                                break
                            index += 1
                        
                        for i in range(index): embed.add_field(name=f'.', value=f'.')
                        embed.add_field(name=f'딜러 카드 ({dealerScore})', value=f'{printCardList(dealerHands, show)}\n.')

                        return embed

                    newShuffledDeck(cardDeck)
                    print(cardDeck)
                    
                    titleText = f':black_joker: 블랙잭 참여인원({joinNum}명)'
                    logText   = f'- 딜러와 유저들의 카드를 분배합니다.'
                    for i in range(joinNum):
                        myHands[i].append(drawCard(cardDeck))
                        myScore[i] = printCardValue(myHands[i], True)
                    dealerHands.append(drawCard(cardDeck))
                    dealerScore = printCardValue(dealerHands, False)
                    embed = printCardField(embed, titleText, logText, False) # 메시지 수정
                    await msg.edit(embed = embed)

                    await asyncio.sleep(1)

                    for i in range(joinNum):
                        myHands[i].append(drawCard(cardDeck))
                        myScore[i] = printCardValue(myHands[i], True)
                    dealerHands.append(drawCard(cardDeck))
                    dealerScore = printCardValue(dealerHands, False)
                    embed = printCardField(embed, titleText, logText, False) # 메시지 수정
                    await msg.edit(embed = embed)

                    # 블랙잭 체크
                    for i in range(joinNum):
                        if myScore[i] == 21:
                            logText += f'\n- {blackJackUser[i][0]}님의 카드합이 {myScore[i]}이므로 블랙잭입니다.'
                            stopSign[i] = 4
                            embed = printCardField(embed, titleText, logText, False) # 메시지 수정
                            await msg.edit(embed = embed)
                            
                    _dealerScore = printCardValue(dealerHands, True)
                    if _dealerScore == 21:
                        logText += f'\n- 딜러의 카드합이 {_dealerScore}이므로 블랙잭입니다.'
                        logText += f'\n- 블랙잭이 아닌 모든 유저는 패배합니다.'
                        for i in range(joinNum):
                            if stopSign[i] == 0:
                                stopSign[i] = 1

                        embed = printCardField(embed, titleText, logText, True) # 메시지 수정
                        await msg.edit(embed = embed)
                    
                    for i in range(joinNum):
                        # 유저의 차례
                        titleText = f':black_joker: 블랙잭 :: {blackJackUser[i][0]}의 차례'
                        embed = printCardField(embed, titleText, logText, False) # 메시지 수정
                        await msg.edit(embed = embed)

                        while stopSign[i] == 0:
                            await addReaction(msg)
                            if myScore[i] > 21:
                                logText += f'\n- {blackJackUser[i][0]}님의 카드합이 {myScore[i]}이므로 버스트입니다.'
                                stopSign[i] = 3
                                embed = printCardField(embed, titleText, logText, False) # 메시지 수정
                                await msg.edit(embed = embed)
                                await msg.clear_reactions()
                                break
                            elif myScore[i] == 21:
                                logText += f'\n- {blackJackUser[i][0]}님의 카드합이 {myScore[i]}이므로 차례를 넘깁니다.'
                                stopSign[i] = 2
                                embed = printCardField(embed, titleText, logText, False) # 메시지 수정
                                await msg.edit(embed = embed)
                                await msg.clear_reactions()
                                break
                            try:
                                def check(reaction, user):
                                    return str(reaction) in ['▶️','⏹️'] and \
                                    user == blackJackUser[i][2] and reaction.message.id == msg.id
                                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)

                                if str(reaction) == '▶️':
                                    await msg.clear_reactions()
                                    myHands[i].append(drawCard(cardDeck))
                                    myScore[i] = printCardValue(myHands[i], True)
                                    embed = printCardField(embed, titleText, logText, False) # 메시지 수정
                                    await msg.edit(embed = embed)
                                    continue

                                elif str(reaction) == '⏹️':
                                    await msg.clear_reactions()
                                    break

                            except asyncio.TimeoutError:
                                await msg.clear_reactions()
                                break
                    

                    # 딜러의 차례
                    titleText = f':black_joker: 블랙잭 :: 딜러의 차례'
                    embed = printCardField(embed, titleText, logText, False) # 메시지 수정
                    await msg.edit(embed = embed)

                    while True:
                        await asyncio.sleep(1)
                        if 0 not in stopSign: break
                        _dealerScore = printCardValue(dealerHands, True)

                        if _dealerScore < 17:
                            dealerHands.append(drawCard(cardDeck))
                            dealerScore = printCardValue(dealerHands, False)
                            embed = printCardField(embed, titleText, logText, False) # 메시지 수정
                            await msg.edit(embed = embed)
                            continue
                        
                        elif _dealerScore == 21:
                            logText += f'\n- 딜러의 카드합이 {_dealerScore}입니다.'
                            for i in range(joinNum):
                                if stopSign[i] == 0:
                                    stopSign[i] = 1
                            dealerScore = printCardValue(dealerHands, True)
                            embed = printCardField(embed, titleText, logText, False) # 메시지 수정
                            await msg.edit(embed = embed)
                            break

                        elif _dealerScore > 21:
                            logText += f'\n- 딜러의 카드합이 {_dealerScore}이므로 버스트입니다.'
                            for i in range(joinNum):
                                if stopSign[i] == 0:
                                    stopSign[i] = 2
                            dealerScore = printCardValue(dealerHands, True)
                            embed = printCardField(embed, titleText, logText, False) # 메시지 수정
                            await msg.edit(embed = embed)
                            break

                        elif _dealerScore >= 17:
                            break
                    
                    await asyncio.sleep(1)
                    titleText = f':black_joker: 블랙잭 :: 게임결과'

                    dealerScore = printCardValue(dealerHands, True)
                    embed = printCardField(embed, titleText, logText, True) # 메시지 수정
                    await msg.edit(embed = embed)

                    for i in range(joinNum):
                        if stopSign[i] == 0:
                            if myScore[i] >= dealerScore:
                                logText += f'\n- {blackJackUser[i][0]}님의 카드합이 딜러보다 높으므로, 승리합니다.'
                                stopSign[i] = 2
                                embed = printCardField(embed, titleText, logText, True) # 메시지 수정
                                await msg.edit(embed = embed)
                            else:
                                logText += f'\n- {blackJackUser[i][0]}님의 카드합이 딜러보다 낮으므로, 패배합니다.'
                                stopSign[i] = 1
                                embed = printCardField(embed, titleText, logText, True) # 메시지 수정
                                await msg.edit(embed = embed)

                    await msg.add_reaction('⏹️')

                    for i in range(joinNum):
                        if stopSign[i] == 2 or stopSign[i] == 4:
                            userBetting = blackJackUser[i][1]
                            con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                            cur = con.cursor()
                            cur.execute("SELECT user_Money FROM User_Info WHERE user_ID = ?", (blackJackJoin[i],))
                            myMoney = cur.fetchone()[0]
                            myMoney += userBetting + int(userBetting*wdRate[stopSign[i]])
                            cur.execute("UPDATE 'User_Info' SET user_Money = ? WHERE user_ID = ?", (myMoney, blackJackJoin[i]))
                            con.close() #db 종료

                            
                    # 초기화
                    blackJackPlay = 0
                    blackJackJoin = []
                    blackJackUser = []
                    return 0

            except BaseException as e:
                print(f'블랙잭게임 {e}')
                pass

def setup(bot):
    bot.add_cog(BlackJackGame(bot))