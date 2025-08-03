import asyncio
from datetime import datetime, timedelta
from typing import Literal

import discord
from discord import app_commands, Interaction
from discord.ext import commands
from dotenv import dotenv_values
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_voyageai import VoyageAIEmbeddings
from pymongo import MongoClient

import utils.Logs as logs
import utils.Utility as util
from main import MynaBot

prompt_template = """
당신은 사용자 질문에 대해 제공된 문서를 기반으로 사실에 입각한 답변을 생성하는 AI 어시스턴트입니다.

질문:
{question}

관련 문서:
{context}

답변:
"""

class Edac(commands.Cog):
    def __init__(self, bot: MynaBot):
        print(f'{type(self).__name__}가 로드되었습니다.')
        self.bot = bot
        self.usage_per_cnt = 10
        self.usage_list = {}

    def get_retriever(self):
        denv = dotenv_values(".env")
        client = MongoClient(denv["MONGODB_URL"])
        db_name = "rag"
        collection_name = "edac-rag"
        collection = client[db_name][collection_name]

        embedding_model = VoyageAIEmbeddings(model="voyage-3.5")

        vectorstore = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embedding_model,
            index_name="default"
        )

        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        return retriever

    def get_rag_chain(self):
        retriever = self.get_retriever()
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
        rag_prompt = PromptTemplate.from_template(prompt_template)

        # 체인 구성: {input -> retriever -> docs -> context formatting -> prompt -> llm -> output}
        chain = (
                {"context": retriever | (lambda docs: "\n\n".join([doc.page_content for doc in docs])),
                 "question": RunnablePassthrough()}
                | rag_prompt
                | llm
                | StrOutputParser()
        )

        return chain, retriever

    def sync_get_answer_from_rag(self, query):
        chain, retriever = self.get_rag_chain()
        answer = chain.invoke(query) # 답변
        source_docs = retriever.invoke(query) # 출처
        return answer, source_docs

    # 비동기 래핑 함수
    async def get_answer_from_rag_async(self, query):
        return await asyncio.to_thread(self.sync_get_answer_from_rag, query)

    def split_message(self, text:str, max_length=2000):
        """문자열을 디스코드 메시지 길이에 맞게 분할"""
        lines = text.split('\n')
        chunks = []
        buffer = ''
        in_code_block = False
        code_block_language = ''


        for line in lines:
            is_code_fence = line.strip().startswith("```")
            line_with_newline = line + '\n'

            # Handle code block start or end
            if is_code_fence:
                if not in_code_block:
                    # START of code block
                    in_code_block = True
                    code_block_language = line.strip()[3:].strip()
                    if buffer and not buffer.endswith('\n\n'):
                        buffer += '\n'  # Ensure code block starts on new line
                else:
                    # END of code block
                    in_code_block = False

            if len(buffer) + len(line_with_newline) > max_length:
                if in_code_block:
                    # Close code block in current chunk
                    buffer += f"\n```"
                    chunks.append(buffer)
                    # Start new chunk with code block reopened
                    buffer = f"```{code_block_language}\n{line_with_newline}"
                else:
                    chunks.append(buffer)
                    buffer = line_with_newline
            else:
                buffer += line_with_newline

        if buffer:
            if in_code_block:
                buffer += "\n```"
            chunks.append(buffer)

        return chunks

    async def check_usage(self, interaction: Interaction[MynaBot]):
        user_id = interaction.user.id
        user_usage = self.usage_list.get(user_id)

        if util.developer(interaction):
            return True

        if user_usage is None:
            now = datetime.now()
            self.usage_list[user_id] = {"cnt": 1, "date": now, "can_date": now + timedelta(hours=3)}
            return True

        if user_usage["cnt"] < self.usage_per_cnt:
            user_usage["cnt"] += 1
            return True
        else:
            can_date = user_usage["can_date"]

            if can_date >= datetime.now():
                await interaction.response.send_message(content=f"🔥 {interaction.user.display_name}님에게 부여된 사용량이 모두 소진되었습니다.\n> {can_date.strftime('%Y.%m.%d %H:%M:%S')}에 제한이 풀립니다.")
                return False
            else:
                self.usage_list[user_id] = {"cnt": 1, "date": datetime.now()}
                return True

    @app_commands.command(description='AI + RAG 기술을 활용하여 카페에 있는 원하는 강의글을 베이스로 질문에 답변합니다.')
    @app_commands.describe(message="궁금한 내용을 입력합니다.")
    async def 질문하기(self, interaction: Interaction[MynaBot], message: str):
        allowed_guild = util.is_allow_guild_interaction(interaction, util.GUILD_COMMAND_TYPE.EUD)

        if allowed_guild is False:
            await interaction.response.send_message(f"개발자가 허용한 서버만 질문하기 명령어를 사용할 수 있어요.", ephemeral=True)
            return

        if not interaction.channel.topic or "EUD" not in interaction.channel.topic:
            channels = interaction.guild.text_channels

            allow_channel = None
            for channel in channels:
                if channel.topic and "EUD" in channel.topic:
                    allow_channel = channel
                    break

            if allow_channel is None:
                await interaction.response.send_message(content=f"사용할 수 없는 명령어입니다. 관리자에게 문의해주세요.\n-# 채널 토픽에 `EUD`가 포함된 채널에서만 사용할 수 있습니다.", ephemeral=True)
            else:
                await interaction.response.send_message(content=f"{allow_channel.name} 채널에서 사용할 수 있습니다.", ephemeral=True)

            return

        if not await self.check_usage(interaction):
            return

        await interaction.response.defer()
        await logs.send_log(bot=self.bot,
                            log_text=f"{interaction.guild.name}의 {interaction.user.display_name}님이 질문하기 명령어를 실행했습니다.")
        
        try:
            answer, sources = await self.get_answer_from_rag_async(message)

            if sources:
                source_text = f"\n\n## Reference\n"
                for i, doc in enumerate(sources):
                    meta = doc.metadata
                    title = meta.get("title", "No title")
                    author = meta.get("author_nickname", "No Author")
                    source_url = meta.get("source", "No link")

                    source_text += f"-# {i+1}번. {title} ({author}님) [링크]({source_url})\n"

                answer += source_text

            user_usage = self.usage_list.get(interaction.user.id)
            if user_usage is not None:
                can_date = user_usage["can_date"]
                answer += f"> {interaction.user.display_name}님은 {can_date.strftime('%Y.%m.%d %H:%M:%S')}까지 남은 사용량이 {self.usage_per_cnt - user_usage['cnt']}회 남았습니다."

            answer_chunks = self.split_message(f"🧠 **마이나의 답변:**\n\n{answer}")
            for chunk in answer_chunks:
                await interaction.followup.send(content=chunk)

        except Exception as e:
            print(f"검색 중 오류 발생! {e}")
            await logs.send_log(bot=self.bot,
                                log_text=f"질문하기 명령어에서 오류가 발생했습니다. {e}")

async def setup(bot):
    await bot.add_cog(Edac(bot))
