import sqlite3
import discord
import asyncio
import random
import datetime
import json
from discord.ext import commands
from bitcoinGame import *
from swordGame import *
from sokobanGame import *
import sokobanGame as soko
# from messageBot import *
# from autoProfile import *
# from rtx3070ti import *
# from edacUsemap import *

#pip3 install discord
#pip3 install asyncio
#pip3 install websockets
#pip3 install aiohttp
#pip3 install requests
#pip3 install beautifulsoup4
# import os

# print(os.getcwd())

workHour,workMin,workSec = 0,0,0
coinDelay = 0

bot = commands.Bot(command_prefix='!')
token = ''
with open("data/token.json", "r") as f:
    loaded_data = json.load(f)  # 데이터 로드하기
    token = loaded_data['token']

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

def check_Discord():
    guildList = bot.guilds
    for server in guildList:
        if(server.id == 631471244088311840): #내 디코서버일 때
            return server

async def check_GuildUser(id):
    try:
        server = check_Discord()
        return await server.fetch_member(id)
    except:
        return False

@bot.event
async def on_ready():
    print('로그인되었습니다!')
    print(bot.user.name)
    print(bot.user.id)
    print('==============================')
    game = discord.Game("명령어는 [!도움말] 참고")
    await bot.change_presence(status=discord.Status.online, activity=game)

    global coinDelay
    global workHour
    global workMin
    global workSec
    while True:
        now = datetime.datetime.today()
        server = check_Discord()
        # await autoProfile(g, now)
        if coinDelay == 0:
            coinDelay = 4
            await bitcoinSystem(server)
        else:
            coinDelay -= 1
        
        print(f'{workHour}h {workMin}m {workSec}s')
        workSec += 10
        if workSec >= 60:
            workSec -= 60
            workMin += 1
            if workMin >= 60:
                workMin -= 60
                workHour += 1
        if soko.sokobanPlay:
            soko.sokobanTimer += 1
            if soko.sokobanTimer > 20:
                embed = discord.Embed(title = f':video_game: {soko.gameName3} │ {soko.sokobanLevel}레벨', description = f'시간 초과로 게임을 종료합니다.', color = 0x324260)
                await soko.sokobanMessage.edit(embed=embed)
                await soko.sokobanMessage.clear_reactions()
                soko.sokobanPlay = False
        #a = await check_GuildUser(383483844218585108)
        await asyncio.sleep(10)
    

