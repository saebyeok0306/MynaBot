import sqlite3
import discord
import asyncio
import datetime
import random
import re
import math

# 강화하는 검에 대한 DB
# sword_userID, sword_prefixID, sword_suffixID, sword_Name, sword_Upgrade, sword_Atk, sword_prefixAtk, sword_SuffixAtk

# 무기공격력 공식
# floor(preAtk^EXTRA + n^UPGRADE + UPGRADE)
# n = 1.12
# EXTRA = 1+random.randint(10,99)/100000

# 강화비용 공식
# floor(log(baseAtk, n) - 200)
# n = 1.01


# 게임요소
# 무기이름 가챠 (간지나는 무기를 뽑아야하지)
# 기본공격력 연마
# 무기 강화 (장기백)
# 무기 인챈트 (접두, 접미)
# 보스몬스터 사냥(인챈트 획득)


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

gameName2 = '강화게임'
weaponName = ["롱소드", "롱해머", "듀얼소드", "듀얼스피어", "스태프", "배틀사이드", "블래스터", "활", "크로스건", "카타마르", "그레이트소드", "배틀글레이브", "팬텀대거", "바스타드소드", "마나리볼버", "호미", "낫", "삽", "젓가락", "숟가락", "포크", "단검", "여의봉", "빨대", "수리검", "레이피어", "트라이던트", "카타나", "너클", "채찍"]

failText    = [
    '어이쿠, 손이 미끄러졌군.',
    '이런, 이거 미안해서 어쩌나.',
    '미안하군, 그래도 나름 유명한 대장장이일세.',
    '그래도 옆동네처럼 무색큐브가 나오진 않는다네.',
    '허허, 이거 미안해서 어쩌나.',
    '내 그만 손이 미끄러지고 말았구려.',
]
we_N = 1.12
up_N = 1.001
up_V = 100 #비용value
pe_N = 1.1


def newWeapon():
    swordName = random.choice(weaponName)
    swordAtk = random.randint(20,40)
    minAtk = swordAtk-random.randint(1,int(swordAtk/5))
    EXTRA = 1+random.randint(10,99)/100000
    upCost = int(round(swordAtk+(math.log(swordAtk**3, up_N)),0))
    percent = round(math.log(101,pe_N),0)
    return swordName, swordAtk, minAtk, EXTRA, upCost, percent

def setUserName(id, msg):
    con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
    cur = con.cursor()
    cur.execute("SELECT user_Name FROM User_Info WHERE user_ID = ?", (id,))
    userName = cur.fetchone()
    # 저장된 닉네임과 일치하지 않는 경우
    if userName[0] != msg.author.display_name:
        cur.execute("UPDATE 'User_Info' SET user_Name = ?WHERE user_ID = ? ", (msg.author.display_name, id,))
    con.close() #db 종료

