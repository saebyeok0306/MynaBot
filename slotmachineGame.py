import sqlite3
import discord
import asyncio
import datetime
import random


gameName3 = '슬롯머신'

# 럭키세븐, 도지, 냥, 페페, 제리, 머쓱
slotList  = ['<a:lucky_seven:961840921144598548>', '<a:thuglifedog:765463003054997515>', '<:NYANG:961824297310101605>', '<:Pepegood:868064047969497129>', '<a:jerry:762198111119605770>', '<:em:672068659295813634>']
slotRand  = [12, 14, 16, 18, 20, 20]
slotRank  = {
    0 : [300, [[0,0,0]]],
    1 : [50, [[1,1,1]]],
    2 : [20, [[2,2,2]]],
    3 : [12, [[5,3,1],[4,2,0]]],
    4 : [11, [[3,3,3]]],
    5 : [10, [[4,4,4]]],
    6 : [9, [[5,5,5]]],
    7 : [3, [[3,4,5],[3,5,4],[4,3,5],[4,5,3],[5,3,4],[5,4,3]]]
}

chatChannel = 953919871522046008

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
    userName = cur.fetchone()
    # 저장된 닉네임과 일치하지 않는 경우
    if userName[0] != msg.author.display_name:
        cur.execute("UPDATE 'User_Info' SET user_Name = ?WHERE user_ID = ? ", (msg.author.display_name, id,))
    con.close() #db 종료

