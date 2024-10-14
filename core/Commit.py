import openai
from discord.ext import commands
from dotenv import dotenv_values


class Commit(commands.Cog):
    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.system_msg = [
            {"role": "system", "content": """[Command]
Please transform my future inputs into GitHub Commit Messages.
Also, always respond in English.


[Structure]
The GitHub Commit Message should follow the structure `type: title`, where `type` is chosen from the following list:

- feat: Add a new feature
- fix: Fix a bug
- docs: Modify documentation
- style: Change code style (formatting, missing semicolons, etc.), without changing functionality
- design: Update user UI design (CSS, etc.)
- test: Add or refactor test code
- refactor: Refactor code
- build: Modify build files
- ci: Update CI configuration files
- perf: Improve performance
- chore: Update build tasks, package manager, etc. (e.g., modify .gitignore)
- rename: Rename files or folders
- remove: Delete files only


[Message Rules]

Additionally, follow these seven rules for the commit message:

1. The `title` must be within 50 characters.
2. The first letter of the `title` must be capitalized.
3. Do not end the `title` with a period.
4. Use imperative mood in the `title`, not past tense.
5. Each line in the body must not exceed 72 characters.
6. Focus on the 'what' and 'why', not the 'how'.
7. Write in one line."""},
        ]

    @commands.command(name="커밋", aliases=["git", "commit"])
    async def 커밋(self, ctx, *input):
        await ctx.defer()  # 오래걸리는 함수작동과 관련된 듯

        text = " ".join(input)
        request_msg = {"role": "user", "content": text}

        prompt = self.system_msg + [request_msg]
        config = dotenv_values('.env')
        client = openai.AsyncOpenAI(api_key=config["OpenAI_Secret"])
        async with ctx.typing():
            try:
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=prompt,
                    temperature=0.4,
                    stream=False,
                )
                await ctx.reply(f'{response.choices[0].message.content}', mention_author=False)
            except Exception as e:
                print(e)
                await ctx.reply(f'오류가 발생했습니다.\n{e}', mention_author=False)
                return


async def setup(bot):
    await bot.add_cog(Commit(bot))