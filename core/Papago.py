import urllib.request

import discord
import json
import langid
from discord.ext import commands
from dotenv import dotenv_values

from utils.Timeout import timeout


class Papago(commands.Cog):

    def __init__(self, bot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.support_langs = {
            'af': False, 'am': False, 'an': False, 'ar': False, 'as': False, 'az': False, 'be': False, 'bg': False,
            'bn': False, 'br': False, 'bs': False, 'ca': False, 'cs': False, 'cy': False, 'da': False, 'de': '독일어',
            'dz': False, 'el': False, 'en': '영어', 'eo': False, 'es': '스페인어', 'et': False, 'eu': False, 'fa': False,
            'fi': False, 'fo': False, 'fr': '프랑스어', 'ga': False, 'gl': False, 'gu': False, 'he': False, 'hi': False,
            'hr': False, 'ht': False, 'hu': False, 'hy': False, 'id': '인도네시아어', 'is': False, 'it': '이탈리아어', 'ja': '일본어',
            'jv': False, 'ka': False, 'kk': False, 'km': False, 'kn': False, 'ko': '한국어', 'ku': False, 'ky': False,
            'la': False, 'lb': False, 'lo': False, 'lt': False, 'lv': False, 'mg': False, 'mk': False, 'ml': False,
            'mn': False, 'mr': False, 'ms': False, 'mt': False, 'nb': False, 'ne': False, 'nl': False, 'nn': False,
            'no': False, 'oc': False, 'or': False, 'pa': False, 'pl': False, 'ps': False, 'pt': False, 'qu': False,
            'ro': False, 'ru': '러시아어', 'rw': False, 'se': False, 'si': False, 'sk': False, 'sl': False, 'sq': False,
            'sr': False, 'sv': False, 'sw': False, 'ta': False, 'te': False, 'th': '태국어', 'tl': False, 'tr': False,
            'ug': False, 'uk': False, 'ur': False, 'vi': '베트남어', 'vo': False, 'wa': False, 'xh': False, 'zh': '중국어',
            'zu': False
        }

        self.exception_lang = {
            'zh': 'zh-CN'
        }

    def translate_text_with_papago(self, source_language, target_language, source_text):
        config = dotenv_values('.env')
        client_id = config['Naver_Client_ID']  # 개발자센터에서 발급받은 Client ID 값
        client_secret = config['Naver_Client_Secret']  # 개발자센터에서 발급받은 Client Secret 값
        quote_text = urllib.parse.quote(source_text)
        data = f"source={source_language}&target={target_language}&text={quote_text}"
        url = "https://openapi.naver.com/v1/papago/n2mt"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        result_code = response.getcode()
        if result_code == 200:
            response_body = response.read()
            response_body = response_body.decode('utf-8')
            json_obj = json.loads(response_body)
            return True, json_obj["message"]["result"]["translatedText"]
        else:
            return False, result_code

    async def too_long_text(self, ctx, text):
        if len(text) >= 500:
            embed = discord.Embed(color=0x2f3136)
            embed.set_author(name=f'입력값이 너무 길어요. `({len(text)})`')
            embed.set_thumbnail(url=self.bot.user.display_avatar)
            embed.add_field(name="결과", value=f'더 짧은 문장으로 작성해주세요.')
            await ctx.reply(embed=embed, mention_author=False)
            return True
        return False

    async def translate_result_form(self, ctx, source, target):
        embed = discord.Embed(color=0x2f3136)
        embed.set_author(name=f'파파고 번역 결과에요.')
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.add_field(name="원문", value=f'{source}')
        embed.add_field(name="결과", value=f'{target}')
        await ctx.reply(embed=embed, mention_author=False)

    async def fail_form(self, ctx):
        embed = discord.Embed(color=0x2f3136)
        embed.set_author(name=f'오늘 할당량이 끝났어요.')
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.add_field(name="결과", value=f'내일 다시 부탁드려요!')
        await ctx.reply(embed=embed, mention_author=False)

    @timeout(5)
    def recogize_language(self, text):
        return langid.classify(text)

    @commands.command(name="번역")
    async def 번역(self, ctx, *input):
        # kor -> eng
        # not kor -> only kor
        text = " ".join(input)
        if await self.too_long_text(ctx, text):
            return False

        # lang, _ = langid.classify(text)

        try:
            lang, _ = self.recogize_language(text)
        except Exception as e:
            if type(e).__name__ == 'TimeoutError':
                await ctx.channel.send(f'언어를 인식하는데 시간이 오래걸려서 정지시켰어요. ㅠㅠ')
            else:
                await ctx.channel.send(f'언어를 인식하는 과정에서 오류가 발생했어요.\n에러 : {e}')
            return False

        support = self.support_langs[lang]
        if support is not False:
            if self.exception_lang.get(lang):
                lang = self.exception_lang[lang]

            if lang == "ko":
                res, content = self.translate_text_with_papago("ko", "en", text)
            else:
                res, content = self.translate_text_with_papago(lang, "ko", text)

            if res is True:
                await self.translate_result_form(ctx, text, content)
            else:
                print("Error Code:" + content)
                await self.fail_form(ctx)

        else:
            embed = discord.Embed(color=0x2f3136)
            embed.set_author(name=f'파파고가 지원하지 않는 언어에요.')
            embed.set_thumbnail(url=self.bot.user.display_avatar)
            embed.add_field(name="결과",
                            value=f'파파고가 지원하는 언어는\n`{[support for support in self.support_langs.values() if support is not False]}`가 있어요.')
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(name="한영번역", aliases=[])
    async def 한영번역(self, ctx, *input):
        text = " ".join(input)
        if await self.too_long_text(ctx, text):
            return False

        res, content = self.translate_text_with_papago("ko", "en", text)
        if res is True:
            await self.translate_result_form(ctx, text, content)
        else:
            print("Error Code:" + content)
            await self.fail_form(ctx)

    @commands.command(name="영한번역", aliases=[])
    async def 영한번역(self, ctx, *input):
        text = " ".join(input)
        if await self.too_long_text(ctx, text):
            return False

        res, content = self.translate_text_with_papago("en", "ko", text)
        if res is True:
            await self.translate_result_form(ctx, text, content)
        else:
            print("Error Code:" + content)
            await self.fail_form(ctx)


async def setup(bot):
    await bot.add_cog(Papago(bot))
