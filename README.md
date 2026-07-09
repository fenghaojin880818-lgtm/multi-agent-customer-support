<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python" />
  <img src="https://img.shields.io/badge/LangChain-1.0-green" />
  <img src="https://img.shields.io/badge/LangGraph-1.0-purple" />
  <img src="https://img.shields.io/badge/Architecture-Multi--Agent-orange" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" />
</p>

---

# 🤖 Multi-Agent Customer Support System

> **多智能体协作智能客服系统** — 基于 LangChain 1.0 + LangGraph 1.0 构建的生产级多 Agent 协作系统

---

## 📋 项目简介

本项目实现了一个**生产级别的多 Agent 智能客服系统**，核心思想是**分工协作**：系统自动判断用户意图，将问题分发给最合适的专业 Agent 处理，最后经过质量检查决定是否回复用户或升级到人工客服。

这套架构是目前 AI 客服领域的**行业标准模式**，已被 OpenAI、Anthropic 等公司在其产品中广泛采用。

---

## 🏗️ 系统架构

```
                        ┌──────────────────┐
                        │   用户输入(User)   │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │  IntentClassifier │  ← 意图分类核心
                        │  (意图识别与分类)  │
                        └────────┬─────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
            ┌───────────┐ ┌──────────┐ ┌───────────┐
            │ 技术支持   │ │ 订单服务 │ │ 产品咨询  │
            │ TechAgent │ │OrderAgent│ │ProductAgent│
            └─────┬─────┘ └────┬─────┘ └─────┬─────┘
                  │            │              │
                  └────────────┼──────────────┘
                               ▼
                        ┌──────────────┐
                        │ QualityCheck │  ← 质量检查层
                        │ (质量评分+决策)│
                        └──────┬───────┘
                              ╱ ╲
                            ╱     ╲
                       通过/回复   转人工
```

---

## 🛠️ 核心技术栈

### 框架与库

| 技术 | 用途 | 说明 |
|------|------|------|
| **LangChain 1.0** | LLM 应用框架 | `init_chat_model` 统一模型接口、`create_agent` Agent 创建、自定义 Tool 系统 |
| **LangGraph 1.0** | 状态图工作流 | `StateGraph` 编排多 Agent 协作流程、状态管理与节点路由 |
| **LangChain Core** | 消息与提示词 | `SystemMessage`/`HumanMessage`/`AIMessage` 消息体系、`ChatPromptTemplate` 模板引擎 |
| **Pydantic** | 数据验证 | `BaseModel` 类型定义、结构化输出、字段校验 |
| **Python 3.12** | 运行环境 | 类型注解、`TypedDict`、`Literal` 精确类型约束 |

### 核心设计模式

#### 1️⃣ 意图分类器 (Intent Classifier)
- 基于 LLM 的语义理解，识别用户真实意图
- 支持 **4 种意图类型**：技术支持 / 订单服务 / 产品咨询 / 人工升级
- 返回意图类型 + 置信度分数，用于路由决策

#### 2️⃣ 多 Agent 协作架构
- **监督者模式 (Supervisor Pattern)**：中央路由节点负责分发任务
- **专业 Agent 隔离**：每个 Agent 只处理自己领域的问题，互不干扰
- **工具注入**：每个 Agent 绑定专属工具集（订单查询、物流跟踪、产品搜索等）

#### 3️⃣ 质量检查层 (Quality Checker)
- 对 Agent 回复进行自动化质量评估
- 低质量回复自动触发**人工升级**流程
- 形成 **Human-in-the-Loop** 闭环

#### 4️⃣ StateGraph 工作流
```
START → classify_intent → route_to_agent
                          ├── tech_support → tech_support_handler
                          ├── order_service → order_service_handler
                          ├── product_consult → product_consult_handler
                          └── escalate → escalate_handler
                          ↓
                    quality_check → should_escalate? → respond / escalate_final
                                                    → END
```

---

## 💡 核心功能

### 四大服务场景

| 场景 | 能力 | 触发关键词示例 |
|------|------|---------------|
| 🔧 **技术支持** | 设备故障排查、使用指导 | "蓝牙连不上"、"充电慢"、"坏了" |
| 📦 **订单服务** | 订单查询、物流追踪 | "查订单"、"ORD001"、"什么时候到" |
| 🛍️ **产品咨询** | 商品推荐、功能解答 | "推荐手表"、"预算1500"、"有什么功能" |
| 👤 **人工升级** | 投诉处理、经理对接 | "投诉"、"叫经理"、"退款" |

