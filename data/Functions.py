import sqlite3, datetime
from collections import defaultdict

guildsList = []

def printN(num:int) -> str: #자리수에 콤마 넣어주는 함수
    goldUnit = ["","만","억","조","경","해","자","양","가","구","간"]
    _num = str(num)[::-1]
    text = ''

    length = len(_num)
    index = 0
    units = 0

    while index < length:
        temp = _num[index:index+4][::-1]
        unit = goldUnit[units]
        if temp != '0000':
            temp = str(int(temp))
            text = temp + unit + text
        index += 4
        units += 1
    return text
    # return '{0:,}'.format(num)

# 숫자 텍스트를 int 자료형으로 반환
def returnNumber(text:str) -> int:
    try:
        num = int(text)
        return num
    except:
        # 숫자 이외에 값이 포함됨
        # 1조3089억2929만2546
        goldUnit = {'만':10000,'억':100000000,'조':1000000000000,'경':10000000000000000,'해':100000000000000000000,'자':1000000000000000000000000,'양':10000000000000000000000000000,'가':100000000000000000000000000000000,'구':1000000000000000000000000000000000000,'간':10000000000000000000000000000000000000000}
        length = len(text)
        number = 0
        units = goldUnit['간']+1
        index = 0
        _temp = ''
        while index < length:
            uncode = ord(text[index])
            if 48 <= uncode <= 57:
                if len(_temp) == 4: return False
                _temp = _temp + text[index]
            else:
                for u,v in goldUnit.items():
                    if u == text[index]:
                        if v < units:
                            units = v
                            number += v*int(_temp)
                            _temp = ''
                            break
                        else:
                            return False
            index += 1
            
        if _temp != '':
            number += int(_temp)
        return number    

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

def getBotChannel(bot, message):
    botChannel = []
    channels = message.guild.text_channels
    for ch in channels:
        if ch.topic is not None and f'#{bot.user.name}' in ch.topic:
            botChannel.append(ch.id)
    return botChannel

def getBotChannelGuild(bot, guild):
    botChannel = []
    for ch in guild.text_channels:
        if ch.topic is not None and f'#{bot.user.name}' in ch.topic:
            botChannel.append(ch)
    return botChannel

def getGuilds(bot): #init
    global guildsList
    guildsList = bot.guilds
    print(guildsList)

def getTopicChannel(Topic):
    data = defaultdict(list)
    global guildsList
    for guild in guildsList:
        for ch in guild.text_channels:
            if ch.topic is not None and Topic in ch.topic:
                data[guild].append(ch)
    return data

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
        costMoney += int(own[3]) #구매비용 합
        coinValue = 0
        for c in coin:
            if c[0] == own[0]:
                coinValue = c[3]*int(own[2])
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
    costMoney   = int(ownCoin[3])
    coinValue   = coinInfo[3]*int(ownCoin[2])
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
        _Value = currentValue+int(user[2])
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

def returnJoinDate(id):
    con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
    cur = con.cursor()
    cur.execute("SELECT user_Date FROM User_Info WHERE user_ID = ?", (id,))
    userInfo = cur.fetchone()[0]
    joindate = datetime.datetime.strptime(userInfo, '%Y-%m-%d %H:%M:%S')
    con.close() #db 종료
    return joindate

def removeUserDB(id):
    con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
    cur = con.cursor()
    cur.execute("DELETE FROM 'User_Info' WHERE user_ID = ?", (id,))
    cur.execute("DELETE FROM 'Coin_Trade' WHERE trade_UserID = ?", (id,))
    cur.execute("DELETE FROM 'Coin_NameList' WHERE user_ID = ?", (id,))
    cur.execute("DELETE FROM 'Sword_Info' WHERE sword_UserID = ?", (id,))
    con.close() #db 종료
    return True

def returnRoleName(id):
    con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
    cur = con.cursor()
    cur.execute("SELECT user_Role FROM User_Info WHERE user_ID = ?", (id,))
    userInfo = cur.fetchone()[0]
    con.close() #db 종료
    return userInfo

def createRoleName(id, roleName):
    con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
    cur = con.cursor()
    cur.execute("UPDATE 'User_Info' SET user_Role = ? WHERE user_ID = ?", (roleName, id))
    con.close() #db 종료

async def returnServerRole(guild, user):
    roleName = user.name + '#' + user.discriminator
    RoleList = [ role for role in guild.roles ]
    for role in RoleList:
        if role.name == roleName:
            return role
    return False

async def createUserRole(guild, user):
    roleName = user.name + '#' + user.discriminator
    serverRole = await returnServerRole(guild, user)
    if not serverRole:
        # 서버에 역할이 없는 경우
        position = [ role for role in guild.roles ]
        new_role = await guild.create_role(name=roleName, color=0x99aab5, hoist=False)

        posIdx = len(position)-3 if len(position) > 3 else len(position)
        position.insert(posIdx, new_role)
        position = {role : pos for pos, role in enumerate(position)}
        await guild.edit_role_positions(positions=position)
        await user.add_roles(new_role)
    else:
        # 서버에 있지만, 등록이 안되어있을 수도 있음
        await user.add_roles(serverRole)
    createRoleName(user.id, roleName)
    return True

async def deleteUserRole(guild, user):
    roleName = returnRoleName(user.id)
    if roleName is not None:
        for role in guild.roles:
            if role.name == roleName:
                await role.delete(reason=f'{roleName}님이 회원탈퇴함.')
                return True
    
    return False