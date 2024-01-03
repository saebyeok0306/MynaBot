import os, importlib
from discord.ext import commands


class Extension(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot

        if bot.user.name == "마이나":
            self.main = importlib.import_module("main")
        else:
            self.main = importlib.import_module("mainTest")

    @staticmethod
    def is_developer(ctx):
        if ctx.author.id == 383483844218585108:
            return True
        return False

    @commands.command(name='로드', aliases=['load'])
    async def load_commands(self, ctx, extension):
        if not self.is_developer(ctx): return
        if type(self).__name__ == extension: return

        await self.bot.load_extension(f'core.{extension}')
        await ctx.send(f':white_check_mark: {extension}을(를) 로드했습니다!')

    @commands.command(name='언로드', aliases=['unload'])
    async def unload_commands(self, ctx, extension):
        if not self.is_developer(ctx): return
        if type(self).__name__ == extension: return

        await self.bot.unload_extension(f'core.{extension}')
        await ctx.send(f':white_check_mark: {extension}을(를) 언로드했습니다!')

    @commands.command(name='리로드', aliases=['reload'])
    async def reload_commands(self, ctx, extension=None):
        if not self.is_developer(ctx): return

        if extension is None:  # extension이 None이면 (그냥 !리로드 라고 썼을 때)
            for filename in os.listdir('core'):
                if filename.endswith('.py'):
                    extension_name = filename[:-3]
                    if type(self).__name__ == extension_name: continue
                    if extension_name in self.main.core_list:
                        try:
                            await self.bot.unload_extension(f'core.{extension_name}')
                        except:
                            pass
                        await self.bot.load_extension(f'core.{extension_name}')
                        await ctx.send(f':white_check_mark: {extension_name}을(를) 다시 불러왔습니다!')
        else:
            if type(self).__name__ == extension: return
            await self.bot.unload_extension(f'core.{extension}')
            await self.bot.load_extension(f'core.{extension}')
            await ctx.send(f':white_check_mark: {extension}을(를) 다시 불러왔습니다!')


async def setup(bot):
    await bot.add_cog(Extension(bot))