### 亮点特性

- ✅ **Mock 模式** — 无需 API Key 即可本地运行演示，降低入门门槛
- ✅ **可热切换** — 一行代码切换 Mock / 真实 LLM 模式
- ✅ **Mock 数据库** — 内置订单、物流、产品模拟数据，开箱即用
- ✅ **结构化输出** — 所有接口返回标准化 JSON，便于前端集成
- ✅ **容错设计** — JSON 解析安全回退、异常捕获与降级策略

---

## 📊 量化评估报告

> 基于 40 条标注测试用例的自动化评测结果，覆盖 4 种意图类型与 3 个难度等级。
> 评估脚本：phase4_projects/02_multi_agent_support/run_evaluation.py
> 数据集：phase4_projects/02_multi_agent_support/eval_dataset.py

### 总体指标

| 指标 | 得分 | 说明 |
|------|:----:|------|
| **意图分类准确率** (Intent Accuracy) | **85.0%** | 40 条中 34 条意图分类正确 |
| **升级决策准确率** (Escalation Accuracy) | **87.5%** | 是否升级人工的判断准确率 |
| **升级精确率** (Escalation Precision) | **100.0%** | 判为升级的案例中全部正确（零误报） |
| **升级召回率** (Escalation Recall) | **54.5%** | 应升级的案例中有 54.5% 被正确识别 |
| **F1 Score** | **70.6%** | 精确率与召回率的调和平均 |
| **回复关键词覆盖率** (Keyword Coverage) | **54.6%** | 回复中包含期望关键词的比例 |

### 按难度分解

| Difficulty | Cases | Intent Accuracy | Escalation Accuracy | Keyword Coverage |
|:-----------|:-----:|:---------------:|:-------------------:|:----------------:|
| Easy       |  14   |      79%        |        93%          |       50%        |
| Medium     |  21   |      86%        |        90%          |       56%        |
| Hard       |   5   |     100%        |        60%          |       63%        |

### 按场景分解

| 场景 | 用例数 | 意图准确率 | 关键词覆盖率 |
|------|:------:|:----------:|:------------:|
| 🔧 技术支持 (Tech Support) | 12 | **100%** | **76%** |
| 📦 订单服务 (Order Service) | 10 | **90%** | 37% |
| 🛍️ 产品咨询 (Product Consult) | 10 | **70%** | 47% |
| 👤 人工升级 (Escalation) | 8 | **75%** | 54% |

### 混淆矩阵（升级决策）

`
              Predicted ESC    Predicted NOT
Actual YES      TP = 6           FN = 5
Actual NO       FP = 0           TN = 29
`

- **零误报** (FP=0)：系统不会错误地将普通咨询升级为人工
- **主要瓶颈** (FN=5)：部分需要升级的场景未被识别

### 失败案例分析

| 用例 | 期望意图 | 预测意图 | 问题分析 |
|------|----------|----------|----------|
| 我想改一下收货地址 | order_service | product_consult | 地址修改被误判为产品咨询 |
| 无线耳机有什么功能 | product_consult | tech_support | 耳机触发技术支持倾向 |
| 推荐一款性价比高的耳机 | product_consult | tech_support | 推荐/性价比信号被耳机掩盖 |
| 耳机降噪效果怎么样 | product_consult | tech_support | 产品参数问题被判定为技术故障 |
| 我要投诉！这已经是第三次坏了 | escalate | tech_support | 坏了关键词权重高于投诉 |
| 你们客服态度太差了 | escalate | product_consult | 缺少明确投诉关键词 |

### 优化路线图

