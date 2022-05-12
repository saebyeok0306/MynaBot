import sqlite3, discord, asyncio, random
import data.Functions as fun
from discord.ext import commands, tasks

gameName3 = '슬롯머신'

# 럭키세븐, 도지, 냥, 페페, 제리, 머쓱
'''
slotEmoji = '<a:slot:966191956407513108>'
slotList  = ['<a:lucky_seven:961840921144598548>', '<a:thuglifedog:765463003054997515>', '<:NYANG:970928229647015966>', '<:Pepegood:868064047969497129>', '<a:jerry:762198111119605770>', '<:em:672068659295813634>']
'''
slotEmoji = '<a:slot2:974217920412520468>'
slotList = ['<:L_:974218016826990632>','<:T_:974218016692781096>','<:S_:974218016717942824>','<:F_:974218016663437352>','<:R_:974218016772468766>','<:H_:974218016374009899>']
slotRand  = [10, 10, 11, 11, 12, 12]
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
slotPlay  = []

class SlotmachineGame(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def 슬롯(self, ctx, *input):
        if(ctx.channel.id in fun.getBotChannel(ctx)):
            # try:
            id = ctx.author.id
            check = fun.game_check(id)
            if check == 0:
                embed = discord.Embed(title = f':exclamation: {gameName3} 미가입', description = f'{ctx.author.mention} {gameName3} 게임에 가입하셔야 이용이 가능합니다. (!회원가입)', color = 0xff0000)
                embed.set_footer(text = f"{ctx.author.display_name} | {gameName3}", icon_url = ctx.author.avatar_url)
                await ctx.channel.send(embed = embed)
                return 0

            fun.setUserName(id, ctx)

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

                embed = discord.Embed(title = f':video_game: {gameName3} 도움말', description = f'{ctx.author.mention} {gameName3} 의 명령어입니다!', color = 0x324260)
                embed.set_footer(text = f"{ctx.author.display_name} | {gameName3}", icon_url = ctx.author.avatar_url)
                embed.add_field(name=f'1등 (배팅금액×300배 + {fun.printN(total_Betting)}원)', value=f'{slotList[0]}{slotList[0]}{slotList[0]}\n추가로 슬롯머신에 담긴 배팅금액의 절반도 지급됩니다.')
                embed.add_field(name=f'2등 (배팅금액×50배)', value=f'{slotList[1]}{slotList[1]}{slotList[1]}')
                embed.add_field(name=f'3등 (배팅금액×20배)', value=f'{slotList[2]}{slotList[2]}{slotList[2]}')
                embed.add_field(name=f'4등 (배팅금액×12배)', value=f'{slotList[5]}{slotList[3]}{slotList[1]} or\n{slotList[4]}{slotList[2]}{slotList[0]}')
                embed.add_field(name=f'5등 (배팅금액×11배)', value=f'{slotList[3]}{slotList[3]}{slotList[3]}')
                embed.add_field(name=f'6등 (배팅금액×10배)', value=f'{slotList[4]}{slotList[4]}{slotList[4]}')
                embed.add_field(name=f'7등 (배팅금액×9배)', value=f'{slotList[5]}{slotList[5]}{slotList[5]}')
                embed.add_field(name=f'8등 (배팅금액×3배)', value=f'{slotList[3]},{slotList[4]},{slotList[5]}\n위치 상관없이 1개씩 나온 경우')
                embed.add_field(name=f'!슬롯 [배팅금액]', value=f'슬롯머신을 돌립니다.')
                await ctx.channel.send(embed = embed)
                return 0

            global slotPlay

            if id in slotPlay: return 0
            slotPlay.append(id)
            betting = 0
            try:
                betting = int(input[0])
                
            except:
                embed = discord.Embed(title = f':exclamation: {gameName3} 오류', description = f'{ctx.author.mention} 배팅하실 금액을 입력하셔야 합니다.\n!슬롯 [배팅금액]', color = 0xff0000)
                embed.set_footer(text = f"{ctx.author.display_name} | {gameName3}", icon_url = ctx.author.avatar_url)
                await ctx.channel.send(embed = embed)
                return 0

            con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
            cur = con.cursor()
            cur.execute("SELECT user_Money, slot_Betting, slot_Reward FROM User_Info WHERE user_ID = ?", (id,))
            userInfo = cur.fetchone()
            myMoney,myBetting,myReward = userInfo[0],userInfo[1],userInfo[2]
            con.close() #db 종료

            if myMoney < betting:
                embed = discord.Embed(title = f':exclamation: {gameName3} 금액부족', description = f'{ctx.author.mention} 보유하고 계시는 돈이 부족합니다.\n보유재산 `{fun.printN(myMoney)}원` :money_with_wings:', color = 0xff0000)
                embed.set_footer(text = f"{ctx.author.display_name} | {gameName3}", icon_url = ctx.author.avatar_url)
                await ctx.channel.send(embed = embed)
                return 0
            myMoney -= betting
            con = sqlite3.connect(r'data/DiscordDB.db', isolation_level = None) #db 접속
            cur = con.cursor()
            cur.execute("UPDATE 'User_Info' SET user_Money = ? WHERE user_ID = ?", (myMoney, id))
            con.close() #db 종료


            embed = discord.Embed(title = f':slot_machine: {ctx.author.display_name}님의 슬롯머신', description = f'슬롯머신을 돌립니다!', color = 0x324260)
            embed.set_footer(text = f"{ctx.author.display_name} | {gameName3}", icon_url = ctx.author.avatar_url)
            embed.add_field(name = f'배팅금액', value = f'{fun.printN(betting)}원')
            msg1 = await ctx.channel.send(embed = embed)
            msg2 = await ctx.channel.send(f'{slotEmoji}{slotEmoji}{slotEmoji}')
            
            await asyncio.sleep(1)

            open = 0
            result = {id : 9 for id in range(3)}

            async def openSlot(msg2, index):
                rand = random.randint(0,sum(slotRand)-1)
                rand2 = 0
                for r in range(6):
                    rand2 += slotRand[r]
                    if rand <= rand2:
                        result[index] = r
                        break
                text = ''
                for i in range(3):
                    if result[i] == 9:
                        text += f'{slotEmoji}'
                    else:
                        text += f'{slotList[result[i]]}' 
                await msg2.edit(content = text)
            
            while open < 3:
                await asyncio.sleep(1)
                await openSlot(msg2, open)
                open += 1

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
                resultText = f'{rank+1}등 당첨! {fun.printN(money)}원이 지급됩니다!'
            
            cur.execute("UPDATE 'User_Info' SET user_Money = ?, slot_Betting = ?, slot_Reward = ? WHERE user_ID = ?", (myMoney, myBetting, myReward, id))
            cur.execute("UPDATE 'Slot_Info' SET total_Betting = ?", (total_Betting,))
            con.close() #db 종료


            embed = discord.Embed(title = f':slot_machine: {ctx.author.display_name}님의 슬롯머신', description = f'슬롯머신을 돌립니다!\n{resultText}', color = 0x324260)
            embed.set_footer(text = f"{ctx.author.display_name} | {gameName3}", icon_url = ctx.author.avatar_url)
            embed.add_field(name = f'배팅금액', value = f'{fun.printN(betting)}원')
            if rank is None:
                rewardText = f'0원'
            elif rank == 0:
                rewardText = f'{fun.printN(money)}원 `(+{fun.printN(userBetting)}원)`'
            else:
                rewardText = f'{fun.printN(money)}원'
            embed.add_field(name = f'당첨금액', value = f'{rewardText}')
            embed.add_field(name = f'보유재산', value = f':money_with_wings:{fun.printN(myMoney)}원')
            
            await msg1.edit(embed = embed)
            slotPlay.remove(id)

            # except BaseException as e:
            #     print(f'슬롯머신게임 {e}')
            #     pass

def setup(bot):
    bot.add_cog(SlotmachineGame(bot))

# embed.add_field(name=f'1등 (배팅금액×300배)', value=f'{slotList[0]}{slotList[0]}{slotList[0]}')
# embed.add_field(name=f'2등 (배팅금액×50배)', value=f'{slotList[1]}{slotList[1]}{slotList[1]}')
# embed.add_field(name=f'3등 (배팅금액×20배)', value=f'{slotList[2]}{slotList[2]}{slotList[2]}')
# embed.add_field(name=f'4등 (배팅금액×12배)', value=f'{slotList[5]}{slotList[3]}{slotList[1]}')
# embed.add_field(name=f'5등 (배팅금액×11배)', value=f'{slotList[3]}{slotList[3]}{slotList[3]}')
# embed.add_field(name=f'6등 (배팅금액×10배)', value=f'{slotList[4]}{slotList[4]}{slotList[4]}')
# embed.add_field(name=f'7등 (배팅금액×9배)', value=f'{slotList[5]}{slotList[5]}{slotList[5]}')