async def swordMessage(message, bot, *input):
    if(message.channel.id == 953919871522046008): #게임채팅채널에서 채팅을 친경우
        # try:
            id = message.author.id
            check = game_check(id)
            if check == 0:
                embed = discord.Embed(title = f':exclamation: {gameName2} 미가입', description = f'{message.author.mention} {gameName2} 에 가입하셔야 이용이 가능합니다. (!회원가입)', color = 0xff0000)
                embed.set_footer(text = f"{message.author.display_name} | {gameName2}", icon_url = message.author.avatar_url)
                await message.channel.send(embed = embed)
                return 0
            setUserName(id, message)
            input = input[0]
            if(input[0] == '도움말'):
                embed = discord.Embed(title = f':video_game: {gameName2} 도움말', description = f'{message.author.mention} {gameName2} 의 명령어입니다!', color = 0x324260)
                embed.add_field(name = f'!강화 무기소환', value = f'무기를 소환합니다. 1000원이 필요해요.')
                embed.set_footer(text = f"{message.author.display_name} | {gameName2}", icon_url = message.author.avatar_url)
                await message.channel.send(embed = embed)
            elif(input[0] == '내정보'):
                con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                cur = con.cursor()
                cur.execute("SELECT user_Name, user_Money FROM User_Info WHERE user_ID = ?", (id,))
                myUser = cur.fetchone()
                cur.execute("SELECT sword_FullName, sword_Upgrade, sword_MinAtk, sword_MaxAtk, sword_PrefixAtk, sword_SuffixAtk, sword_Percent, sword_EXTRA, sword_UpCost, sword_Count FROM Sword_Info WHERE sword_UserID = ?", (id,))
                swordInfo = cur.fetchone()
                embed = discord.Embed(title = f'{message.author.display_name}님의 정보창', description = f'{gameName2} 에서의 본인 정보입니다.\n현금 재산은 모든 게임에서 공유됩니다.', color = 0xffc0cb)
                embed.set_thumbnail(url=message.author.avatar_url)
                embed.add_field(name = f'무기이름', value = f'{swordInfo[0]}+{swordInfo[1]}')
                embed.add_field(name = f'공격력', value = f'`{swordInfo[2]}~{swordInfo[3]} Atk`')
                embed.add_field(name = f'현재확률', value = f'{swordInfo[6]}%')
                embed.add_field(name = f'현재비용', value = f'`{printN(swordInfo[8])}원`')
                embed.add_field(name = f'현금재산', value = f'`{printN(myUser[1])}원`')
                await message.channel.send(embed = embed)

            elif(input[0] == '무기소환'):
                con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                cur = con.cursor()
                cur.execute("SELECT user_Name, user_Money FROM User_Info WHERE user_ID = ?", (id,))
                myUser = cur.fetchone()
                myMoney = myUser[1]
                if myMoney >= 1000:
                    cur.execute("SELECT sword_FullName, sword_Upgrade, sword_MinAtk, sword_MaxAtk FROM Sword_Info WHERE sword_UserID = ?", (id,))
                    swordInfo = cur.fetchone()
                    if not swordInfo: #생성한 무기가 없음
                        myMoney -= 1000
                        cur.execute("UPDATE 'User_Info' SET user_Money = ? WHERE user_ID = ?", (myMoney, id))
                        swordName, swordAtk, minAtk, EXTRA, upCost, percent = newWeapon()
                        cur.execute("INSERT INTO Sword_Info VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, message.author.display_name, 0, 0, swordName, swordName, 0, minAtk, swordAtk, 0, 0, percent, EXTRA, upCost, 0))
                        embed = discord.Embed(title = f':trident: {gameName2} 무기소환', description = f'{message.author.mention}님께서 새로운 무기를 소환했습니다! `-1000원`', color = 0x324260)
                        embed.set_thumbnail(url=message.author.avatar_url)
                        embed.add_field(name = f'무기정보', value = f'이름 `{swordName}+0`\n공격력 `{minAtk}~{swordAtk} Atk`')
                        embed.add_field(name = f'보유재산', value = f'`{printN(myMoney)}원`')
                        embed.set_footer(text = f"{message.author.display_name} | {gameName2}", icon_url = message.author.avatar_url)
                        await message.channel.send(embed = embed)
                        
                    else: #생성한 무기가 이미 존재함
                        embed = discord.Embed(title = f':trident: {gameName2} 무기소환', description = f'{message.author.mention} 이미 무기가 존재합니다.\n기존 무기를 지우고 새롭게 소환하시려면, 반응아이콘을 선택하세요.', color = 0x324260)
                        embed.set_footer(text = f"{message.author.display_name} | {gameName2}", icon_url = message.author.avatar_url)
                        msg = await message.channel.send(embed = embed)
                        await msg.add_reaction('🔴')
                        await msg.add_reaction('❌')
                        try:
                            def check(reaction, user):
                                return str(reaction) in ['🔴', '❌'] and \
                                user == message.author and reaction.message.id == msg.id

                            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
                            if str(reaction) == '🔴':
                                myMoney -= 1000
                                cur.execute("UPDATE 'User_Info' SET user_Money = ? WHERE user_ID = ?", (myMoney, id))
                                swordName, swordAtk, minAtk, EXTRA, upCost, percent = newWeapon()
                                cur.execute("DELETE FROM 'Sword_Info' WHERE sword_UserID = ?", (id,))
                                cur.execute("INSERT INTO Sword_Info VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, message.author.display_name, 0, 0, swordName, swordName, 0, minAtk, swordAtk, 0, 0, percent, EXTRA, upCost, 0))
                                embed = discord.Embed(title = f':trident: {gameName2} 무기재소환', description = f'{message.author.mention}님께서 새로운 무기를 소환했습니다! `-1000원`', color = 0x324260)
                                embed.set_thumbnail(url=message.author.avatar_url)
                                embed.add_field(name = f'이전무기', value = f'이름 `{swordInfo[0]}+{swordInfo[1]}`\n공격력 `{swordInfo[2]}~{swordInfo[3]} Atk`')
                                embed.add_field(name = f'신규무기', value = f'이름 `{swordName}+0`\n공격력 `{minAtk}~{swordAtk} Atk`')
                                embed.add_field(name = f'보유재산', value = f'`{printN(myMoney)}원`')
                                embed.set_footer(text = f"{message.author.display_name} | {gameName2}", icon_url = message.author.avatar_url)
                                await msg.clear_reactions()
                                await msg.edit(embed=embed)
                            elif str(reaction) == '❌':
                                embed = discord.Embed(title = f':trident: {gameName2} 무기소환', description = f'{message.author.mention} 무기소환을 취소합니다.', color = 0x324260)
                                await msg.clear_reactions()
                                await msg.add_reaction('❌')
                                await msg.edit(embed=embed)
                        except asyncio.TimeoutError:
                            embed = discord.Embed(title = f':trident: {gameName2} 무기소환', description = f'{message.author.mention} 시간초과로 무기소환을 취소합니다.', color = 0x324260)
                            await msg.clear_reactions()
                            await msg.add_reaction('❌')
                            await msg.edit(embed=embed)
                else:
                    embed = discord.Embed(title = f':exclamation: {gameName2} 소환실패', description = f'{message.author.mention} 무기를 소환하려면 1000원이 필요합니다.\n보유재산 `{printN(myMoney)}원`', color = 0xff0000)
                    embed.set_footer(text = f"{message.author.display_name} | {gameName2}", icon_url = message.author.avatar_url)
                    await message.channel.send(embed = embed)
                con.close() #db 종료
            
            if(input[0] == '무기'):
                con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
                cur = con.cursor()
                cur.execute("SELECT user_Name, user_Money FROM User_Info WHERE user_ID = ?", (id,))
                myUser = cur.fetchone()
                myMoney = myUser[1]
                cur.execute("SELECT sword_FullName, sword_Upgrade, sword_MinAtk, sword_MaxAtk, sword_PrefixAtk, sword_SuffixAtk, sword_Percent, sword_EXTRA, sword_UpCost, sword_Count FROM Sword_Info WHERE sword_UserID = ?", (id,))
                swordInfo = cur.fetchone()
                if not swordInfo: #생성한 무기가 없음
                    embed = discord.Embed(title = f':exclamation: 강화실패', description = f'{message.author.mention} 소유하고 있는 무기가 없습니다!\n`!강화 무기소환`을 통해, 무기를 소환해보세요!', color = 0xff0000)
                    embed.set_footer(text = f"{message.author.display_name} | {gameName2}", icon_url = message.author.avatar_url)
                    await message.channel.send(embed = embed)
                else: #무기가 있을 때
                    sword_FullName  = swordInfo[0]
                    sword_Upgrade   = swordInfo[1]
                    sword_MinAtk    = swordInfo[2]
                    sword_MaxAtk    = swordInfo[3]
                    sword_PrefixAtk = swordInfo[4]
                    sword_SuffixAtk = swordInfo[5]
                    sword_Percent   = swordInfo[6]
                    sword_EXTRA     = swordInfo[7]
                    sword_UpCost    = swordInfo[8]
                    sword_Count     = swordInfo[9]
                    enchantAtk      = sword_PrefixAtk+sword_SuffixAtk
                    if myMoney >= sword_UpCost:
                        if sword_Upgrade < 100:
                            myMoney -= sword_UpCost
                            cur.execute("UPDATE 'User_Info' SET user_Money = ? WHERE user_ID = ?", (myMoney, id))
                            upRand = random.randint(0,99)
                            if upRand < sword_Percent: #성공
                                sword_Upgrade += 1
                                newAtk = int(round((sword_MaxAtk**sword_EXTRA + we_N**sword_Upgrade + sword_Upgrade),0))
                                increaeAtk = newAtk-sword_MaxAtk
                                sword_MaxAtk = newAtk
                                sword_MinAtk = sword_MaxAtk-random.randint(1,int(newAtk/5)) #sword_MinAtk = sword_MinAtk + increaeAtk
                                newCost = int(round(newAtk+(math.log(newAtk**3, up_N)),0))
                                newPercent = round(math.log(101-sword_Upgrade, pe_N),0)
                                newEXTRA = 1+random.randint(10,99)/100000
                                cur.execute("UPDATE 'Sword_Info' SET sword_Upgrade = ?, sword_MinAtk = ?, sword_MaxAtk = ?, sword_Percent = ?, sword_EXTRA = ?, sword_UpCost = ?, sword_Count = ? WHERE sword_UserID = ?", (sword_Upgrade, sword_MinAtk, sword_MaxAtk, newPercent, newEXTRA, newCost, 0, id))
                                embed = discord.Embed(title = f':hammer_pick: {message.author.display_name}님의 {sword_FullName}+{sword_Upgrade} 강화성공', description = f'강화에 성공했습니다!', color = 0x324260)
                                embed.set_thumbnail(url='https://i.imgur.com/FgubKQd.png')
                                embed.add_field(name = f'{sword_FullName}+{sword_Upgrade}', value = f'공격력 {sword_MinAtk+enchantAtk}~{sword_MaxAtk+enchantAtk} (+{increaeAtk})')
                                embed.add_field(name = f'강화확률', value = f'{sword_Percent}% 확률로 성공!')
                                embed.add_field(name = f'다음강화', value = f'성공률 {newPercent}%')
                                embed.add_field(name = f'다음비용', value = f'비용 {printN(newCost)}원')
                                embed.add_field(name = f'보유재산', value = f'{printN(myMoney)}원')
                                embed.set_footer(text = f"{message.author.display_name} | {gameName2}", icon_url = message.author.avatar_url)
                                await message.channel.send(embed = embed)
                            else: #실패
                                textR = random.randint(0,len(failText));
                                tempR = round((random.randint(1,9))/10, 1)
                                newPercent = round(sword_Percent+tempR, 1) if (sword_Percent+tempR <= 100.0) else 100
                                newCost = sword_UpCost + int(round((math.log(sword_MaxAtk, up_N)),0))
                                cur.execute("UPDATE 'Sword_Info' SET sword_Percent = ?, sword_UpCost = ? WHERE sword_UserID = ?", (newPercent, newCost, id))
                                embed = discord.Embed(title = f':hammer_pick: {message.author.display_name}님의 {sword_FullName}+{sword_Upgrade} 강화실패', description = f'{failText[textR]}', color = 0x324260)
                                embed.set_thumbnail(url='https://i.imgur.com/tj2xDpe.png')
                                embed.add_field(name = f'강화확률', value = f'{newPercent}% 확률 (+{round(newPercent-sword_Percent, 1)})')
                                embed.add_field(name = f'강화비용', value = f'{printN(newCost)}원 (+{printN(newCost-sword_UpCost)})')
                                embed.add_field(name = f'보유재산', value = f'{printN(myMoney)}원')
                                embed.set_footer(text = f"{message.author.display_name} | {gameName2}", icon_url = message.author.avatar_url)
                                await message.channel.send(embed = embed)
                        else:
                            embed = discord.Embed(title = f':exclamation: {message.author.display_name}님의 {sword_FullName}+{sword_Upgrade} 강화실패', description = f'{message.author.mention} 가지고 계신 무기는 더이상 강화할 수 없습니다!', color = 0xff0000)
                            embed.set_footer(text = f"{message.author.display_name} | {gameName2}", icon_url = message.author.avatar_url)
                            await message.channel.send(embed = embed)
                    else:
                        embed = discord.Embed(title = f':exclamation: {message.author.display_name}님의{sword_FullName}+{sword_Upgrade} 강화실패', description = f'{message.author.mention} 무기를 강화하려면 {printN(sword_UpCost)}원이 필요합니다.\n보유재산 `{printN(myMoney)}원`', color = 0xff0000)
                        embed.set_footer(text = f"{message.author.display_name} | {gameName2}", icon_url = message.author.avatar_url)
                        await message.channel.send(embed = embed)
                con.close() #db 종료
            
            if(input[0] == '전투'):
                embed = discord.Embed(title = f':video_game: 전투로그다옹', description = f'{message.author.mention} 전투 시작!', color = 0x324260)
                embed.set_footer(text = f"{message.author.display_name} | {gameName2}", icon_url = message.author.avatar_url)
                msg = await message.channel.send(embed = embed)
                turn        = 0
                bossTimer   = 60
                attack      = 0
                curHP       = 5000000
                bossHP      = 5000000
                while bossTimer:
                    if turn == 0:
                        attack += 1000
                        embed.add_field(name = f'{message.author.display_name}의 턴', value = f'갈대의 무기로 1000데미지!')
                        await msg.edit(embed = embed)
                        turn += 1
                    else:
                        curHP -= attack
                        embed.add_field(name = f'보스의 턴', value = f'보스는 {attack}데미지를 받았습니다!\n보스체력 : `{printN(curHP)}/{printN(bossHP)}`')
                        await msg.edit(embed = embed)
                        attack = 0
                        turn = 0
                    await asyncio.sleep(1)
                    if turn == 0: embed.clear_fields()
                    bossTimer -= 1

        # except:
        #     print("강화에러")
        #     pass