import discord, asyncio, copy
import data.Functions as fun
import data.sokobanMap as map
from discord.ext import commands, tasks

gameName3       = '소코반'
sokobanPlay     = False # 플레이시 id값을 넣음. 시작한 사람이 종료할 수 있도록
sokobanLoop     = False # 루프까지 종료된 상태에서 다시 게임을 시작할 수 있도록 체크
sokobanLevel    = 0
sokobanMessage  = 0
sokobanTimer    = 0
sokobanGoal     = 0
sokobanSysTimer = 0

# 실제 게임이 진행될 변수
sokobanField    = []
sokobanLog      = []

sokobanUnit     = []
sokobanDirection= {'Up':[0,-1], 'Down':[0,1], 'Left':[-1,0], 'Right':[1,0]}
sokobanObject   = ['⬛', '🟫', '🔳', '⚪', '🎃', '⏺️']
# 0:땅 1:벽 2:골 3:돌 4:캐릭터, 5:골+돌


sokobanList     = [0, map.sokobanGame1, map.sokobanGame2, map.sokobanGame3, map.sokobanGame4, map.sokobanGame5, map.sokobanGame6]
sokobanMAX      = len(sokobanList)-1

def checkInt(str):
    ordStr = ord(str)
    if 48 <= ordStr and ordStr <= 57: return True
    return False

def sokobanMapSetting():
    global sokobanField, sokobanUnit, sokobanLevel
    global sokobanList, sokobanTimer, sokobanGoal
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
        embed.set_footer(text = f"{message.display_name} | {gameName3}", icon_url = message.display_avatar)
    await sokobanMessage.edit(embed = embed)
    # await sokobanReaction(sokobanMessage)

async def sokobanMove(direction, message):
    global sokobanTimer, sokobanField, sokobanUnit
    global sokobanDirection, sokobanLog, sokobanSysTimer
    sokobanTimer, sokobanSysTimer= 0, 0
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
    global sokobanMAX, sokobanLevel, sokobanPlay
    global sokobanMessage, sokobanLog
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

