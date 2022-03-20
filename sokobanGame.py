import discord
import asyncio
import copy

chatChannel     = 953919871522046008
gameName3       = '소코반'
sokobanMAX      = 1
sokobanPlay     = False # 플레이시 id값을 넣음. 시작한 사람이 종료할 수 있도록
sokobanLevel    = 0
sokobanMessage  = 0

# 실제 게임이 진행될 변수
sokobanField    = []

sokobanUnit     = []
sokobanDirection= {'Up':[0,-1], 'Down':[0,1], 'Left':[-1,0], 'Right':[1,0]}
sokobanObject   = ['⬛', '🟫', '🔳', '⚪', '🎃', '⏺️', '🎃']
# 0:땅 1:벽 2:골 3:돌 4:캐릭터, 5:골+돌 6:캐릭터+골
sokobanGame1    = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 4, 0, 2, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 3, 0, 0, 3, 2, 0, 1],
    [1, 0, 3, 0, 0, 2, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

sokobanList     = [0, sokobanGame1]

def checkInt(str):
    ordStr = ord(str)
    if 48 <= ordStr and ordStr <= 57: return True
    return False

def sokobanMapSetting():
    global sokobanField
    global sokobanUnit
    global sokobanLevel
    global sokobanList
    sokobanField = copy.deepcopy(sokobanList[sokobanLevel])
    width, height = len(sokobanField[0]), len(sokobanField)
    for y in range(height):
        for x in range(width):
            if sokobanField[y][x] == 4:
                sokobanField[y][x] = 0
                sokobanUnit = [x,y]
                return True
    return False
            

def sokobanPrint(message):
    global sokobanField
    global sokobanUnit
    width, height = len(sokobanField[0]), len(sokobanField)
    printText = ''
    for y in range(height):
        for x in range(width):
            if sokobanUnit[0] == x and sokobanUnit[1] == y:
                printText += sokobanObject[4]
            else:
                printText += sokobanObject[sokobanField[y][x]]
        printText += '\n'
    embed = discord.Embed(title = f':video_game: {gameName3} │ {sokobanLevel}레벨', description = f'{printText}', color = 0x324260)
    embed.set_footer(text = f"{message.author.display_name} | {gameName3}", icon_url = message.author.avatar_url)
    return embed

def sokobanMove(direction):
    global sokobanField
    global sokobanUnit
    global sokobanDirection
    movement    = sokobanDirection[direction]
    curGrid     = sokobanUnit[:]
    print(f'movement {movement} curGrid {curGrid}')
    moveGrid    = [curGrid[0]+movement[0], curGrid[1]+movement[1]]
    moveAction  = sokobanField[moveGrid[1]][moveGrid[0]]
    
    # 벽인 경우
    if moveAction == 1:
        return False
    # 돌인 경우
    elif moveAction == 3:
        moveGrid2 = [moveGrid[0]+movement[0], moveGrid[1]+movement[1]]
        moveAction2 = sokobanField[moveGrid2[1]][moveGrid2[0]]
        # 돌앞이 벽인 경우
        if moveAction2 == 1:
            return False
        # 돌앞에 돌이 있는 경우
        elif moveAction2 == 3:
            return False
        # 돌앞이 골인 경우
        elif moveAction2 == 2:
            sokobanUnit = moveGrid[:]
            sokobanField[moveGrid[1]][moveGrid[0]] = 0
            sokobanField[moveGrid2[1]][moveGrid2[0]] = 5 # 골과 돌이 합쳐짐
            return True
        else:
            sokobanUnit = moveGrid[:]
            sokobanField[moveGrid[1]][moveGrid[0]] = 0
            sokobanField[moveGrid2[1]][moveGrid2[0]] = 3
            return True
    # 골+돌이 있는 경우
    elif moveAction == 5:
        moveGrid2 = [moveGrid[0]+movement[0], moveGrid[1]+movement[1]]
        moveAction2 = sokobanField[moveGrid2[1]][moveGrid2[0]]
        # 돌앞이 벽인 경우
        if moveAction2 == 1:
            return False
        # 돌앞에 돌이 있는 경우
        elif moveAction2 == 3:
            return False
        # 돌앞이 골인 경우
        elif moveAction2 == 2:
            sokobanUnit = moveGrid[:]
            sokobanField[moveGrid[1]][moveGrid[0]] = 2
            sokobanField[moveGrid2[1]][moveGrid2[0]] = 5 # 골과 돌이 합쳐짐
            return True
        else:
            sokobanUnit = moveGrid[:]
            sokobanField[moveGrid[1]][moveGrid[0]] = 2
            sokobanField[moveGrid2[1]][moveGrid2[0]] = 3
            return True
    else:
        sokobanUnit = moveGrid[:]
        return True


async def sokobanReaction(embedText):
    await embedText.add_reaction('◀️')
    await embedText.add_reaction('▶️')
    await embedText.add_reaction('🔼')
    await embedText.add_reaction('🔽')
    await embedText.add_reaction('🔄')
    await embedText.add_reaction('⏹️')


async def sokobanMessage(message, bot, *input):
    if(message.channel.id == chatChannel): #게임채팅채널에서 채팅을 친경우
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
            global sokobanLevel
            global sokobanField
            global sokobanMessage
            if sokobanPlay:
                embed = discord.Embed(title = f':video_game: {gameName3} 안내', description = f'소코반 게임이 이미 실행된 상태입니다.', color = 0x324260)
                embed.set_footer(text = f"{message.author.display_name} | {gameName3}", icon_url = message.author.avatar_url)
                await message.channel.send(embed = embed)
            else:
                sokobanPlay = id
                sokobanLevel = 1
                sokobanMapSetting() # 맵세팅
                if len(input) > 1 and checkInt(input[1]):
                    sokobanLevel = int(input[1])
                embed = discord.Embed(title = f':video_game: {gameName3} 플레이', description = f'소코반 게임을 실행합니다.\n게임을 세팅 중이니 잠시만 기다려주세요.', color = 0x324260)
                embed.add_field(name = f'레벨', value = f'{sokobanLevel}레벨로 진행')
                embed.set_footer(text = f"{message.author.display_name} | {gameName3}", icon_url = message.author.avatar_url)
                sokobanMessage = await message.channel.send(embed = embed)
                while True:
                    embed = sokobanPrint(message)
                    await sokobanMessage.edit(embed = embed)
                    await sokobanReaction(sokobanMessage)
                    await asyncio.sleep(0.5)
                    try:
                        def check(reaction, user):
                            return str(reaction) in ['◀️','▶️','🔼','🔽','🔄','⏹️']
                        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
                        if str(reaction) == '◀️':
                            await sokobanMessage.clear_reactions()
                            sokobanMove('Left')
                        elif str(reaction) == '▶️':
                            await sokobanMessage.clear_reactions()
                            sokobanMove('Right')
                        elif str(reaction) == '🔼':
                            await sokobanMessage.clear_reactions()
                            sokobanMove('Up')
                        elif str(reaction) == '🔽':
                            await sokobanMessage.clear_reactions()
                            sokobanMove('Down')
                        elif str(reaction) == '🔄':
                            await sokobanMessage.clear_reactions()
                            sokobanMapSetting() # 맵세팅
                        elif str(reaction) == '⏹️':
                            embed = discord.Embed(title = f':video_game: {gameName3} │ {sokobanLevel}레벨', description = f'게임을 종료합니다.', color = 0x324260)
                            await sokobanMessage.clear_reactions()
                            await sokobanMessage.add_reaction('⏹️')
                            await sokobanMessage.edit(embed=embed)
                            sokobanPlay = False
                            break
                    except asyncio.TimeoutError:
                            embed = discord.Embed(title = f':video_game: {gameName3} │ {sokobanLevel}레벨', description = f'시간초과로 게임이 종료됩니다.', color = 0x324260)
                            await sokobanMessage.clear_reactions()
                            await sokobanMessage.add_reaction('⏹️')
                            await sokobanMessage.edit(embed=embed)
                            sokobanPlay = False
                            break



async def sokobanPlaying(ctx):
    pass