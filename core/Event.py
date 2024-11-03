import datetime
import os, importlib

import discord
from discord.ext import commands, tasks
from sqlalchemy import and_

import utils.Logs as logs
import utils.Utility as util
from utils.Role import *
from utils.database.Database import SessionContext
from utils.database.model.status import Status
from utils.database.model.users import Users


class Event(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.core_list = ['Administrator', 'Command', 'Profile']

        if util.is_test_version():
            # Test Version
            self.core_list.extend([
                'VoiceClient', 'Youtube', 'ClovaX', 'ChatGPT',
                'Authority', 'Message', 'RoleIcon'
            ])
        else:
            # Deploy Version
            self.core_list.extend([
                'ColorName', 'Papago', 'ChatGPT', 'Message',
                'VoiceClient', 'Youtube', 'Authority',
                'ClovaX', 'RoleIcon'
            ])

    @commands.Cog.listener()
    async def on_ready(self):
        print('로그인되었습니다!')
        print(self.bot.user.name)
        print(self.bot.user.id)
        print('==============================')

        now = datetime.datetime.now()
        now_time = f"{now.year}.{now.month:02}.{now.day:02} {now.hour:02}:{now.minute:02d}"

        await self.bot.change_presence(
                activity=discord.Game(f"{sum(map(lambda x: x.member_count, self.bot.guilds))} 명이 이용")
        )

        await self.load_core()

        with SessionContext() as session:
            # FIXME: boot_time 제대로 갱신이 안됨
            status = session.query(Status).first()
            if status is None:
                status = Status()
            status.boot_time = f"{now_time}"
            session.add(status)
            session.commit()

        with SessionContext() as session:
            for guild in self.bot.guilds:
                for author in guild.members:
                    # if guild.id != 966942556078354502: continue
                    if author.bot:
                        continue

                    user = Users(_id=author.id, guild_id=author.guild.id, username=author.display_name)
                    if session.query(Users).filter(
                            and_(Users.id == author.id, Users.guild_id == author.guild.id)).first() is None:
                        session.add(user)
            session.commit()

    async def load_core(self):
        print("코어모듈을 로드합니다...")
        for filename in os.listdir('core'):
            if filename.endswith('.py'):
                extension_name = filename[:-3]
                if extension_name in self.core_list:
                    await self.bot.load_extension(f'core.{extension_name}')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        with SessionContext() as session:
            user = Users(_id=member.id, guild_id=member.guild.id, username=member.display_name)
            log_text = f"{member.guild} 서버에 {member.display_name} 님이 가입했습니다. ("
            try:
                session.add(user)
                session.commit()
                log_text += "유저정보 추가, "
            except:
                log_text += "중복된 유저정보, "
            log_text += ")"

        await logs.send_log(bot=self.bot, log_text=log_text)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        log_text = f"{member.guild} 서버에서 {member.display_name} 님이 나갔습니다. ("
        with SessionContext() as session:
            user = session.query(Users).filter(and_(Users.id == member.id, Users.guild_id == member.guild.id)).first()
            if user:
                role_res = await delete_role_server_by_author(member)
                if role_res: log_text += f"역할 제거, "
                try:
                    log_text += f"유저정보 제거, "
                    session.delete(user)
                    session.commit()
                except:
                    log_text += f"유저정보 제거실패, "
        log_text += ")"

        await logs.send_log(bot=self.bot, log_text=log_text)

    # @commands.Cog.listener()
    # async def on_command_error(self, ctx, error):
    #     if isinstance(error, commands.CommandNotFound):
    #         return False
    #     elif isinstance(error, commands.MissingRequiredArgument):
    #         return False
    #     elif isinstance(error, commands.BadArgument):
    #         return False
    #     else:
    #         with open('log/error.txt', 'a', encoding='utf-8') as l:
    #             now = datetime.datetime.now()
    #             formatted_time = "{}-{:02d}-{:02d} {:02d}:{:02d}".format(
    #                 now.year, now.month, now.day, now.hour, now.minute
    #             )
    #             guild_str = ctx.message.guild.name if ctx.message.guild else ""
    #             channel_str = ctx.message.channel.name if hasattr(ctx.message.channel, "name") else "dm"
    #             text = f'user : {ctx.author.name}#{ctx.author.discriminator}\n'
    #             text += f'cmd : {ctx.message.content}\n'
    #             text += f'from : {guild_str}.{channel_str}\n'
    #             text += f'error : {error}\n'
    #             text += f'date : {formatted_time}'
    #             text += f'\n\n'
    #             l.write(text)
    #             await logs.send_log(bot=self.bot,
    #                                 log_text=text)
    #         return True

    @commands.command(name='로드', aliases=['load'])
    async def load_commands(self, ctx, extension):
        if not util.is_developer(ctx.author): return
        if type(self).__name__ == extension: return

        try:
            await self.bot.load_extension(f'core.{extension}')
            await ctx.send(f':white_check_mark: {extension}을(를) 로드했습니다!')
        except commands.ExtensionAlreadyLoaded:
            await ctx.send(f':x: {extension}은(는) 이미 로드되어 있습니다!')
        except Exception as e:
            await ctx.send(f':x: {extension}을(를) 로드하는 중 오류가 발생했습니다!\n{e}')

    @commands.command(name='언로드', aliases=['unload'])
    async def unload_commands(self, ctx, extension):
        if not util.is_developer(ctx.author): return
        if type(self).__name__ == extension: return

        try:
            await self.bot.unload_extension(f'core.{extension}')
            await ctx.send(f':white_check_mark: {extension}을(를) 언로드했습니다!')
        except commands.ExtensionNotLoaded:
            await ctx.send(f':x: {extension}은(는) 로드되지 않았습니다!')
        except Exception as e:
            await ctx.send(f':x: {extension}을(를) 언로드하는 중 오류가 발생했습니다!\n{e}')

    @commands.command(name='리로드', aliases=['reload'])
    async def reload_commands(self, ctx, extension=None):
        if not util.is_developer(ctx.author): return

        if extension is None:  # extension이 None이면 (그냥 !리로드 라고 썼을 때)
            for filename in os.listdir('core'):
                if filename.endswith('.py'):
                    extension_name = filename[:-3]
                    if type(self).__name__ == extension_name: continue
                    if extension_name in self.core_list:
                        try:
                            await self.bot.unload_extension(f'core.{extension_name}')
                        except:
                            pass
                        try:
                            await self.bot.load_extension(f'core.{extension_name}')
                            await ctx.send(f':white_check_mark: {extension_name}을(를) 다시 불러왔습니다!')
                        except commands.ExtensionAlreadyLoaded:
                            await ctx.send(f':x: {extension}은(는) 이미 로드되어 있습니다!')
                        except Exception as e:
                            await ctx.send(f':x: {extension}을(를) 로드하는 중 오류가 발생했습니다!\n{e}')
        else:
            if type(self).__name__ == extension: return
            try:
                await self.bot.unload_extension(f'core.{extension}')
            except:
                pass

            try:
                await self.bot.load_extension(f'core.{extension}')
                await ctx.send(f':white_check_mark: {extension}을(를) 다시 불러왔습니다!')
            except commands.ExtensionAlreadyLoaded:
                await ctx.send(f':x: {extension}은(는) 이미 로드되어 있습니다!')
            except Exception as e:
                await ctx.send(f':x: {extension}을(를) 로드하는 중 오류가 발생했습니다!\n{e}')


async def setup(bot):
    await bot.add_cog(Event(bot))
