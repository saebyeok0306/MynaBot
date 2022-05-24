import discord, asyncio, json, random, datetime
import sys, os
import data.Functions as fun
from discord.ext import commands


# sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root
# screen -S dc python3 main.py
# screen -S dc -X quit

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')
token = ''
with open('data/token.json', 'r') as f:
    loaded_data = json.load(f)  # 데이터 로드하기
    token = loaded_data['token']

for filename in os.listdir('core'):
    if filename.endswith('.py'):
        bot.load_extension(f'core.{filename[:-3]}')
        # print(f'{filename[:-3]}가 로드되었습니다.')

@bot.event
async def on_ready():
    print('로그인되었습니다!')
    print(bot.user.name)
    print(bot.user.id)
    print('==============================')
    game = discord.Game('명령어는 [!도움말] 참고')
    await bot.change_presence(status=discord.Status.online, activity=game)

    fun.getGuilds(bot)

@bot.event
async def on_message(message):
    if message.author.bot: return None

    if random.randint(1, 10) <= 2:
        if message.content.count('ㅋ') >= 2:
            emoji = ['<a:jerry:762198111119605770>','<:dog1:647472178287214593>','<a:SpongeBob3:762542652381069352>','<a:SpongeBob2:762541940914782260>', '<:cat2:671208661997060096>','<:troll2:733561463930749007>','<:troll3:733561496076025866>', '<:cat3:750001125477974106>']
            await message.add_reaction(random.choice(emoji))
        
        elif '캬루' in message.content:
            emoji = ['<:jjag2:740050586828931164>', '<:cat2:745897614708441168>', '<:cat3:750001125477974106>', '<:cat4:750001279014797342>', '<:cat5:750001356709822504>', '<:cat7:750324958554751106>', '<:cat8:753133462642229248>', '<:cat9:753132725107556442>', '<:jjag:739874314324672532>', '<a:jjag3:740055407103574097>']
            await message.add_reaction(random.choice(emoji))
        
    if '몰?루' == message.content or '몰!루' == message.content:
        await message.add_reaction('<a:molu:968521092476051526>')
    elif '아?루' == message.content or '아!루' == message.content:
        await message.add_reaction('<a:aru:968710530376282212>')

    await bot.process_commands(message)

@bot.command(name='로드', aliases=['load'])
async def load_commands(ctx, extension):
    if ctx.message.author.guild_permissions.administrator:
        bot.load_extension(f'core.{extension}')
        await ctx.send(f':white_check_mark: {extension}을(를) 로드했습니다!')

@bot.command(name='언로드', aliases=['unload'])
async def unload_commands(ctx, extension):
    if ctx.message.author.guild_permissions.administrator:
        bot.unload_extension(f'core.{extension}')
        await ctx.send(f':white_check_mark: {extension}을(를) 언로드했습니다!')

@bot.command(name='리로드', aliases=['reload'])
async def reload_commands(ctx, extension=None):
    if ctx.message.author.guild_permissions.administrator:
        if extension is None: # extension이 None이면 (그냥 !리로드 라고 썼을 때)
            for filename in os.listdir('core'):
                if filename.endswith('.py'):
                    extensionName = filename[:-3]
                    try: bot.unload_extension(f'core.{extensionName}')
                    except: pass
                    bot.load_extension(f'core.{extensionName}')
                    await ctx.send(f':white_check_mark: {extensionName}을(를) 다시 불러왔습니다!')
        else:
            bot.unload_extension(f'core.{extension}')
            bot.load_extension(f'core.{extension}')
            await ctx.send(f':white_check_mark: {extension}을(를) 다시 불러왔습니다!')
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):             return
    elif isinstance(error, commands.MissingRequiredArgument):   return
    elif isinstance(error, commands.BadArgument):               return
    else:
        with open('log/error.txt', 'a', encoding='utf-8') as l:
            now = datetime.datetime.now()
            nowDatetime = "{}-{:02d}-{:02d} {:02d}:{:02d}".format(now.year, now.month, now.day, now.hour, now.minute)
            text = f'user : {ctx.author.name}#{ctx.author.discriminator}\n'
            text += f'cmd : {ctx.message.content}\n'
            text += f'from : {ctx.message.guild.name}.{ctx.message.channel.name}\n'
            text += f'error : {error}\n'
            text += f'date : {nowDatetime}'
            text += f'\n\n'
            l.write(text)
        
        # embed = discord.Embed(title='Error', description='오류가 발생했습니다.', color=0xFF0000)
        # embed.add_field(name='상세내용', value=f'```{error}```')
        # await ctx.send(embed=embed)

@bot.event
async def on_member_remove(member):
    await fun.deleteUserRole(member.guild, member) # delete role
    fun.removeUserDB(member.id) # db에서 데이터 삭제

bot.run(token)