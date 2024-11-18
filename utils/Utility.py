import inspect
from collections import defaultdict
from enum import Enum

import discord

from utils.database.Database import SessionContext
from utils.database.model.authority import Authoritys
from utils.database.model.commands import Commands


def print_(num: int) -> str:
    # 자리수에 콤마 넣어주는 함수
    gold_unit = ["", "만", "억", "조", "경", "해", "자", "양", "구", "간", "정", "재", "극"]
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
            '구': 100000000000000000000000000000000,
            '간': 1000000000000000000000000000000000000,
            '정': 10000000000000000000000000000000000000000,
            '재': 100000000000000000000000000000000000000000000,
            '극': 1000000000000000000000000000000000000000000000000
        }
        length = len(text)
        number = 0
        units = gold_unit['극'] + 1
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


def get_bot_channel_interaction(bot, interaction: discord.Interaction):
    bot_channel = []
    channels = interaction.guild.text_channels
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


def current_function_name():
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    caller_name = caller_frame.f_code.co_name
    return caller_name


def is_developer(author):
    if author.id == 383483844218585108:
        return True
    return False


def developer(interaction: discord.Interaction):
    return interaction.user.id == 383483844218585108


def is_server_manager(member: discord.Member):
    if member.guild_permissions.administrator:
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
    MINECRAFT = "MINECRAFT"


def is_allow_guild(ctx, role: GUILD_COMMAND_TYPE):
    with SessionContext() as session:
        guild_command = session.query(Commands).filter(Commands.guild_id == ctx.guild.id).first()
        if guild_command:
            roles = guild_command.get_roles()
            if role.value in roles:
                return True

    return False


def is_allow_guild_interaction(interaction, role: GUILD_COMMAND_TYPE):
    with SessionContext() as session:
        guild_command = session.query(Commands).filter(Commands.guild_id == interaction.guild.id).first()
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


def is_allow_user_interaction(interaction, role: ROLE_TYPE):
    if developer(interaction):
        return True

    with SessionContext() as session:
        authority = session.query(Authoritys).filter(Authoritys.id == interaction.user.id).first()
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


def is_allow_channel_interaction(bot, interaction):
    if developer(interaction):
        return True

    if interaction.channel.id in get_bot_channel_interaction(bot, interaction):
        return True

    return False


async def is_not_allow_channel(ctx, func_name):
    embed = discord.Embed(
        title=f':exclamation: 채널 설정 안내',
        description=f'{ctx.author.mention} 채널명이 `봇명령`이거나 채널주제(topic)에 `#{ctx.bot.user.name}`이 포함된 채널에서만 가능합니다. 없는 경우 해당서버의 관리자에게 부탁하셔야 합니다.',
        color=0xff0000
    )
    embed.set_footer(text=f"{ctx.author.display_name} | {func_name} 명령어", icon_url=ctx.author.display_avatar)
    msg = await ctx.channel.send(embed=embed)
    await msg.delete(delay=10)
    await ctx.message.delete(delay=10)


async def is_not_allow_channel_interaction(bot, interaction, func_name):
    embed = discord.Embed(
        title=f':exclamation: 채널 설정 안내',
        description=f'{interaction.user.mention} 채널명이 `봇명령`이거나 채널주제(topic)에 `#{bot.user.name}`이 포함된 채널에서만 가능합니다. 없는 경우 해당서버의 관리자에게 부탁하셔야 합니다.',
        color=0xff0000
    )
    embed.set_footer(text=f"{interaction.user.display_name} | {func_name} 명령어", icon_url=interaction.user.display_avatar)
    await interaction.followup.send(embed=embed, ephemeral=True)


def merge_type_text(content: list):
    temp = []
    for part in content:
        match part["type"]:
            case "text":
                temp.append(f"{part['text']}")
            case "image_url":
                temp.append(part["image_url"]["url"])

    return "\n".join(temp)