class SokobanGame(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
    
    def cog_unload(self):
        if self.run.is_running():
            self.run.cancel()
    
    @tasks.loop(seconds=10)
    async def run(self):
        global sokobanPlay, sokobanMessage
        global sokobanLevel, sokobanSysTimer
        if sokobanPlay:
            sokobanSysTimer += 1
            if sokobanSysTimer > 11:
                embed = discord.Embed(title = f':video_game: {gameName3} │ {sokobanLevel}레벨', description = f'시간 초과로 게임을 종료합니다.', color = 0x324260)
                await sokobanMessage.edit(embed=embed)
                await sokobanMessage.clear_reactions()
                sokobanPlay = False
                sokobanSysTimer = 0
                self.run.stop()
                print(f'sokoban runtime stop')
        else:
            sokobanSysTimer = 0
            self.run.stop()
            print(f'sokoban runtime stop')

    
    @commands.command()
    async def 소코반(self, ctx, *input):
        if(ctx.channel.id in fun.getBotChannel(self.bot, ctx)):
            # try:
            id = ctx.author.id

            if(input[0] == '도움말'):
                embed = discord.Embed(title = f':video_game: {gameName3} 도움말', description = f'{ctx.author.mention} {gameName3} 의 명령어입니다!', color = 0x324260)
                embed.add_field(name = f'!소코반  시작', value = f'레벨을 지정하지 않으면, 1레벨부터 시작해요.')
                embed.add_field(name = f'!소코반  시작  레벨', value = f'소코반을 플레이할 수 있어요. (MAX {sokobanMAX}레벨)')
                # embed.add_field(name = f'!소코반  종료', value = f'소코반 게임을 종료합니다.')
                embed.set_footer(text = f"{ctx.author.display_name} | {gameName3}", icon_url = ctx.author.display_avatar)
                await ctx.channel.send(embed = embed)

            elif(input[0] == '시작'):
                global sokobanPlay, sokobanLoop, sokobanLevel, sokobanField
                global sokobanMessage, sokobanTimer, sokobanLog
                if sokobanPlay or sokobanLoop:
                    embed = discord.Embed(title = f':video_game: {gameName3} 안내', description = f'소코반 게임이 이미 실행된 상태입니다.', color = 0x324260)
                    embed.set_footer(text = f"{ctx.author.display_name} | {gameName3}", icon_url = ctx.author.display_avatar)
                    await ctx.channel.send(embed = embed)
                else:
                    self.run.start() # sokoban System Run
                    sokobanPlay = id
                    sokobanLevel = 1
                    sokobanLog = []
                    if len(input) > 1 and checkInt(input[1]):
                        sokobanLevel = int(input[1])
                    sokobanMapSetting() # 맵세팅
                    embed = discord.Embed(title = f':video_game: {gameName3} 플레이', description = f'소코반 게임을 실행합니다.\n게임을 세팅 중이니 잠시만 기다려주세요.', color = 0x324260)
                    embed.add_field(name = f'레벨', value = f'{sokobanLevel}레벨로 진행')
                    embed.set_footer(text = f"{ctx.author.display_name} | {gameName3}", icon_url = ctx.author.display_avatar)
                    sokobanMessage = await ctx.channel.send(embed = embed)
                    await sokobanReaction(sokobanMessage)
                    await sokobanPrint(0)
                    while True:
                        sokobanLoop = True
                        # await asyncio.sleep(0.5)
                        # await sokobanAnswer()
                        try:
                            def check(reaction, user):
                                return str(reaction) in ['◀️','▶️','🔼','🔽'] and \
                                user != sokobanMessage.author and reaction.message.id == sokobanMessage.id
                            reaction, user = await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
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
            # except BaseException as e:
            #     print(f'소코반게임 {e}')
            #     pass

    @commands.command()
    async def 좌(self, ctx):
        global sokobanPlay
        if sokobanPlay:
            await ctx.message.delete(delay=0)
            await sokobanMove('Left', ctx.message.author)
            await sokobanPrint(ctx.message.author) # 맵갱신
        

    @commands.command()
    async def 우(self, ctx):
        global sokobanPlay
        if sokobanPlay:
            await ctx.message.delete(delay=0)
            await sokobanMove('Right', ctx.message.author)
            await sokobanPrint(ctx.message.author) # 맵갱신
        

    @commands.command()
    async def 상(self, ctx):
        global sokobanPlay
        if sokobanPlay:
            await ctx.message.delete(delay=0)
            await sokobanMove('Up', ctx.message.author)
            await sokobanPrint(ctx.message.author) # 맵갱신

    @commands.command()
    async def 하(self, ctx):
        global sokobanPlay
        if sokobanPlay:
            await ctx.message.delete(delay=0)
            await sokobanMove('Down', ctx.message.author)
            await sokobanPrint(ctx.message.author) # 맵갱신

    @commands.command()
    async def 리셋(self, ctx):
        global sokobanPlay, sokobanLog
        if sokobanPlay:
            await ctx.message.delete(delay=0)
            sokobanLog.append(f'Reset ({ctx.message.author.display_name})')
            sokobanMapSetting() # 맵세팅
            await sokobanPrint(ctx.message.author) # 맵갱신

    @commands.command()
    async def 로그(self, ctx):
        global sokobanPlay
        if sokobanPlay:
            await ctx.message.delete(delay=0)
            logText = ''
            logLen  = len(sokobanLog)
            for log in range(logLen):
                logText += sokobanLog[log]
                if log < logLen-1:
                    logText += ' > '
            embed = discord.Embed(title = f':video_game: {gameName3} 로그', description = f'{logText}', color = 0xff0000)
            embed.set_footer(text = f"{ctx.author.display_name} | {gameName3}", icon_url = ctx.author.display_avatar)
            msg = await ctx.channel.send(embed = embed)
            await msg.delete(delay=10)

    @commands.command()
    async def 종료(self, ctx):
        global sokobanPlay
        if sokobanPlay:
            await ctx.message.delete(delay=0)
            embed = discord.Embed(title = f':video_game: {gameName3} │ {sokobanLevel}레벨', description = f'게임을 종료합니다.', color = 0x324260)
            await sokobanMessage.edit(embed=embed)
            await sokobanMessage.clear_reactions()
            sokobanPlay = False


async def setup(bot):
    await bot.add_cog(SokobanGame(bot))