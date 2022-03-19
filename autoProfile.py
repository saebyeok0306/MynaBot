import discord
import asyncio
from datetime import datetime


user_avatar = [0,0,0,0,0,0,0,0,0,0] #아바타 url 주소가 바뀌면 프로필이미지를 바꾼걸로 간주
user_ID     = [
    864428155506655273, #카구팔
    298824090171736074, #마스님
    317960020912504832, #믹넛님
    383483844218585108, #갈대
    501303312029712384, #노마님
    278461838067236864, #하늘님
    382906504694595585, #하이루님
    434348010974216203, #뮤님
    351002869685551119 #로체님
]

async def autoProfile(g, time):
    global user_avatar
    #타이머
    for id in range(len(user_ID)):
        try:
            user = await g.fetch_member(user_ID[id])
            if(user_avatar[id] == 0):
                user_avatar[id] = user.avatar_url
            elif(user_avatar[id] != user.avatar_url):
                print(user.name + "님께서 프로필을 변경했습니다.")
                user_avatar[id] = user.avatar_url
                ch = user.guild.get_channel(764367163464351786)
                await ch.send("=avatar "+user.mention + " 카짓 해버리기~")
                embed = discord.Embed(title=user, description='Direct Link')
                embed.set_image(url = user.avatar_url)
                await ch.send(embed=embed)
        except:
            print("오류id ->", user_ID[id])

# async def autoProfile(client):
#     global user_avatar
#     #타이머
#     now = datetime.now()
#     guildList = client.guilds
#     for g in guildList:
#         if(g.id == 631471244088311840): #내 디코서버일 때
#             for id in range(len(user_ID)):
#                 user = await g.fetch_member(user_ID[id])
#                 if(user_avatar[id] == 0):
#                     user_avatar[id] = user.avatar_url
#                 elif(user_avatar[id] != user.avatar_url):
#                     print(user.name + "님께서 프로필을 변경했습니다.")
#                     user_avatar[id] = user.avatar_url
#                     ch = user.guild.get_channel(764367163464351786)
#                     await ch.send("=avatar "+user.mention + " 카짓 해버리기~")
#                     embed = discord.Embed(title=user, description='Direct Link')
#                     embed.set_image(url = user.avatar_url)
#                     await ch.send(embed=embed)