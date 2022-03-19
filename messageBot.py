import discord
import asyncio
import random

async def chatUserMessage(message):
    if message.content == '!마크':
        embed=discord.Embed(color=0xB22222, title="노마님의 서버", description="`NightNoma`님의 1.17.1 모드서버", timestamp=message.created_at)
        embed.set_thumbnail(url=message.author.avatar_url)
        embed.add_field(name = '서버주소', value = '힐링.시오.서버.한국')
        embed.add_field(name = '서버문의', value = '@NightNoma 님에게 연락하세요!')
        embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
        await message.channel.send(embed=embed)
    if message.content == '!도움말':
        embed=discord.Embed(color=0xB22222, title="도움말:", description="마이나에게 있는 명령어들을 알려드려요. By.갈대", timestamp=message.created_at)
        embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
        embed.add_field(name = '!가위 !바위 !보', value = '마이나와 가위바위보를 할 수 있어요.')
        embed.add_field(name = '!주사위', value = '주사위를 굴립니다. 범위:1~100')
        embed.add_field(name = '!마크', value = '디코방에서 운영되고 있는 서버주소를 알려줘요!')
        # embed.add_field(name = '!회원가입', value = '갈대가 제작한 게임서비스를 이용하려면, 가입이 필요해요.')
        # embed.add_field(name = '!회원탈퇴', value = '회원가입이 있으면 회원탈퇴도 있는법.')
        # embed.add_field(name = '!코인 도움말', value = '갈대가 직접 제작한 `코인게임`!\n명령어를 확인할 수 있어요.')
        await message.channel.send(embed=embed)

    #가위 바위 보
    if message.content == "!가위":
        str1 = ['가위','바위','보']
        r = random.choice(str1)
        if r == '가위':
            await message.channel.send('가위! 비겼네요!')
        elif r == '바위':
            await message.channel.send('바위! 마이나가 이겼어요!')
        elif r == '보':
            await message.channel.send('보... 마이나가 졌어요.')

    if message.content == "!바위":
        str1 = ['가위','바위','보']
        r = random.choice(str1)
        if r == '바위':
            await message.channel.send('바위! 비겼네요!')
        elif r == '보':
            await message.channel.send('보! 마이나가 이겼어요!')
        elif r == '가위':
            await message.channel.send('가위... 마이나가 졌어요.')

    if message.content == "!보":
        str1 = ['가위','바위','보']
        r = random.choice(str1)
        if r == '보':
            await message.channel.send('보! 비겼네요!')
        elif r == '가위':
            await message.channel.send('가위! 마이나가 이겼어요!')
        elif r == '바위':
            await message.channel.send('바위... 마이나가 졌어요.')
    
    #주사위
    if message.content == "!주사위":
        str1 = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100]
        r = random.choice(str1)
        result = ""
        result = result + "주사위를 굴립니다...\n" + str(r) + "이(가) 나왔습니다!"
        await message.channel.send(result)
    
    # if message.author.id == 317960020912504832:
    #     str1 = ['이건... 믹넛쿤?', '응 아니야~', '이 멘트는 랜덤입니다.', '슬슬 즐기고 있는 믹넛님이 보이는군요.', 'ㅋㅋㅋㅋ', '이 봇은 무료로 시비를 털어줍니다.', '아 그거 그렇게 하는거 아닌데..', '논리적으로 있을 수 없는 일입니다.']
    #     r = random.choice(str1)
    #     msg = await message.channel.send(r)
    #     await asyncio.sleep(1)
    #     await msg.delete()



# if message.content == "!실검":
#     #메시지가 실검이라면
#     url = "https://m.search.naver.com/search.naver?query=%EC%8B%A4%EA%B2%80"
#     #url 선언
#     html = urlopen(url)
#     parse = BeautifulSoup(html, "html.parser")
#     #html 가져오기
#     result = ""
#     #result 선언
#     tags = parse.find_all("span", {"class" : "tit _keyword"})
#     #이름이 span, class 속성이 tit _keyword 인 태그들 가져오기
#     for i, e in enumerate(tags):
#         result = result + (str(i+1))+"위|"+e.text+"\n"
#     #for문을 이용해 정리
#     await message.channel.send(result)
#     #답하기