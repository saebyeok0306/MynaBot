from collections import defaultdict
from enum import Enum

from utils.database.Database import SessionContext
from utils.database.model.authority import Authoritys
from utils.database.model.commands import Commands


def print_(num: int) -> str:
    # 자리수에 콤마 넣어주는 함수
    gold_unit = ["", "만", "억", "조", "경", "해", "자", "양", "가", "구", "간"]
    _num = str(num)[::-1]
    text = ''

    length = len(_num)
    index = 0
    units = 0

    while index < length:
        temp = _num[index:index + 4][::-1]
        unit = gold_unit[units]
        if temp != '0000':
            temp = str(int(temp))
            text = temp + unit + text
        index += 4
        units += 1
    return text


def parse_number(text: str) -> int:
    # 숫자 텍스트를 int 자료형으로 반환
    try:
        num = int(text)
        return num
    except Exception:
        # 숫자 이외에 값이 포함됨
        # 1조3089억2929만2546
        gold_unit = {
            '만': 10000,
            '억': 100000000,
            '조': 1000000000000,
            '경': 10000000000000000,
            '해': 100000000000000000000,
            '자': 1000000000000000000000000,
            '양': 10000000000000000000000000000,
            '가': 100000000000000000000000000000000,
            '구': 1000000000000000000000000000000000000,
            '간': 10000000000000000000000000000000000000000
        }
        length = len(text)
        number = 0
        units = gold_unit['간'] + 1
        index = 0
        _temp = ''
        while index < length:
            uncode = ord(text[index])
            if 48 <= uncode <= 57:
                if len(_temp) == 4: return False
                _temp = _temp + text[index]
            else:
                for u, v in gold_unit.items():
                    if u == text[index]:
                        if v < units:
                            units = v
                            number += v * int(_temp)
                            _temp = ''
                            break
                        else:
                            return False
            index += 1

        if _temp != '':
            number += int(_temp)
        return number


def get_bot_channel(bot, message):
    bot_channel = []
    channels = message.guild.text_channels
    for channel in channels:
        if channel.topic is not None and f'#{bot.user.name}' in channel.topic:
            bot_channel.append(channel.id)
    return bot_channel


def get_bot_channel_guild(bot):
    bot_channel = {}
    for guild in bot.guilds:
        bot_channel[guild] = []
        for channel in guild.text_channels:
            if channel.topic is not None and f'#{bot.user.name}' in channel.topic:
                bot_channel[guild].append(channel)
    return bot_channel


def get_topic_channel(bot, topic):
    data = defaultdict(list)
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.topic is not None and topic in channel.topic:
                data[guild].append(channel)
    return data


def is_test_version():
    import sys
    argv_len = len(sys.argv)

    if argv_len == 1:
        return False

    if "--test" in sys.argv:
        return True

    return False


def is_developer(author):
    if author.id == 383483844218585108:
        return True
    return False


class ROLE_TYPE(Enum):
    GPT4 = "GPT4"
    CLOVAX = "CLOVAX"
    BLACKCAT = "BLACKCAT"
    CHATGPT = "CHATGPT"


class GUILD_COMMAND_TYPE(Enum):
    CHATGPT = "CHATGPT"
    BLACKCAT = "BLACKCAT"


def is_allow_guild(ctx, role: GUILD_COMMAND_TYPE):
    with SessionContext() as session:
        guild_command = session.query(Commands).filter(Commands.guild_id == ctx.guild.id).first()
        if guild_command:
            roles = guild_command.get_roles()
            if role.value in roles:
                return True

    return False


def is_allow_user(ctx, role: ROLE_TYPE):
    if is_developer(ctx.author):
        return True

    with SessionContext() as session:
        authority = session.query(Authoritys).filter(Authoritys.id == ctx.author.id).first()
        if authority:
            roles = authority.get_roles()
            if role.value in roles:
                return True

    return False


def is_allow_channel(bot, ctx):
    if is_developer(ctx.author):
        return True

    if ctx.channel.id in get_bot_channel(bot, ctx):
        return True

    return False
