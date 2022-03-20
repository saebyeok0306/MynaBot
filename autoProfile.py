import discord
import asyncio
from datetime import datetime


user_avatar = [0,0,0,0,0,0,0,0,0,0] #아바타 url 주소가 바뀌면 프로필이미지를 바꾼걸로 간주
user_ID     = []

async def autoProfile(server, time):
    global user_avatar
    #타이머
    for id in range(len(user_ID)):
        try:
            user = await server.fetch_member(user_ID[id])
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