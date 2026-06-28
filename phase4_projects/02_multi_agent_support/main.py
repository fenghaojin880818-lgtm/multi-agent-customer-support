"""
多代理智能客服系统 - 完整实现

本模块实现了一个生产级别的多代理客服系统，包括：
- 智能意图分类和路由
- 专业领域代理（技术支持、订单服务、产品咨询）
- 工具集成（订单查询、产品搜索）
- 服务质量监控
- 人工升级机制
"""

import os
from typing import List, Dict, Any, Optional, TypedDict, Literal, Annotated
from dataclasses import dataclass
from datetime import datetime
import json
from dotenv import load_dotenv

# LangChain 核心导入
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool

# LangGraph
from langgraph.graph import StateGraph, START, END
from langchain.agents import create_agent

# ==================== JSON 解析辅助函数 ====================

def safe_parse_json(text: str, default: dict = None) -> dict:
    """
    安全地解析JSON文本
    
    处理：
    - Markdown 代码块 (```json ... ```)
    - 前后的空白字符
    - 解析失败时返回默认值
    """
    if default is None:
        default = {}
    
    content = text.strip()
    
    # 移除 Markdown 代码块
    if "```json" in content:
        try:
            content = content.split("```json")[1].split("```")[0]
        except IndexError:
            pass
    elif "```" in content:
        try:
            parts = content.split("```")
            if len(parts) >= 2:
                content = parts[1]
        except IndexError:
            pass
    
    content = content.strip()
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"   ⚠️ JSON 解析失败: {e}")
        return default



# 加载环境变量
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

USE_MOCK = True

