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
            
        if '몰?루' == text or '몰!루' == text:
            await message.add_reaction('<a:molu:968521092476051526>')
        elif '아?루' == text or '아!루' == text:
            await message.add_reaction('<a:aru:968710530376282212>')
        elif text.endswith("내놔") or text.endswith("줘"):
            await message.add_reaction('<:giveme:1093503999824634019>')
        elif text in ['돔황챠', '도망쳐']:
            await message.add_reaction('<:Run:1031451662814027817>')

async def setup(bot):
    await bot.add_cog(Message(bot))