@bot.event
async def on_message(message):
    # if message.content == '!마크':
    #     owner = await check_GuildUser(383483844218585108)
    #     embed=discord.Embed(color=0xB22222, title="모드서버", description="`갈대`의 1.17.1 패브릭서버", timestamp=message.created_at)
    #     embed.set_thumbnail(url=owner.avatar_url)
    #     embed.add_field(name = '서버주소', value = 'westreed.kro.kr')
    #     embed.add_field(name = '서버문의', value = '@갈대#2519 에게 연락하세요!')
    #     embed.add_field(name = '서버모드', value = 'https://drive.google.com/drive/folders/1hmhwEPjykEU257-PMXHJQbS0Tx_0XyVA?usp=sharing')
    #     embed.add_field(name = '모드리스트', value = '갈대서버에 사용된 모드는 "!갈대서버"를 입력하세요.')
    #     embed.add_field(name = '에러발생시', value = 'https://www.curseforge.com/minecraft/mc-mods/lib/download/3459369\n다운 받아서 모드폴더에 덮어씌워보세요.')
    #     embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
    #     await message.channel.send(embed=embed)
    
    # if message.content == '!갈대서버':
    #     owner = await check_GuildUser(383483844218585108)
    #     embed=discord.Embed(color=0xB22222, title="갈대서버의 모드리스트", description="사용된 모드리스트입니다.\nhttps://drive.google.com/drive/folders/1hmhwEPjykEU257-PMXHJQbS0Tx_0XyVA?usp=sharing\n넣는경로 C:\\Users\\\계정명\\AppData\\Roaming\\\.minecraft\\mods", timestamp=message.created_at)
    #     embed.set_thumbnail(url=owner.avatar_url)
    #     embed.add_field(name = 'AppleSkin', value = '허기와 관련된 GUI 표기')
    #     embed.add_field(name = 'NaturesCompass', value = '특정 바이옴의 위치 탐색')
    #     embed.add_field(name = 'Waystones', value = '마을에 있는 워프스톤 관련 모드')
    #     embed.add_field(name = 'Wthit', value = '마우스로 가리키는 대상의 정보를 보여주는 모드')
    #     embed.add_field(name = 'Xaero`s Minimap', value = '미니맵 모드')
    #     embed.add_field(name = 'CocoaInput(선택)', value = '한글 채팅모드')
    #     embed.add_field(name = 'illuminations(선택)', value = '반딧불이와 같은 다양한 야광효과모드')
    #     embed.add_field(name = 'logicalZoom(선택)', value = '옵티파인의 확대기능을 구현한 모드')
    #     embed.add_field(name = 'IronChests', value = '다양한 상자를 추가하는 모드')
    #     embed.add_field(name = 'Pipe', value = '뭣같은 호퍼 대신 아름다운 파이프를 드림')
    #     embed.add_field(name = 'BetterEnd', value = '더 나은 엔더월드 모드')
    #     embed.add_field(name = 'BetterNether', value = '더 나은 네더월드 모드')
    #     embed.add_field(name = 'Charm', value = '오버월드 관련 모드')
    #     embed.add_field(name = 'RepurposedStructures', value = '오버월드 관련 모드')
    #     embed.add_field(name = 'MoStructures', value = '오버월드 관련 모드')
    #     embed.add_field(name = 'WilliamWythersOverhauledOverworld', value = '오버월드 관련 모드')
    #     embed.add_field(name = 'MoreStructuresForWilliamWythersOverhauledOverworld', value = '오버월드 관련 모드')
    #     embed.add_field(name = 'FerriteCore', value = '메모리 최적화 모드')
    #     embed.add_field(name = 'Lazydfu', value = '최적화 관련 모드')
    #     embed.add_field(name = 'Light-Fix', value = '마크의 광원 버그 개선 모드')
    #     embed.add_field(name = 'Lithium', value = '최적화 관련 모드')
    #     embed.add_field(name = 'Iris-and-Sodium', value = '최적화 및 쉐이더 관련 모드')
    #     embed.add_field(name = 'LambDynamicLights(선택)', value = '동적 조명 관련 모드')
    #     embed.add_field(name = 'Fabric API', value = 'API 모드')
    #     embed.add_field(name = 'Cloth Config API', value = 'API 모드')
    #     embed.add_field(name = 'Bclib', value = 'API 모드')
    #     embed.add_field(name = 'FlytreLib', value = 'API 모드')
    #     embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
    #     await message.channel.send(embed=embed)
        
    if message.content == '!도움말':
        embed=discord.Embed(color=0xB22222, title="도움말:", description="마이나에게 있는 명령어들을 알려드려요. By.갈대", timestamp=message.created_at)
        embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
        embed.add_field(name = '!주사위 `값(기본값 100)`', value = '주사위를 굴립니다. 범위:1~100  값을 입력하면 1~값까지')
        # embed.add_field(name = '!계산 `수식`', value = '수식을 계산해줍니다.')
        # embed.add_field(name = '!마크', value = '디코방에서 운영되고 있는 서버주소를 알려줘요!')
        embed.add_field(name = '!회원가입', value = '디코게임을 이용하려면, 가입이 필요해요.')
        embed.add_field(name = '!회원탈퇴', value = '회원가입이 있으면 회원탈퇴도 있는법.')
        embed.add_field(name = '!코인 도움말', value = '!코인게임\n명령어를 확인할 수 있어요.')
        embed.add_field(name = '!강화 도움말', value = '!강화게임\n명령어를 확인할 수 있어요.')
        await message.channel.send(embed=embed)

    if message.author.bot: return None
    await bot.process_commands(message)



