import discord, asyncio
from discord.ext import commands

import utils.Utility as util
from utils.database.Database import SessionContext
from utils.database.model.authority import Authoritys
from utils.database.model.commands import Commands


class Authority(commands.Cog):
    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot

    @commands.command(name="권한추가")
    async def 권한추가(self, ctx, *input):
        if util.is_developer(ctx.author):
            try:
                target_user_id, input_role = input
                target_user_id = int(target_user_id)
                input_role = input_role.upper()
            except:
                await ctx.reply(f"명령어 사용법이 잘못되었습니다.\n`!권한추가 [유저아이디] [권한]`", mention_author=False)
                return

            target_author = self.bot.get_user(target_user_id)
            if target_author is None:
                await ctx.reply(f"해당 유저를 찾을 수 없습니다.", mention_author=False)
                return

            for role in util.ROLE_TYPE:
                if role.value == input_role:
                    break
            else:
                await ctx.reply(f"해당 권한이 존재하지 않습니다.\n`ex. {util.ROLE_TYPE}`", mention_author=False)
                return

            with SessionContext() as session:
                authority = session.query(Authoritys).filter(Authoritys.id == target_user_id).first()
                if authority:
                    prev_roles = authority.get_roles()
                    if input_role in prev_roles:
                        await ctx.reply(f"{target_author.display_name}님에게 이미 {input_role} 권한이 존재합니다.", mention_author=False)
                        return
                    authority.set_roles(prev_roles + [input_role])
                else:
                    authority = Authoritys(_id=target_user_id)
                    authority.set_roles([input_role])
                    session.add(authority)
                session.commit()

            await ctx.reply(f"{target_author.display_name}님에게 {input_role} 권한이 추가되었습니다.", mention_author=False)

    @commands.command(name="권한삭제", aliases=["권한제거"])
    async def 권한삭제(self, ctx, *input):
        if util.is_developer(ctx.author):
            try:
                target_user_id, delete_role = input
                target_user_id = int(target_user_id)
                delete_role = delete_role.upper()
            except:
                await ctx.reply(f"명령어 사용법이 잘못되었습니다.\n`!권한삭제 [유저아이디] [권한]`", mention_author=False)
                return

            target_author = self.bot.get_user(target_user_id)
            if target_author is None:
                await ctx.reply(f"해당 유저를 찾을 수 없습니다.", mention_author=False)
                return

            for role in util.ROLE_TYPE:
                if role.value == delete_role:
                    break
            else:
                await ctx.reply(f"해당 권한이 존재하지 않습니다.\n`ex. {util.ROLE_TYPE}`", mention_author=False)
                return

            with SessionContext() as session:
                authority = session.query(Authoritys).filter(Authoritys.id == target_user_id).first()
                if authority:
                    prev_roles = authority.get_roles()
                    if delete_role in prev_roles:
                        prev_roles.remove(delete_role)
                        authority.set_roles(prev_roles)
                    else:
                        await ctx.reply(f"{target_author.display_name}님에게 {delete_role} 권한이 존재하지 않습니다.", mention_author=False)
                        return
                else:
                    await ctx.reply(f"{target_author.display_name}님에게 {delete_role} 권한이 존재하지 않습니다.", mention_author=False)
                    return

                session.commit()
            await ctx.reply(f"{target_author.display_name}님에게 {delete_role} 권한이 제거되었습니다.", mention_author=False)

    @commands.command(name="권한보기", aliases=["권한확인"])
    async def 권한보기(self, ctx, *input):
        if util.is_developer(ctx.author):
            try:
                target_user_id = int(input[0])
            except:
                await ctx.reply(f"명령어 사용법이 잘못되었습니다.\n`!권한보기 [유저아이디]`", mention_author=False)
                return

            target_author = self.bot.get_user(target_user_id)
            if target_author is None:
                await ctx.reply(f"해당 유저를 찾을 수 없습니다.", mention_author=False)
                return

            with SessionContext() as session:
                authority = session.query(Authoritys).filter(Authoritys.id == target_user_id).first()
                if authority:
                    roles = authority.get_roles()
                    role_str = ", ".join(roles)
                    await ctx.reply(f"{target_author.display_name}님의 권한은 `{role_str}` 입니다.", mention_author=False)
                else:
                    await ctx.reply(f"{target_author.display_name}님의 권한은 존재하지 않습니다.", mention_author=False)

    @commands.command(name="서버권한추가")
    async def 서버권한추가(self, ctx, *input):
        if util.is_developer(ctx.author):
            try:
                target_guild_id, input_role = input
                target_guild_id = int(target_guild_id)
                input_role = input_role.upper()
            except:
                await ctx.reply(f"명령어 사용법이 잘못되었습니다.\n`!서버권한추가 [서버아이디] [권한]`", mention_author=False)
                return

            target_guild = self.bot.get_guild(target_guild_id)
            if target_guild is None:
                await ctx.reply(f"해당 서버를 찾을 수 없습니다.", mention_author=False)
                return

            for role in util.GUILD_COMMAND_TYPE:
                if role.value == input_role:
                    break
            else:
                await ctx.reply(f"해당 권한이 존재하지 않습니다.\n`ex. {util.GUILD_COMMAND_TYPE}`", mention_author=False)
                return

            with SessionContext() as session:
                guild_command = session.query(Commands).filter(Commands.guild_id == target_guild_id).first()
                if guild_command:
                    prev_roles = guild_command.get_roles()
                    if input_role in prev_roles:
                        await ctx.reply(f"{target_guild.name} 서버에게 이미 {input_role} 권한이 존재합니다.",
                                        mention_author=False)
                        return
                    guild_command.set_roles(prev_roles + [input_role])
                else:
                    guild_command = Commands(guild_id=target_guild_id)
                    guild_command.set_roles([input_role])
                    session.add(guild_command)
                session.commit()

            await ctx.reply(f"{target_guild.name} 서버에게 {input_role} 권한이 추가되었습니다.", mention_author=False)

    @commands.command(name="서버권한삭제", aliases=["서버권한제거"])
    async def 서버권한삭제(self, ctx, *input):
        if util.is_developer(ctx.author):
            try:
                target_guild_id, delete_role = input
                target_guild_id = int(target_guild_id)
                delete_role = delete_role.upper()
            except:
                await ctx.reply(f"명령어 사용법이 잘못되었습니다.\n`!서버권한삭제 [서버아이디] [권한]`", mention_author=False)
                return

            target_guild = self.bot.get_guild(target_guild_id)
            if target_guild is None:
                await ctx.reply(f"해당 서버를 찾을 수 없습니다.", mention_author=False)
                return

            for role in util.GUILD_COMMAND_TYPE:
                if role.value == delete_role:
                    break
            else:
                await ctx.reply(f"해당 권한이 존재하지 않습니다.\n`ex. {util.GUILD_COMMAND_TYPE}`", mention_author=False)
                return

            with SessionContext() as session:
                guild_command = session.query(Commands).filter(Commands.guild_id == target_guild_id).first()
                if guild_command:
                    prev_roles = guild_command.get_roles()
                    if delete_role in prev_roles:
                        prev_roles.remove(delete_role)
                        guild_command.set_roles(prev_roles)
                    else:
                        await ctx.reply(f"{target_guild.name} 서버에게 {delete_role} 권한이 존재하지 않습니다.", mention_author=False)
                        return
                else:
                    await ctx.reply(f"{target_guild.name} 서버에게 {delete_role} 권한이 존재하지 않습니다.", mention_author=False)
                    return

                session.commit()
            await ctx.reply(f"{target_guild.name} 서버에게 {delete_role} 권한이 제거되었습니다.", mention_author=False)

    @commands.command(name="서버권한보기", aliases=["서버권한확인"])
    async def 서버권한보기(self, ctx, *input):
        if util.is_developer(ctx.author):
            try:
                target_guild_id = int(input[0])
            except:
                await ctx.reply(f"명령어 사용법이 잘못되었습니다.\n`!서버권한보기 [서버아이디]`", mention_author=False)
                return

            target_guild = self.bot.get_guild(target_guild_id)
            if target_guild is None:
                await ctx.reply(f"해당 서버를 찾을 수 없습니다.", mention_author=False)
                return

            with SessionContext() as session:
                guild_command = session.query(Commands).filter(Commands.guild_id == target_guild_id).first()
                if guild_command:
                    roles = guild_command.get_roles()
                    role_str = ", ".join(roles)
                    await ctx.reply(f"{target_guild.name} 서버의 권한은 `{role_str}` 입니다.", mention_author=False)
                else:
                    await ctx.reply(f"{target_guild.name} 서버의 권한은 존재하지 않습니다.", mention_author=False)


async def setup(bot):
    await bot.add_cog(Authority(bot))
