import sqlite3
from collections import defaultdict

guildsList = []

def printN(num): #자리수에 콤마 넣어주는 함수
    return '{0:,}'.format(num)

def game_check(id):
    alr_exist = []
    con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
    cur = con.cursor()
    cur.execute("SELECT user_ID FROM User_Info WHERE user_ID = ?", (id,))
    rows = cur.fetchall()
    con.close() #db 종료
    for i in rows :
        alr_exist.append(i[0])
    if id not in alr_exist :
        return False
    elif id in alr_exist :
        return True

# DB에 저장된 닉네임이 현재닉네임과 일치하지 않을 때, 닉네임 갱신하기
def setUserName(id, msg):
    con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
    cur = con.cursor()
    cur.execute("SELECT user_Name FROM User_Info WHERE user_ID = ?", (id,))
    userName = cur.fetchone()[0]
    # 저장된 닉네임과 일치하지 않는 경우
    if userName != msg.author.display_name:
        cur.execute("UPDATE 'User_Info' SET user_Name = ?WHERE user_ID = ? ", (msg.author.display_name, id,))
    con.close() #db 종료

def game_getMessageChannel(bot, channel):
    return bot.get_channel(channel)

# def check_Discord(bot):
#     guildList = bot.guilds
#     for server in guildList:
#         if(server.id == 631471244088311840): #내 디코서버일 때
#             return server

# async def check_GuildUser(bot, id):
#     try:
#         server = check_Discord(bot)
#         return await server.fetch_member(id)
#     except:
#         return False

def getBotChannel(message):
    botChannel = []
    channels = message.guild.text_channels
    for ch in channels:
        if ch.topic is not None and '#마이나' in ch.topic:
            botChannel.append(ch.id)
    return botChannel

def getBotChannelGuild(guild):
    botChannel = []
    for ch in guild.text_channels:
        if ch.topic is not None and '#마이나' in ch.topic:
            botChannel.append(ch)
    return botChannel

def getGuilds(bot): #init
    global guildsList
    guildsList = bot.guilds
    print(guildsList)

def getChartChannel():
    chartData = defaultdict(list)
    global guildsList
    for g in guildsList:
        for ch in g.text_channels:
            if ch.topic is not None and '#차트마이나' in ch.topic:
                chartData[g].append(ch)
    return chartData

# 내가 구매한 코인의 가치 표기
def game_coinValue(id):
    con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
    cur = con.cursor()
    cur.execute("SELECT trade_CoinID, trade_CoinName, trade_CoinNum, trade_CoinCost FROM Coin_Trade WHERE trade_UserID = ?", (id,))
    ownCoin = cur.fetchall()
    cur.execute("SELECT coin_ID, coin_Name, coin_Open, coin_Price1 FROM Coin_Info")
    coin = cur.fetchall()
    con.close() #db 종료
    costMoney = 0       # 코인을 구매할 때 사용한 돈
    currentValue = 0    # 현재 코인의 가치
    PM = True           # 구입한 코인의 가치가 마이너스인지 플러스인지
    for own in ownCoin:
        costMoney += own[3] #구매비용 합
        coinValue = 0
        for c in coin:
            if c[0] == own[0]:
                coinValue = c[3]*own[2]
                currentValue += coinValue
                break
    # 결국 내가 구매한 코인의 가치가 비용보다 낮은 경우
    if currentValue < costMoney:
        PM = False
    return PM, costMoney, currentValue

def game_perCoinValue(id, coinId):
    con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
    cur = con.cursor()
    cur.execute("SELECT trade_CoinID, trade_CoinName, trade_CoinNum, trade_CoinCost FROM Coin_Trade WHERE trade_UserID = ? AND trade_CoinID = ?", (id, coinId,))
    ownCoin = cur.fetchone()
    cur.execute("SELECT coin_ID, coin_Name, coin_Open, coin_Price1 FROM Coin_Info WHERE coin_ID = ?", (coinId,))
    coinInfo = cur.fetchone()
    con.close() #db 종료
    # 해당 코인 데이터가 아무것도 없는 경우
    if not ownCoin:
        return 0, 0, 0
    costMoney   = ownCoin[3]
    coinValue   = coinInfo[3]*ownCoin[2]
    PM          = True
    if coinValue < costMoney: PM = False
    return PM, costMoney, coinValue

# 코인게임 랭킹 계산
def coin_Ranking(set_):
    con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
    cur = con.cursor()
    cur.execute("SELECT user_ID, user_Name, user_Money FROM User_Info")
    userList = cur.fetchall()
    con.close() #db 종료
    userRanking = {}
    userNumber = len(userList)
    # 유저리스트를 순회하기
    for user in userList:
        _Name = user[0]
        # set_ 인자가 1인 경우, _Name에는 user_Name 넣기
        if set_ == 1: _Name = user[1]
        # 해당 유저의 재산 현황 가져오기
        PM,constMmoney,currentValue = game_coinValue(user[0])
        # 코인재산과 현금 재산 합치기
        _Value = currentValue+user[2]
        userRanking[_Name] = _Value
    userRanking = sorted(userRanking.items(), reverse=True, key=lambda x:x[1])
    return userRanking, userNumber

# id값의 랭킹 순위
def coin_GetRank(id):
    userRanking, userNumber = coin_Ranking(0)
    rankIndex = 0
    rankSameMoney = 0
    for rank in userRanking:
        if rankSameMoney != rank[1]:
            rankIndex += 1
        rankSameMoney = rank[1]
        if id == rank[0]:
            return rankIndex, userNumber
    return False, False