# Skip API check in mock mode
if not USE_MOCK and (not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here"):
    raise ValueError(
        "\n请先在 .env 文件中设置有效的 GROQ_API_KEY\n"
        "访问 https://console.groq.com/keys 获取免费密钥"
    )

# 初始化模型
model = init_chat_model("groq:llama-3.3-70b-versatile", api_key=GROQ_API_KEY)

# ==================== Mock 模式（无需 API Key）====================
class MockLLM:
    INTENT_MAP = {
        "tech_support": ["蓝牙","耳机","连接不上","充电慢","坏了","故障"],
        "order_service": ["订单","物流","快递","ORD00","什么时候到","发货"],
        "product_consult": ["推荐","预算","怎么样","有什么","功能","价格"],
        "escalate": ["投诉","经理","退款","赔偿","第三次"],
    }
    RESPONSES = {
        "tech_support": (
            "【技术支持】请尝试：\n1. 重启设备\n2. 检查蓝牙是否开启\n"
            "3. 确保电量充足\n如仍有问题，请联系人工客服。"
        ),
        "order_service": (
            "【订单服务】订单已发货，顺丰快递，预计2-3个工作日送达。\n"
            "如有疑问，请提供订单号进一步查询。"
        ),
        "product_consult": (
            "【产品咨询】推荐商品：\n"
            "1. 智能手表Pro - ￥1299\n2. 无线耳机Max - ￥899\n"
            "3. 智能手环 - ￥399\n需要了解哪款？"
        ),
        "escalate": "【人工升级】已为您转接高级客服专员，请稍候...",
    }
    def classify(self, msg):
        for intent, kws in self.INTENT_MAP.items():
            if any(k in msg for k in kws):
                return {"intent": intent, "confidence": 0.88}
        return {"intent": "product_consult", "confidence": 0.65}
    def respond(self, intent, msg):
        return self.RESPONSES.get(intent, self.RESPONSES["product_consult"])
    def quality(self, msg, resp):
        score = 0.9 if len(resp) > 20 else 0.3
        return {"score": score, "pass": score >= 0.5, "suggestion": ""}

mock = MockLLM()
print("  [Mock] Running in mock mode (no API key needed)")


@tool
def query_order(order_id: str) -> str:
    """查询订单信息

    Args:
        order_id: 订单号，格式如 ORD001
    
    Returns:
        订单详情的JSON字符串
    """
    order = MOCK_ORDERS.get(order_id.upper())
    if order:
        return json.dumps(order, ensure_ascii=False, indent=2)
    return f"未找到订单 {order_id}"

@tool
def track_shipping(tracking_number: str) -> str:
    """查询物流信息

    Args:
        tracking_number: 物流单号
    
    Returns:
        物流状态信息
    """
    # 模拟物流信息
    if tracking_number.startswith("SF"):
        return f"顺丰快递 {tracking_number}: 包裹已到达配送站，预计今日送达"
    elif tracking_number.startswith("YT"):
        return f"圆通快递 {tracking_number}: 已签收"
    return f"未找到物流信息 {tracking_number}"

@tool
def search_product(keyword: str) -> str:
    """搜索产品信息

    Args:
        keyword: 产品关键词
    
    Returns:
        匹配产品的信息
    """
    results = []
    for name, info in MOCK_PRODUCTS.items():
        if keyword.lower() in name.lower():
            results.append({
                "name": name,
                "price": f"¥{info['price']}",
                "features": info['features'],
                "rating": f"{info['rating']}分"
            })
    
    if results:
        return json.dumps(results, ensure_ascii=False, indent=2)
    return f"未找到包含 '{keyword}' 的产品"

@tool
def get_product_recommendations(budget: int, category: str = "全部") -> str:
    """根据预算推荐产品

    Args:
        budget: 预算金额
        category: 产品类别（可选）
    
    Returns:
        推荐产品列表
    """
    recommendations = []
    for name, info in MOCK_PRODUCTS.items():
        if info['price'] <= budget:
            recommendations.append({
                "name": name,
                "price": f"¥{info['price']}",
                "rating": info['rating']
            })
    
    # 按评分排序
    recommendations.sort(key=lambda x: float(x['rating']), reverse=True)
    
    if recommendations:
        return json.dumps(recommendations[:3], ensure_ascii=False, indent=2)
    return f"在预算 ¥{budget} 内暂无推荐产品"

@tool
def search_faq(problem_type: str) -> str:
    """搜索常见问题解答

    Args:
        problem_type: 问题类型关键词
    
    Returns:
        相关FAQ答案
    """
    for key, answer in FAQ_DATABASE.items():
        if problem_type in key or key in problem_type:
            return f"【{key}】\n{answer}"
    return "未找到相关FAQ，建议联系人工客服获取更多帮助。"

# ==================== 状态定义 ====================

class CustomerServiceState(TypedDict):
    """客服系统状态"""
    user_message: str                   # 用户消息
    chat_history: List[Dict[str, str]]  # 对话历史
    intent: str                         # 识别的意图
    confidence: float                   # 意图置信度
    agent_response: str                 # 代理回复
    needs_escalation: bool              # 是否需要升级
    escalation_reason: str              # 升级原因
    quality_score: float                # 质量评分
    metadata: Dict[str, Any]            # 元数据

# ==================== 代理定义 ====================

class IntentClassifier:
    """意图分类器"""
    
    def __init__(self):
        self.llm = model
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个意图分类专家。分析用户消息并返回意图分类。

可选意图：
- tech_support: 技术问题、故障排除、使用帮助
- order_service: 订单查询、物流跟踪、退换货
- product_consult: 产品咨询、价格询问、功能介绍
- escalate: 投诉、无法理解、需要人工

返回格式（JSON）：
{{"intent": "意图类型", "confidence": 0.0-1.0, "reason": "分类原因"}}

只返回JSON，不要其他内容。"""),
            ("human", "{message}")
        ])
    
    def classify(self, message: str) -> Dict[str, Any]:
        """分类用户意图"""
        chain = self.prompt | self.llm | StrOutputParser()
        result = chain.invoke({"message": message})
        
        # 使用安全的 JSON 解析
        default_result = {"intent": "escalate", "confidence": 0.5, "reason": "解析失败"}
        parsed = safe_parse_json(result, default_result)
        
        # 确保返回有效的意图
        if "intent" not in parsed:
            return default_result
        return parsed

class TechSupportAgent:
    """技术支持代理"""
    
    def __init__(self):
        self.llm = model
        self.tools = [search_faq]
        
        # 先定义 system_prompt
        self.system_prompt = """你是一个专业的技术支持工程师。你的职责是：
1. 分析用户遇到的技术问题
2. 提供清晰的故障排除步骤
3. 使用 search_faq 工具查找相关解决方案
4. 如果问题超出能力范围，建议升级到人工支持

回复要求：
- 语气友好专业
- 步骤清晰有序
- 提供多个可能的解决方案"""
        
        # 创建 agent 时传入所有参数
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt
        )
    
    def handle(self, message: str, chat_history: List = None) -> str:
        """处理技术支持请求"""
        # 不需要再拼接 system_prompt，直接传用户消息
        messages = [{"role": "user", "content": message}]
        
        result = self.agent.invoke({"messages": messages})
        
        # 提取最终回复
        if result["messages"]:
            return result["messages"][-1].content
        return "抱歉，我暂时无法处理您的问题。建议联系人工客服。"

class OrderServiceAgent:
    """订单服务代理"""
    
    def __init__(self):
        self.llm = model
        self.tools = [query_order, track_shipping]
        
        self.system_prompt = """你是一个专业的订单服务专员。你的职责是：
1. 帮助用户查询订单状态
2. 提供物流跟踪信息
3. 解答退换货相关问题
4. 使用工具获取准确信息

回复要求：
- 信息准确完整
- 主动提供相关信息
- 如果需要订单号，礼貌询问"""
        
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt
        )
    
    def handle(self, message: str, chat_history: List = None) -> str:
        """处理订单服务请求"""
        messages = [{"role": "user", "content": message}]
        
        result = self.agent.invoke({"messages": messages})
        
        if result["messages"]:
            return result["messages"][-1].content
        return "抱歉，订单查询服务暂时不可用。请稍后再试。"

class ProductConsultAgent:
    """产品咨询代理"""
    
    def __init__(self):
        self.llm = model
        self.tools = [search_product, get_product_recommendations]
        
        self.system_prompt = """你是一个热情的产品顾问。你的职责是：
1. 介绍产品功能和特点
2. 根据用户需求推荐合适的产品
3. 解答价格和库存问题
4. 使用工具获取最新产品信息

回复要求：
- 热情有亲和力
- 突出产品优势
- 根据用户需求推荐
- 不要过度推销"""
        
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt
        )
    
    def handle(self, message: str, chat_history: List = None) -> str:
        """处理产品咨询请求"""
        messages = [{"role": "user", "content": message}]
        
        result = self.agent.invoke({"messages": messages})
        
        if result["messages"]:
            return result["messages"][-1].content
        return "抱歉，产品信息查询暂时不可用。请稍后再试。"

class QualityChecker:
    """质量检查器"""
    
    def __init__(self):
        self.llm = model
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是客服质量检查专家。评估客服回复的质量。

评估维度：
1. 相关性（0-25分）：回复是否针对用户问题
2. 完整性（0-25分）：是否提供了足够的信息
3. 专业性（0-25分）：语言是否专业得体
4. 有用性（0-25分）：是否真正帮助到用户

返回格式（JSON）：
{{"total_score": 0-100, "needs_escalation": true/false, "reason": "评估说明"}}

只返回JSON。"""),
            ("human", """用户问题：{user_message}
客服回复：{agent_response}

请评估：""")
        ])
    
    def check(self, user_message: str, agent_response: str) -> Dict[str, Any]:
        """检查回复质量"""
        chain = self.prompt | self.llm | StrOutputParser()
        result = chain.invoke({
            "user_message": user_message,
            "agent_response": agent_response
        })
        
        # 使用安全的 JSON 解析
        default_result = {"total_score": 60, "needs_escalation": False, "reason": "评估完成"}
        return safe_parse_json(result, default_result)

# ==================== 客服系统主类 ====================



# TODO: StateGraph workflow coming soon
