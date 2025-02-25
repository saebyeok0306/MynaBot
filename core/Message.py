import random
from datetime import datetime

import discord
from discord.ext import commands
from sqlalchemy import and_

from utils.database.Database import SessionContext
from utils.database.model.exp import Exp


class Message(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')

        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot: return None

        await self.add_emoji(message)
        if self.bot.BCFlag:
            await self.버엄령(message)

        today = datetime.today().strftime('%Y-%m-%d')

        with SessionContext() as session:
            user_exp = session.query(Exp).filter(and_(Exp.id == message.author.id, Exp.guild_id == message.guild.id)).first()
            if user_exp is None:
                user_exp = Exp(message.author.id, message.guild.id)
            user_exp.chat_count += 1
            if user_exp.today_str != today:
                user_exp.today_str = today
                user_exp.today_exp += 1
            session.add(user_exp)
            session.commit()

        # await bot.process_commands(message)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user.bot: return None

        if self.bot.BCFlag:
            await reaction.clear()

    async def add_emoji(self, message):
        if message.guild.id not in [631471244088311840]: return

        text = message.content
        if random.randint(1, 10) <= 2:
            if text.count('ㅋ') >= 2:
                emoji = ['<a:jerry:762198111119605770>','<:dog1:647472178287214593>','<a:SpongeBob3:762542652381069352>','<a:SpongeBob2:762541940914782260>', '<:cat2:671208661997060096>','<:troll2:733561463930749007>','<:troll3:733561496076025866>', '<:cat3:750001125477974106>']
                await message.add_reaction(random.choice(emoji))
            
            elif '캬루' in text:
                emoji = ['<:jjag2:740050586828931164>', '<:cat2:745897614708441168>', '<:cat3:750001125477974106>', '<:cat4:750001279014797342>', '<:cat5:750001356709822504>', '<:cat7:750324958554751106>', '<:cat8:753133462642229248>', '<:cat9:753132725107556442>', '<:jjag:739874314324672532>', '<a:jjag3:740055407103574097>']
                await message.add_reaction(random.choice(emoji))
            
        if '몰?루' == text or '몰!루' == text:
            await message.add_reaction('<a:molu:968521092476051526>')
        elif '아?루' == text or '아!루' == text:
            await message.add_reaction('<a:aru:968710530376282212>')

    async def 버엄령(self, message: discord.Message):
        if message.guild.id != 631471244088311840: return
        import re

        pattern = r'<:[^:]+:\d+>|<a:[^:]+:\d+>'
        chk = False
        for sid in self.bot.BC_LIST:
            if message.author.id == int(sid):
                chk = True
                break
        if chk:
            if len(message.content) == 0 or len(re.findall(pattern, message.content)) > 0:
                await message.delete()

async def setup(bot):
    await bot.add_cog(Message(bot))