| 优先级 | 改进项 | 预期提升 | 实现方式 |
|:------:|--------|:--------:|----------|
| **P0** | 升级召回率优化 | 54.5% -> **90%+** | 补充投诉关键词库，增加情感分析信号 |
| **P0** | 产品咨询意图优化 | 70% -> **90%+** | 区分产品参数与故障排查的语义边界 |
| **P1** | 关键词覆盖率提升 | 54.6% -> **85%+** | 优化 Agent Prompt 模板，约束回复结构 |
| **P1** | 接入真实 LLM | 各项 +10~15% | 切换 USE_MOCK = False |
| **P2** | 集成 RAG 知识库 | 新增上下文召回率 | Pinecone / ChromaDB 存储产品文档 |
| **P2** | 添加 Human-in-the-Loop | 降低误判风险 | 低置信度触发人工审核 |

### 评估方法

`ash
cd phase4_projects/02_multi_agent_support
python run_evaluation.py
`

评估框架特点：
- **结构化数据集**：7 字段 TestCase 数据类，支持自动化验证
- **多维度评分**：意图准确率 + 升级决策质量 + 关键词覆盖率
- **分层分析**：按难度和场景分组定位具体短板
- **可复现**：Mock 模式运行，零配置即可复现结果

---
## 🚀 快速开始

```bash
# 1. 克隆
git clone https://github.com/你的用户名/multi-agent-customer-support.git
cd multi-agent-customer-support

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行（默认 Mock 模式，无需 API Key）
python phase4_projects/02_multi_agent_support/main.py
```

## 🔄 模式切换

编辑 `phase4_projects/02_multi_agent_support/main.py` 顶部：

```python
USE_MOCK = True   # ✅ Mock 模式 — 本地运行，零配置
USE_MOCK = False  # 真实 LLM — 需配置 .env API Key
```

## ⚙️ 配置真实 LLM

1. 在 `.env` 中填入 API Key
2. 将 `USE_MOCK` 设为 `False`
3. 支持模型：
   - Groq: `llama-3.3-70b-versatile`
   - OpenAI: `gpt-4o-mini`
   - 其他兼容 OpenAI 格式的模型

---

## 📁 项目结构

```
multi-agent-customer-support/
├── phase4_projects/
│   └── 02_multi_agent_support/
│       ├── main.py           # 主程序（736行完整实现）
│       └── README.md         # 项目文档
├── requirements.txt          # 依赖清单
├── .env.example              # 环境变量模板
└── README.md                 # 本文件
```

### 代码模块划分（main.py）

| 模块 | 行数 | 职责 |
|------|------|------|
| JSON 解析辅助 | L32-66 | `safe_parse_json` 安全解析 |
| 模拟数据库 | L83-145 | 订单、物流、产品 Mock 数据 |
| 工具定义 | L147-244 | 5 个自定义 Tool |
| Agent 定义 | L247-438 | 意图分类器 + 3 个专业 Agent + 质量检查 |
| 工作流编排 | L440-612 | StateGraph 节点与边定义 |
| 主程序 | L613-736 | 测试用例 + 交互模式 |

---

## 📊 与同类项目的对比优势

| 维度 | 本系统 | 一般教程项目 |
|------|--------|------------|
| 架构设计 | 多 Agent 协作 + 监督者模式 | 单 Agent / 简单 Chain |
| 可扩展性 | 新增 Agent 只需加一个节点 | 需要重构代码 |
| 错误处理 | 完整异常捕获 + 降级策略 | 无 |
| 质量保障 | 自动化质量检查 + 人工升级 | 无 |
| 运行模式 | Mock + 真实 LLM 双模式 | 仅真实 LLM |
| 代码质量 | 类型注解 + 中文文档 + 结构化 | 快速原型风格 |

---

## 🔮 扩展方向

- [ ] 接入真实搜索 API（Tavily / DuckDuckGo）
- [ ] 添加 SQLite 持久化存储（`langgraph-checkpoint-sqlite`）
- [ ] 集成 FastAPI 暴露 RESTful 接口
- [ ] 添加 WebSocket 实时推送
- [ ] 接入 Streamlit / Next.js 前端界面
- [ ] 支持多语言（英语、日语等）
- [ ] 添加用户反馈闭环（Feedback Loop）

---

## 📖 学习资源

- [LangChain 1.0 官方文档](https://docs.langchain.com/oss/python/langchain/)
- [LangGraph 1.0 官方文档](https://docs.langchain.com/oss/python/langgraph)
- [LangChain GitHub](https://github.com/langchain-ai/langchain)
- [Groq Console](https://console.groq.com/keys)

---

## 📄 License

MIT License
