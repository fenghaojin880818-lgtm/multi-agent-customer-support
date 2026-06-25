"""
Phase 1: Fundamentals - 01 Hello LangChain
"""
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
import os

load_dotenv()


def main():
    # 初始化 LLM
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.7,
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )

    # 创建消息
    messages = [
        SystemMessage(content="你是一个有帮助的 AI 助手。请用中文回答。"),
        HumanMessage(content="你好！请用一句话介绍 LangChain。"),
    ]

    # 调用 LLM
    response = llm.invoke(messages)
    print(f"🤖 AI: {response.content}")


if __name__ == "__main__":
    main()
