import sqlite3, datetime
from collections import defaultdict

# 자리수에 콤마 넣어주는 함수
def printN(num:int) -> str:
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

def getBotChannel(bot, message):
    botChannel = []
    channels = message.guild.text_channels
    for channel in channels:
        if channel.topic is not None and f'#{bot.user.name}' in channel.topic:
            botChannel.append(channel.id)
    return botChannel

def getBotChannelGuild(bot):
    botChannel = {}
    for guild in bot.guilds:
        botChannel[guild] = []
        for channel in guild.text_channels:
            if channel.topic is not None and f'#{bot.user.name}' in channel.topic:
                botChannel[guild].append(channel)
    return botChannel

def getTopicChannel(bot, Topic):
    data = defaultdict(list)
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.topic is not None and Topic in channel.topic:
                data[guild].append(channel)
    return data
