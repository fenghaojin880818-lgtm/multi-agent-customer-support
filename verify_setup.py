"""
验证安装脚本 - 无需 API Key
"""
import sys

print(f"Python 版本: {sys.version}")

# 验证所有依赖包
packages = {
    "langchain": "langchain",
    "langchain_core": "langchain_core.messages",
    "langchain_groq": "langchain_groq",
    "langchain_openai": "langchain_openai",
    "langgraph": "langgraph.graph",
    "langsmith": "langsmith",
    "pinecone": "pinecone",
    "dotenv": "dotenv",
    "pydantic": "pydantic",
    "tiktoken": "tiktoken",
}

print("\n依赖检查:")
for package, test_import in packages.items():
    try:
        exec(f"import {test_import}")
        print(f"  [OK] {package}")
    except ImportError:
        print(f"  [X] {package} - 未安装")

print("\n环境验证完成!")