@bot.command()
async def 코인(ctx, *input):
    await bitcoinMessage(ctx, input)

@bot.command()
async def 강화(ctx, *input):
    await swordMessage(ctx, bot, input)

@bot.command()
async def 소코반(ctx, *input):
    await sokobanMessage(ctx, bot, input)

# @bot.command()
# async def 계산(ctx, *input):
#     text = " ".join(input)
#     try:
#         await ctx.channel.send(f'{str(eval(text))}')
#     except:
#         print(text)
#         await ctx.channel.send(f'수식에 오류가 있어요.')

@bot.command()
async def 주사위(ctx, *input):
    # input이 없는 경우
    value = 100
    try:
        if input:
            if int(input[0]) <= 1: return
            else: value = int(input[0])
    except:
        pass
    
    r = random.randint(1, value)
    await ctx.channel.send(f'주사위를 굴립니다...\n두둥! `{r}`입니다!')
    


gameTitle = '게임서비스'
@bot.command()
async def 회원가입(ctx):
    if(ctx.channel.id == 953919871522046008):
        id = ctx.author.id
        check = game_check(id)
        con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
        cur = con.cursor()
        now = datetime.datetime.now()
        nowDatetime = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
        if check == False:
            null = 'NULL'
            cur.execute("INSERT INTO User_Info VALUES(?, ?, ?, ?, ?)", (id, ctx.author.display_name, nowDatetime, 0, null))
            embed = discord.Embed(title = f':wave: {gameTitle} 가입', description = f'{ctx.author.mention} 성공적으로 갈대의 {gameTitle}에 가입되셨습니다.', color = 0xffc0cb)
            embed.set_footer(text = f"{ctx.author.display_name} | {gameTitle}", icon_url = ctx.author.avatar_url)
            await ctx.channel.send(embed = embed)
        elif check == True:
            embed = discord.Embed(title = f':wave: {gameTitle} 가입', description = f'{ctx.author.mention} 이미 {gameTitle}에 가입되어 있습니다.', color = 0xff0000)
            embed.set_footer(text = f"{ctx.author.display_name} | {gameTitle}", icon_url = ctx.author.avatar_url)
            await ctx.channel.send(embed = embed)
        con.close() #db 종료

@bot.command()
async def 회원탈퇴(ctx):
    if(ctx.channel.id == 953919871522046008):
        id = ctx.author.id
        check = game_check(id)
        con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
        cur = con.cursor()
        cur.execute("SELECT user_Date FROM User_Info WHERE user_ID = ?", (id,))
        userInfo = cur.fetchone()
        now = datetime.datetime.now()
        joindate = datetime.datetime.strptime(userInfo[0], '%Y-%m-%d %H:%M:%S')
        if now.day != joindate.day:
            if check == False:
                embed = discord.Embed(title = f':heart: {gameTitle} 탈퇴', description = f'{ctx.author.mention} 갈대의 {gameTitle}에 가입되어 있지 않습니다.', color = 0xff0000)
                embed.set_footer(text = f"{ctx.author.display_name} | {gameTitle}", icon_url = ctx.author.avatar_url)
                await ctx.channel.send(embed = embed)
            elif check == True:
                cur.execute("DELETE FROM 'User_Info' WHERE user_ID = ?", (id,))
                cur.execute("DELETE FROM 'Coin_Trade' WHERE trade_UserID = ?", (id,))
                cur.execute("DELETE FROM 'Coin_NameList' WHERE user_ID = ?", (id,))
                cur.execute("DELETE FROM 'Sword_Info' WHERE sword_UserID = ?", (id,))
                embed = discord.Embed(title = f':heart: {gameTitle} 탈퇴', description = f'{ctx.author.mention} 성공적으로 {gameTitle}에서 탈퇴되셨습니다.', color = 0xffc0cb)
                embed.set_footer(text = f"{ctx.author.display_name} | {gameTitle}", icon_url = ctx.author.avatar_url)
                await ctx.channel.send(embed = embed)
        else:
            embed = discord.Embed(title = f':x: {gameTitle} 탈퇴불가능', description = f'{ctx.author.mention} 가입한 날로부터 하루가 지나야 합니다!\n가입날짜 `{joindate.year}년 {joindate.month}월 {joindate.day}일`', color = 0xff0000)
            embed.set_footer(text = f"{ctx.author.display_name} | {gameTitle}", icon_url = ctx.author.avatar_url)
            await ctx.channel.send(embed = embed)
        con.close() #db 종료
        