async def slotMessage(message, bot, *input):
    if(message.channel.id == chatChannel):
        try:
            id = message.author.id
            check = game_check(id)
            if check == 0:
                embed = discord.Embed(title = f':exclamation: {gameName3} 미가입', description = f'{message.author.mention} {gameName3} 게임에 가입하셔야 이용이 가능합니다. (!회원가입)', color = 0xff0000)
                embed.set_footer(text = f"{message.author.display_name} | {gameName3}", icon_url = message.author.avatar_url)
                await message.channel.send(embed = embed)
                return 0
            setUserName(id, message)
            input = input[0]
            if(input[0] == '도움말'):
                con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                cur = con.cursor()
                cur.execute("SELECT total_Betting FROM Slot_Info")
                total_Betting = cur.fetchone()[0]
                con.close() #db 종료

                if total_Betting >= 10:
                    total_Betting //= 2
                else:
                    total_Betting = 0

                embed = discord.Embed(title = f':video_game: {gameName3} 도움말', description = f'{message.author.mention} {gameName3} 의 명령어입니다!', color = 0x324260)
                embed.set_footer(text = f"{message.author.display_name} | {gameName3}", icon_url = message.author.avatar_url)
                embed.add_field(name=f'1등 (배팅금액×300배 + {printN(total_Betting)}원)', value=f'{slotList[0]}{slotList[0]}{slotList[0]}\n추가로 슬롯머신에 담긴 배팅금액의 절반도 지급됩니다.')
                embed.add_field(name=f'2등 (배팅금액×50배)', value=f'{slotList[1]}{slotList[1]}{slotList[1]}')
                embed.add_field(name=f'3등 (배팅금액×20배)', value=f'{slotList[2]}{slotList[2]}{slotList[2]}')
                embed.add_field(name=f'4등 (배팅금액×12배)', value=f'{slotList[5]}{slotList[3]}{slotList[1]} or\n{slotList[4]}{slotList[2]}{slotList[0]}')
                embed.add_field(name=f'5등 (배팅금액×11배)', value=f'{slotList[3]}{slotList[3]}{slotList[3]}')
                embed.add_field(name=f'6등 (배팅금액×10배)', value=f'{slotList[4]}{slotList[4]}{slotList[4]}')
                embed.add_field(name=f'7등 (배팅금액×9배)', value=f'{slotList[5]}{slotList[5]}{slotList[5]}')
                embed.add_field(name=f'8등 (배팅금액×3배)', value=f'{slotList[3]},{slotList[4]},{slotList[5]}\n위치 상관없이 1개씩 나온 경우')
                embed.add_field(name=f'!슬롯 [배팅금액]', value=f'슬롯머신을 돌립니다.')
                await message.channel.send(embed = embed)
                return 0
            
            elif input[0] == '내정보':
                con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                cur = con.cursor()
                cur.execute("SELECT user_Money, slot_Betting, slot_Reward FROM User_Info WHERE user_ID = ?", (id,))
                userInfo = cur.fetchone()
                myMoney,myBetting,myReward = userInfo[0],userInfo[1],userInfo[2]
                cur.execute("SELECT total_Betting FROM Slot_Info")
                total_Betting = cur.fetchone()[0]
                con.close() #db 종료

                PM,diffMoney = '',0
                if myBetting > myReward:
                    PM = '-'
                    diffMoney = myBetting-myReward
                else:
                    PM = '+'
                    diffMoney = myReward-myBetting


                embed = discord.Embed(title = f'{message.author.display_name}님의 정보창', description = f'{gameName3} 게임에서의 본인 정보입니다.\n현금 재산은 모든 게임에서 공유됩니다.', color = 0xffc0cb)
                embed.set_thumbnail(url=message.author.avatar_url)
                embed.add_field(name = f'총 배팅액', value = f'{printN(myBetting)}원')
                embed.add_field(name = f'총 당첨액', value = f'{printN(myReward)}원')
                embed.add_field(name = f'손익률', value = f'{PM}{printN(diffMoney)}원')
                embed.add_field(name = f'현금 재산', value = f':dollar:{printN(myMoney)}원')
                embed.add_field(name = f'슬롯머신 배팅금', value = f'슬롯머신에 저장된 배팅금액입니다. (1등 보상)\n{printN(total_Betting)}원')
                await message.channel.send(embed = embed)
                return 0

            betting = 0
            try:
                betting = int(input[0])
                
            except:
                embed = discord.Embed(title = f':exclamation: {gameName3} 오류', description = f'{message.author.mention} 배팅하실 금액을 입력하셔야 합니다.\n!슬롯 [배팅금액]', color = 0xff0000)
                embed.set_footer(text = f"{message.author.display_name} | {gameName3}", icon_url = message.author.avatar_url)
                await message.channel.send(embed = embed)
                return 0

            con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
            cur = con.cursor()
            cur.execute("SELECT user_Money, slot_Betting, slot_Reward FROM User_Info WHERE user_ID = ?", (id,))
            userInfo = cur.fetchone()
            myMoney,myBetting,myReward = userInfo[0],userInfo[1],userInfo[2]
            con.close() #db 종료

            if myMoney < betting:
                embed = discord.Embed(title = f':exclamation: {gameName3} 금액부족', description = f'{message.author.mention} 보유하고 계시는 자산이 부족합니다.\n보유재산 `{printN(myMoney)}원` :money_with_wings:', color = 0xff0000)
                embed.set_footer(text = f"{message.author.display_name} | {gameName3}", icon_url = message.author.avatar_url)
                await message.channel.send(embed = embed)
                return 0
            myMoney -= betting
            con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
            cur = con.cursor()
            cur.execute("UPDATE 'User_Info' SET user_Money = ? WHERE user_ID = ?", (myMoney, id))
            con.close() #db 종료

            await message.channel.send(f'{message.author.display_name}님,\n반응 이모지를 클릭해서 슬롯머신을 돌리세요!')
            msg = await message.channel.send(f'❔❔❔')
            await msg.add_reaction('1️⃣')
            await msg.add_reaction('2️⃣')
            await msg.add_reaction('3️⃣')

            open = [0,1,2]
            result = {id : 9 for id in range(3)}

            async def openSlot(msg, index):
                open.remove(index)
                rand = random.randint(0,99)
                rand2 = 0
                for r in range(6):
                    rand2 += slotRand[r]
                    if rand <= rand2:
                        result[index] = r
                        break
                text = ''
                for i in range(3):
                    if result[i] == 9:
                        text += f'❔'
                    else:
                        text += f'{slotList[result[i]]}' 
                await msg.edit(content = text)
            
            while open:
                try:
                    def check(reaction, user):
                        return str(reaction) in ['1️⃣','2️⃣','3️⃣'] and \
                        user == message.author and reaction.message.id == msg.id

                    reaction, user = await bot.wait_for('reaction_add', timeout=15.0, check=check)
                    if str(reaction) == '1️⃣' and 0 in open:
                        await openSlot(msg, 0)
                        continue
                    elif str(reaction) == '2️⃣' and 1 in open:
                        await openSlot(msg, 1)
                        continue
                    elif str(reaction) == '3️⃣' and 2 in open:
                        await openSlot(msg, 2)
                        continue
                except asyncio.TimeoutError:
                    for o in open:
                        await openSlot(msg, o)
                        continue
            await msg.clear_reactions()

            _result = list(result.values())
            rank = None
            money = 0
            userBetting = 0 # 유저들이 배팅했던 돈들

            for i in slotRank:
                rate, number = slotRank[i]
                if _result in number:
                    rank = i
                    money = rate*betting
                    break
            
            myMoney += money
            myBetting += betting
            myReward += money

            con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
            cur = con.cursor()

            cur.execute("SELECT total_Betting FROM Slot_Info")
            total_Betting = cur.fetchone()[0]
            if rank == 0 and total_Betting >= 10:
                userBetting = total_Betting // 2
                myMoney += userBetting
                total_Betting = total_Betting - userBetting
            
            if rank is None:
                total_Betting += betting
                resultText = f'아무것도 해당하지 않았습니다...'
            else:
                resultText = f'{rank+1}등 당첨! {printN(money)}원이 지급됩니다!'
            
            cur.execute("UPDATE 'User_Info' SET user_Money = ?, slot_Betting = ?, slot_Reward = ? WHERE user_ID = ?", (myMoney, myBetting, myReward, id))
            cur.execute("UPDATE 'Slot_Info' SET total_Betting = ?", (total_Betting,))
            con.close() #db 종료


            embed = discord.Embed(title = f':slot_machine: {gameName3} 결과', description = f'{message.author.mention} {resultText}', color = 0x324260)
            embed.set_footer(text = f"{message.author.display_name} | {gameName3}", icon_url = message.author.avatar_url)
            embed.add_field(name = f'배팅금액', value = f'{printN(betting)}원')
            if rank is None:
                rewardText = f'0원'
            elif rank == 0:
                rewardText = f'{printN(money)}원 `(+{printN(userBetting)}원)`'
            else:
                rewardText = f'{printN(money)}원'
            embed.add_field(name = f'당첨금액', value = f'{rewardText}')
            embed.add_field(name = f'보유재산', value = f':money_with_wings:{printN(myMoney)}원')
            
            await message.channel.send(embed = embed)

        except:
            print("슬롯머신에러")
            pass

# embed.add_field(name=f'1등 (배팅금액×300배)', value=f'{slotList[0]}{slotList[0]}{slotList[0]}')
# embed.add_field(name=f'2등 (배팅금액×50배)', value=f'{slotList[1]}{slotList[1]}{slotList[1]}')
# embed.add_field(name=f'3등 (배팅금액×20배)', value=f'{slotList[2]}{slotList[2]}{slotList[2]}')
# embed.add_field(name=f'4등 (배팅금액×12배)', value=f'{slotList[5]}{slotList[3]}{slotList[1]}')
# embed.add_field(name=f'5등 (배팅금액×11배)', value=f'{slotList[3]}{slotList[3]}{slotList[3]}')
# embed.add_field(name=f'6등 (배팅금액×10배)', value=f'{slotList[4]}{slotList[4]}{slotList[4]}')
# embed.add_field(name=f'7등 (배팅금액×9배)', value=f'{slotList[5]}{slotList[5]}{slotList[5]}')