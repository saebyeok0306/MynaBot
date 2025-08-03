import asyncio

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

    def get_retriever(self):
        denv = dotenv_values(".env")
        print("--- 벡터 데이터베이스 연결 ---")
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
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)
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
        current = ""
        for line in lines:
            if len(current) + len(line) + 1 > max_length:
                chunks.append(current)
                current = line
            else:
                current += "\n" + line if current else line
        if current:
            chunks.append(current)
        return chunks

    @app_commands.command(description='AI + RAG 기술을 활용하여 카페에 있는 원하는 강의글을 베이스로 질문에 답변합니다.')
    @app_commands.describe(message="궁금한 내용을 입력합니다.")
    async def 질문하기(self, interaction: Interaction[MynaBot], message: str):
        await interaction.response.defer()

        await logs.send_log(bot=self.bot,
                            log_text=f"{interaction.guild.name}의 {interaction.user.display_name}님이 강의 검색 명령어를 실행했습니다.")
        
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

            answer_chunks = self.split_message(f"🧠 **마이나의 답변:**\n\n{answer}")
            for chunk in answer_chunks:
                await interaction.followup.send(chunk)

        except Exception as e:
            print(f"검색 중 오류 발생! {e}")

async def setup(bot):
    await bot.add_cog(Edac(bot))