@bot.command()
async def 좌(ctx):
    if soko.sokobanPlay:
        await ctx.message.delete(delay=0)
        await sokobanMove('Left', ctx.message.author)
        await sokobanPrint(ctx.message.author) # 맵갱신
    

@bot.command()
async def 우(ctx):
    if soko.sokobanPlay:
        await ctx.message.delete(delay=0)
        await sokobanMove('Right', ctx.message.author)
        await sokobanPrint(ctx.message.author) # 맵갱신
    

@bot.command()
async def 상(ctx):
    if soko.sokobanPlay:
        await ctx.message.delete(delay=0)
        await sokobanMove('Up', ctx.message.author)
        await sokobanPrint(ctx.message.author) # 맵갱신

@bot.command()
async def 하(ctx):
    if soko.sokobanPlay:
        await ctx.message.delete(delay=0)
        await sokobanMove('Down', ctx.message.author)
        await sokobanPrint(ctx.message.author) # 맵갱신

@bot.command()
async def 리셋(ctx):
    if soko.sokobanPlay:
        await ctx.message.delete(delay=0)
        soko.sokobanLog.append(f'Reset ({ctx.message.author.display_name})')
        sokobanMapSetting() # 맵세팅
        await sokobanPrint(ctx.message.author) # 맵갱신

@bot.command()
async def 로그(ctx):
    if soko.sokobanPlay:
        await ctx.message.delete(delay=0)
        logText = ''
        logLen  = len(soko.sokobanLog)
        for log in range(logLen):
            logText += soko.sokobanLog[log]
            if log < logLen-1:
                logText += ' > '
        embed = discord.Embed(title = f':video_game: {soko.gameName3} 로그', description = f'{logText}', color = 0xff0000)
        embed.set_footer(text = f"{ctx.author.display_name} | {gameTitle}", icon_url = ctx.author.avatar_url)
        msg = await ctx.channel.send(embed = embed)
        await msg.delete(delay=10)

@bot.command()
async def 종료(ctx):
    if soko.sokobanPlay:
        await ctx.message.delete(delay=0)
        embed = discord.Embed(title = f':video_game: {soko.gameName3} │ {soko.sokobanLevel}레벨', description = f'게임을 종료합니다.', color = 0x324260)
        await soko.sokobanMessage.edit(embed=embed)
        await soko.sokobanMessage.clear_reactions()
        soko.sokobanPlay = False
# @client.event
# async def on_member_join(member):
#     await member.guild.get_channel(631477839144812586).send(member.mention + "님이 새롭게 접속했습니다. 환영해요!")
    #await member.guild.get_channel(631477839144812586).send("저희 서버는 [reedfarm.kro.kr] 주소로 접속하시면 되요.")
    #author = await client.get_user(383483844218585108).create_dm()
    #await author.send("<@{}>님께서 마인팜 서버에 가입하셨습니다.".format(str(member.id)))
    #await member.guild.get_channel(709349938470846557).send("<@{}> 님을 호출했으니 오래 걸리진 않을거에요... 아마?".format(383483844218585108))

bot.run(token)

