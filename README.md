<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python" />
  <img src="https://img.shields.io/badge/LangChain-1.0-green" />
  <img src="https://img.shields.io/badge/LangGraph-1.0-purple" />
  <img src="https://img.shields.io/badge/Architecture-Multi--Agent-orange" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" />
</p>

---

# 🤖 Multi-Agent Customer Support System

> **电子产品多智能体客服原型** — 基于 LangChain 1.0 + LangGraph 1.0，加入型号感知的本地混合 RAG

---

## 📋 项目简介

本项目实现了一个面向蓝牙耳机、智能手表和智能手环的**多 Agent 客服原型**。系统根据用户意图调用技术支持、订单服务或产品咨询能力，并在低置信度、证据不足及高风险场景下升级人工客服。

技术支持 Agent 不再依赖固定 FAQ：它会识别产品型号，对说明书和故障排查资料进行 BM25 + 字符级 TF-IDF 混合检索；安装可选依赖后还可启用 BGE Dense Embedding。检索经过型号 Metadata 过滤后返回带章节、页码和相关度的证据。当前知识库为可复现的模拟资料，后续可替换为真实产品手册。

### RAG 设计亮点

- **型号隔离**：EarPro、EarLite、WatchPro、WatchS、Band5、Band6 的操作说明不会串用。
- **混合检索**：BM25负责型号等精确信号，TF-IDF提供离线语义基线，可选BGE Embedding处理复杂口语。
- **证据引用**：每条结果包含文档、章节、页码与相关度，便于客服核验。
- **安全升级**：电池鼓包、进水充电、拆机等高风险内容强制标记转人工。
- **多轮排障状态**：记录型号、排障轮数和已使用证据，避免重复步骤；解决、高风险或达到上限时终止。
- **离线可评测**：36条文档、36条查询的模拟集上，Recall@1 97.2%、Recall@3 100%、MRR 0.986、型号串扰为0。

```bash
python phase4_projects/02_multi_agent_support/run_rag_evaluation.py
```

### 可视化演示

```bash
pip install -r requirements-demo.txt
streamlit run phase4_projects/02_multi_agent_support/streamlit_app.py
```

界面会展示当前产品型号、排障轮数、已经使用的证据、文档页码、相关度及人工升级原因。

可选运行 BGE 检索评测（首次运行会下载模型）：

```bash
pip install -r requirements-embedding.txt
python phase4_projects/02_multi_agent_support/run_rag_evaluation.py --embedding
```

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
| **意图分类准确率** (Intent Accuracy) | **100.0%** | Mock规则在40条当前测试集上的结果，不代表线上泛化能力 |
| **升级决策准确率** (Escalation Accuracy) | **92.5%** | 是否升级人工的判断准确率 |
| **升级精确率** (Escalation Precision) | **100.0%** | 判为升级的案例中全部正确（零误报） |
| **升级召回率** (Escalation Recall) | **72.7%** | 应升级案例的识别率，仍是下一阶段重点 |
| **F1 Score** | **84.2%** | 精确率与召回率的调和平均 |
| **回复关键词覆盖率** (Keyword Coverage) | **40.4%** | 旧指标；RAG要求先补充型号后，固定关键词覆盖率不再适合作为主指标 |

### 按难度分解

| Difficulty | Cases | Intent Accuracy | Escalation Accuracy | Keyword Coverage |
|:-----------|:-----:|:---------------:|:-------------------:|:----------------:|
| Easy       |  14   |     100%        |       100%          |       50%        |
| Medium     |  21   |     100%        |        95%          |       33%        |
| Hard       |   5   |     100%        |        60%          |       43%        |

### 按场景分解

| 场景 | 用例数 | 意图准确率 | 关键词覆盖率 |
|------|:------:|:----------:|:------------:|
| 🔧 技术支持 (Tech Support) | 12 | **100%** | 0%* |
| 📦 订单服务 (Order Service) | 10 | **100%** | 42% |
| 🛍️ 产品咨询 (Product Consult) | 10 | **100%** | 67% |
| 👤 人工升级 (Escalation) | 8 | **100%** | 67% |

\* 技术支持现在会在缺少型号时追问，而旧数据集期待直接给出通用步骤；请以独立RAG评测为准。

### 混淆矩阵（升级决策）

`
              Predicted ESC    Predicted NOT
Actual YES      TP = 8           FN = 3
Actual NO       FP = 0           TN = 29
`

- **零误报** (FP=0)：系统不会错误地将普通咨询升级为人工
- **主要瓶颈** (FN=3)：部分多轮失败场景仍需引入会话状态才能正确升级

### 当前局限

- 当前意图分类高分来自小型Mock测试集，需要接入真实LLM并扩充对抗样本验证。
- 多轮状态目前保存在进程内，服务重启后不会恢复；生产环境需接入SQLite或Redis Checkpointer。
- 知识库为36条模拟手册片段，不能把当前检索结果直接作为线上收益。
- BGE为可选后端，默认离线模式仍使用BM25 + TF-IDF，便于零配置复现。

### 优化路线图

| 优先级 | 改进项 | 预期提升 | 实现方式 |
|:------:|--------|:--------:|----------|
| **P0** | 导入真实说明书 | 验证真实泛化能力 | PDF结构化解析、页码保留和对抗样本 |
| **P0** | 状态持久化 | 支持服务恢复 | LangGraph Checkpointer + SQLite/Redis |
| **P1** | BGE消融实验 | 验证复杂口语收益 | 对比BM25、TF-IDF、BGE及混合方案 |
| **P1** | 接入真实LLM评测 | 替代Mock规则结论 | 切换 USE_MOCK = False 并保存运行轨迹 |
| **P2** | Human-in-the-Loop持久化 | 降低敏感操作风险 | LangGraph interrupt + SQLite checkpointer |

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
- [x] 接入 Streamlit 演示界面
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
