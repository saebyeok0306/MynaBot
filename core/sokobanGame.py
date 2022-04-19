from unittest import result
import discord
import asyncio
import copy

chatChannel     = 953919871522046008
gameName3       = '소코반'
sokobanPlay     = False # 플레이시 id값을 넣음. 시작한 사람이 종료할 수 있도록
sokobanLoop     = False # 루프까지 종료된 상태에서 다시 게임을 시작할 수 있도록 체크
sokobanLevel    = 0
sokobanMessage  = 0
sokobanTimer    = 0
sokobanGoal     = 0

# 실제 게임이 진행될 변수
sokobanField    = []
sokobanLog      = []

sokobanUnit     = []
sokobanDirection= {'Up':[0,-1], 'Down':[0,1], 'Left':[-1,0], 'Right':[1,0]}
sokobanObject   = ['⬛', '🟫', '🔳', '⚪', '🎃', '⏺️']
# 0:땅 1:벽 2:골 3:돌 4:캐릭터, 5:골+돌
sokobanGame1    = [
    [0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 1, 2, 1, 0, 0, 0],
    [0, 0, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 3, 4, 3, 2, 1],
    [1, 2, 0, 3, 0, 1, 1, 1],
    [1, 1, 1, 1, 3, 1, 0, 0],
    [0, 0, 0, 1, 2, 1, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0]
]
sokobanGame2    = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 0, 0, 1, 0, 0],
    [0, 1, 4, 3, 0, 1, 0, 0],
    [0, 1, 1, 3, 0, 1, 1, 0],
    [0, 1, 1, 0, 3, 0, 1, 0],
    [0, 1, 2, 3, 0, 0, 1, 0],
    [0, 1, 0, 2, 2, 2, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

sokobanGame3    = [
    [0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 1, 1, 1],
    [1, 1, 3, 1, 1, 1, 0, 0, 0, 1],
    [1, 0, 4, 0, 3, 0, 0, 3, 0, 1],
    [1, 0, 2, 2, 1, 0, 3, 0, 1, 1],
    [1, 1, 2, 2, 1, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0]
]

sokobanGame4    = [
    [0, 1, 1, 1, 1, 1, 0, 0],
    [0, 1, 4, 0, 1, 1, 1, 0],
    [0, 1, 0, 3, 0, 0, 1, 0],
    [1, 1, 1, 0, 1, 0, 1, 1],
    [1, 2, 1, 0, 1, 0, 0, 1],
    [1, 2, 3, 0, 0, 1, 0, 1],
    [1, 2, 0, 0, 0, 3, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

sokobanGame5    = [
    [0, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 1, 0, 0, 0, 1, 1, 1, 1],
    [0, 1, 0, 0, 0, 1, 0, 0, 1],
    [0, 1, 1, 0, 0, 0, 0, 2, 1],
    [1, 1, 1, 0, 1, 1, 1, 2, 1],
    [1, 0, 3, 0, 1, 0, 1, 2, 1],
    [1, 0, 3, 3, 1, 0, 1, 1, 1],
    [1, 4, 0, 0, 1, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 0, 0, 0, 0]
]

sokobanGame6    = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 0, 0, 1, 0, 0],
    [0, 1, 4, 3, 0, 1, 0, 0],
    [0, 1, 1, 3, 0, 1, 1, 0],
    [0, 1, 1, 0, 3, 0, 1, 0],
    [0, 1, 2, 3, 0, 0, 1, 0],
    [0, 1, 2, 2, 5, 2, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

sokobanList     = [0, sokobanGame1, sokobanGame2, sokobanGame3, sokobanGame4, sokobanGame5, sokobanGame6]
sokobanMAX      = len(sokobanList)-1

def checkInt(str):
    ordStr = ord(str)
    if 48 <= ordStr and ordStr <= 57: return True
    return False

def sokobanMapSetting():
    global sokobanField
    global sokobanUnit
    global sokobanLevel
    global sokobanList
    global sokobanTimer
    global sokobanGoal
    sokobanTimer = 0
    sokobanGoal  = 0
    sokobanField = copy.deepcopy(sokobanList[sokobanLevel])
    width,height = len(sokobanField[0]), len(sokobanField)
    for y in range(height):
        for x in range(width):
            # 캐릭터 위치 넣기
            if sokobanField[y][x] == 4:
                sokobanField[y][x] = 0
                sokobanUnit = [x,y]
            # 골 갯수 넣기
            if sokobanField[y][x] == 2:
                sokobanGoal += 1
            

async def sokobanPrint(message):
    global sokobanField
    global sokobanUnit
    global sokobanMessage
    width, height = len(sokobanField[0]), len(sokobanField)
    printText = ''
    for y in range(height):
        for x in range(width):
            if sokobanUnit[0] == x and sokobanUnit[1] == y:
                printText += sokobanObject[4]
            else:
                printText += sokobanObject[sokobanField[y][x]]
        printText += '\n'
    printText += '\n채팅으로 !상 !하 !좌 !우 를 입력해서\n조작할 수 있습니다. `(!리셋 !종료)`'
    embed = discord.Embed(title = f':video_game: {gameName3} │ {sokobanLevel}레벨', description = f'{printText}', color = 0x324260)
    if message:
        embed.set_footer(text = f"{message.display_name} | {gameName3}", icon_url = message.avatar_url)
    await sokobanMessage.edit(embed = embed)
    # await sokobanReaction(sokobanMessage)

async def sokobanMove(direction, message):
    global sokobanTimer
    global sokobanField
    global sokobanUnit
    global sokobanDirection
    global sokobanLog
    sokobanTimer= 0
    movement    = sokobanDirection[direction]
    curGrid     = sokobanUnit[:]
    print(f'movement {movement} curGrid {curGrid}')
    moveGrid    = [curGrid[0]+movement[0], curGrid[1]+movement[1]]
    moveAction  = sokobanField[moveGrid[1]][moveGrid[0]]
    moveBlock   = False
    
    # 벽인 경우
    if moveAction == 1:
        moveBlock = True
    # 돌인 경우
    elif moveAction == 3:
        moveGrid2 = [moveGrid[0]+movement[0], moveGrid[1]+movement[1]]
        moveAction2 = sokobanField[moveGrid2[1]][moveGrid2[0]]
        # 돌앞이 벽인 경우
        if moveAction2 == 1:
            moveBlock = True
        # 돌앞에 돌이 있는 경우
        elif moveAction2 == 3:
            moveBlock = True
        # 돌앞이 골인 경우
        elif moveAction2 == 2:
            sokobanUnit = moveGrid[:]
            sokobanField[moveGrid[1]][moveGrid[0]] = 0
            sokobanField[moveGrid2[1]][moveGrid2[0]] = 5 # 골과 돌이 합쳐짐
        else:
            sokobanUnit = moveGrid[:]
            sokobanField[moveGrid[1]][moveGrid[0]] = 0
            sokobanField[moveGrid2[1]][moveGrid2[0]] = 3
    # 골+돌이 있는 경우
    elif moveAction == 5:
        moveGrid2 = [moveGrid[0]+movement[0], moveGrid[1]+movement[1]]
        moveAction2 = sokobanField[moveGrid2[1]][moveGrid2[0]]
        # 돌앞이 벽인 경우
        if moveAction2 == 1:
            moveBlock = True
        # 돌앞에 돌이 있는 경우
        elif moveAction2 == 3:
            moveBlock = True
        # 돌앞이 골인 경우
        elif moveAction2 == 2:
            sokobanUnit = moveGrid[:]
            sokobanField[moveGrid[1]][moveGrid[0]] = 2
            sokobanField[moveGrid2[1]][moveGrid2[0]] = 5 # 골과 돌이 합쳐짐
        else:
            sokobanUnit = moveGrid[:]
            sokobanField[moveGrid[1]][moveGrid[0]] = 2
            sokobanField[moveGrid2[1]][moveGrid2[0]] = 3
    else:
        sokobanUnit = moveGrid[:]
    
    if not moveBlock:
        sokobanLog.append(f'{direction} ({message.display_name})')
    else:
        sokobanLog.append(f'Block ({message.display_name})')
    await sokobanAnswer(message)

async def sokobanAnswer(message):
    global sokobanField
    global sokobanGoal
    global sokobanLog
    global sokobanLevel
    width,height = len(sokobanField[0]), len(sokobanField)
    checkGoal = 0
    for y in range(height):
        for x in range(width):
            if sokobanField[y][x] == 5:
                checkGoal += 1
    if checkGoal == sokobanGoal:
        sokobanLog.append(f'Lv.{sokobanLevel} Clear ({message.display_name})')
        await sokobanNextLevel()
    return False

async def sokobanNextLevel():
    global sokobanMAX
    global sokobanLevel
    global sokobanPlay
    global sokobanMessage
    global sokobanLog
    if sokobanLevel < sokobanMAX:
        await asyncio.sleep(1)
        sokobanLevel += 1
        sokobanMapSetting()
        await sokobanPrint(0)
    else:
        sokobanPlay = False
        embed = discord.Embed(title = f':video_game: {gameName3} │ {sokobanLevel}레벨', description = f'더이상 문제가 없기 때문에 종료합니다.', color = 0x324260)
        await sokobanMessage.edit(embed = embed)
        sokobanLog.append(f'종료')


async def sokobanReaction(embedText):
    await embedText.add_reaction('◀️')
    await embedText.add_reaction('▶️')
    await embedText.add_reaction('🔼')
    await embedText.add_reaction('🔽')

async def sokobanMessage(message, bot, *input):
    if(message.channel.id == chatChannel): #게임채팅채널에서 채팅을 친경우
        try:
            id = message.author.id
            input = input[0]
            if(input[0] == '도움말'):
                embed = discord.Embed(title = f':video_game: {gameName3} 도움말', description = f'{message.author.mention} {gameName3} 의 명령어입니다!', color = 0x324260)
                embed.add_field(name = f'!소코반  시작', value = f'레벨을 지정하지 않으면, 1레벨부터 시작해요.')
                embed.add_field(name = f'!소코반  시작  레벨', value = f'소코반을 플레이할 수 있어요. (MAX {sokobanMAX}레벨)')
                # embed.add_field(name = f'!소코반  종료', value = f'소코반 게임을 종료합니다.')
                embed.set_footer(text = f"{message.author.display_name} | {gameName3}", icon_url = message.author.avatar_url)
                await message.channel.send(embed = embed)
            elif(input[0] == '시작'):
                global sokobanPlay
                global sokobanLoop
                global sokobanLevel
                global sokobanField
                global sokobanMessage
                global sokobanTimer
                global sokobanLog
                if sokobanPlay or sokobanLoop:
                    embed = discord.Embed(title = f':video_game: {gameName3} 안내', description = f'소코반 게임이 이미 실행된 상태입니다.', color = 0x324260)
                    embed.set_footer(text = f"{message.author.display_name} | {gameName3}", icon_url = message.author.avatar_url)
                    await message.channel.send(embed = embed)
                else:
                    sokobanPlay = id
                    sokobanLevel = 1
                    sokobanLog = []
                    if len(input) > 1 and checkInt(input[1]):
                        sokobanLevel = int(input[1])
                    sokobanMapSetting() # 맵세팅
                    embed = discord.Embed(title = f':video_game: {gameName3} 플레이', description = f'소코반 게임을 실행합니다.\n게임을 세팅 중이니 잠시만 기다려주세요.', color = 0x324260)
                    embed.add_field(name = f'레벨', value = f'{sokobanLevel}레벨로 진행')
                    embed.set_footer(text = f"{message.author.display_name} | {gameName3}", icon_url = message.author.avatar_url)
                    sokobanMessage = await message.channel.send(embed = embed)
                    await sokobanReaction(sokobanMessage)
                    await sokobanPrint(0)
                    while True:
                        sokobanLoop = True
                        # await asyncio.sleep(0.5)
                        # await sokobanAnswer()
                        try:
                            def check(reaction, user):
                                return str(reaction) in ['◀️','▶️','🔼','🔽'] and \
                                user != sokobanMessage.author
                            reaction, user = await bot.wait_for('reaction_add', timeout=20.0, check=check)
                            if str(reaction) == '◀️':
                                await sokobanMessage.clear_reactions()
                                await sokobanMove('Left', user)
                                await sokobanPrint(user)
                                await sokobanReaction(sokobanMessage)
                            elif str(reaction) == '▶️':
                                await sokobanMessage.clear_reactions()
                                await sokobanMove('Right', user)
                                await sokobanPrint(user)
                                await sokobanReaction(sokobanMessage)
                            elif str(reaction) == '🔼':
                                await sokobanMessage.clear_reactions()
                                await sokobanMove('Up', user)
                                await sokobanPrint(user)
                                await sokobanReaction(sokobanMessage)
                            elif str(reaction) == '🔽':
                                await sokobanMessage.clear_reactions()
                                await sokobanMove('Down', user)
                                await sokobanPrint(user)
                                await sokobanReaction(sokobanMessage)
                        except asyncio.TimeoutError:
                            if not sokobanPlay and sokobanLoop:
                                sokobanLoop = False
                                await sokobanMessage.add_reaction('⏹️')
                                break
        except:
            print("소코반에러")
            pass


# async def sokobanReaction(embedText):
#     await embedText.add_reaction('◀️')
#     await embedText.add_reaction('▶️')
#     await embedText.add_reaction('🔼')
#     await embedText.add_reaction('🔽')
#     await embedText.add_reaction('🔄')
#     await embedText.add_reaction('⏹️')

# await sokobanPrint() # 맵갱신
# await asyncio.sleep(0.5)
# try:
#     def check(reaction, user):
#         return str(reaction) in ['◀️','▶️','🔼','🔽','🔄','⏹️']
#     reaction, user = await bot.wait_for('reaction_add', check=check)
#     if str(reaction) == '◀️':
#         await sokobanMessage.clear_reactions()
#         sokobanMove('Left')
#     elif str(reaction) == '▶️':
#         await sokobanMessage.clear_reactions()
#         sokobanMove('Right')
#     elif str(reaction) == '🔼':
#         await sokobanMessage.clear_reactions()
#         sokobanMove('Up')
#     elif str(reaction) == '🔽':
#         await sokobanMessage.clear_reactions()
#         sokobanMove('Down')
#     elif str(reaction) == '🔄':
#         await sokobanMessage.clear_reactions()
#         sokobanMapSetting() # 맵세팅
#     elif str(reaction) == '⏹️':
#         embed = discord.Embed(title = f':video_game: {gameName3} │ {sokobanLevel}레벨', description = f'게임을 종료합니다.', color = 0x324260)
#         await sokobanMessage.clear_reactions()
#         await sokobanMessage.add_reaction('⏹️')
#         await sokobanMessage.edit(embed=embed)
#         sokobanPlay = False
#         break
# except:
#     break