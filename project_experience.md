# 项目经历：多智能体客服系统 (Multi-Agent Customer Support System)

---

## 项目概述

**项目名称**：基于 LangChain + LangGraph 的多智能体协作客服系统
**项目时间**：2025 年 6 月 — 2025 年 7 月
**技术栈**：Python 3.12 / LangChain 1.0 / LangGraph 1.0 / Pydantic / StateGraph / FastAPI（规划中）
**项目地址**：[github.com/fenghaojin880818-lgtm/multi-agent-customer-support](https://github.com/fenghaojin880818-lgtm/multi-agent-customer-support)

---

## 项目背景

独立设计并实现了一套**多智能体协作的智能客服系统**。不同于市面上常见的单 Agent 或简单 Chain 架构，本项目采用**监督者模式 (Supervisor Pattern)**，由中央意图分类器统一调度多个专业领域 Agent 协作完成任务，并配备**质量检查层**进行输出质量监控与人工升级决策。项目动机源于对当前 AI Agent 行业落地模式的探索——参考了 OpenAI、Anthropic 等公司在其产品中采用的多 Agent 协作架构。

---

## 个人职责与技术实现

### 1. 系统架构设计与工作流编排
- 使用 **LangGraph 1.0 的 StateGraph** 构建有状态的工作流引擎，定义了 `classify_intent → route → [tech_support | order_service | product_consult | escalate] → quality_check → respond / escalate_final` 的完整链路
- **6 个 StateGraph 节点 + 7 条条件边** 实现灵活的路由逻辑
- 利用 `TypedDict` / `Literal` 做类型约束，确保状态传递的类型安全

### 2. 意图分类器 (Intent Classifier) 开发
- 基于 LLM 调用（支持 Mock 模式）实现 **4 意图分类**：技术支持、订单服务、产品咨询、人工升级
- 返回意图标签 + 置信度分数，为下游路由决策提供依据
- **Mock 模式下 40 条测试集意图分类准确率达 85.0%**

### 3. 多 Agent 路由与工具集成
- 实现 **3 个专业 Agent**（技术支持 Agent、订单服务 Agent、产品咨询 Agent），每个 Agent 绑定专属工具集
- 开发 **5 个自定义 LangChain Tool**：`get_order_status`（订单查询）、`track_logistics`（物流跟踪）、`search_products`（产品搜索）、`get_product_detail`（产品详情）、`get_order_detail`（订单明细）
- Agent 间**完全隔离**，每个 Agent 只处理自身领域的问题，降低上下文干扰

### 4. 质量检查与升级决策 (Quality Checker)
- 实现自动化质量检查层，对 Agent 回复进行 **0-1 分质量评分**
- 低质量回复自动触发 **Human-in-the-Loop 升级流程**
- **升级决策精确率达 100.0%**（零误报），F1 Score 70.6%

### 5. 评测体系建设
- 构建 **40 条标注测试用例**，覆盖 4 种意图 × 3 个难度等级（easy / medium / hard）
- 实现自动化评测脚本，从 **意图准确率、升级决策质量、关键词覆盖率** 三个维度量化系统表现
- 支持**按难度分组**和**按场景分组**的细粒度分析，定位具体短板

---

## 量化成果

### 系统性能指标

| 指标 | 当前值 | 说明 |
|------|:------:|------|
| 意图分类准确率 | **85.0%** | 40 条测试用例中 34 条分类正确 |
| 升级决策精确率 | **100.0%** | 判为升级的案例零误报 |
| 升级决策召回率 | **54.5%** | 需优化，已制定改进方案 |
| F1 Score | **70.6%** | 精确率与召回率的调和平均 |
| 关键词覆盖率 | **54.6%** | Agent 回复的信息完整性 |

### 评估驱动的优化路径

通过构建评测体系，系统性地识别出以下瓶颈并提出优化方案：

1. **升级召回率仅 54.5%** → 分析发现 5 个漏报案例集中在投诉处理和订单修改场景，计划通过补充情感关键词库和优先级调整提升至 90%+
2. **产品咨询意图准确率仅 70%** → 主要混淆发生在"耳机"类产品（被误判为技术支持），计划通过优化意图边界区分"功能咨询"与"故障排查"
3. **技术支持场景表现最佳**（意图准确率 100%）→ 验证了该场景的分类规则设计合理，可复用至其他场景
4. **关键词覆盖率 54.6%** → Agent Prompt 缺乏回复内容约束，计划通过模板优化提升至 85%+

---

## 项目亮点

| 维度 | 说明 |
|------|------|
| **工程化设计** | 支持 Mock / 真实 LLM 双模式热切换，Mock 模式零配置即可运行，降低演示和调试门槛 |
| **评估驱动** | 构建完整评测流水线，40 条标注用例 + 多维度自动化评分，可量化追踪优化效果 |
| **容错机制** | JSON 安全解析回退 + 异常捕获降级策略，确保极端输入下系统稳定运行 |
| **代码规范** | 完整类型注解（TypedDict / Literal / Optional）、结构化模块划分（736 行代码） |
| **可扩展性** | 新增 Agent 只需添加一个 StateGraph 节点，无需重构现有逻辑 |

---

## 技术关键词

`LangChain` `LangGraph` `Multi-Agent` `StateGraph` `Intent Classification` `Tool Calling` `Supervisor Pattern` `Human-in-the-Loop` `Quality Check` `LLM` `Prompt Engineering` `Evaluation-Driven Development` `Python` `Pydantic` `RESTful`

---

## 对岗位的匹配说明

| JD 要求 | 本项目匹配点 |
|---------|------------|
| Agent 工作流开发（数据获取→处理→推理→输出） | 完整实现 classify→route→handle→check→respond 全链路 |
| LangChain / LangGraph 框架 | 核心框架，使用 StateGraph 编排 + create_agent + Tool 系统 |
| 工具调用 (Function Call / Tool Calling) | 5 个自定义 Tool，Agent 按需绑定调用 |
| RAG / 知识库构建 | 已有 Mock 数据库和产品数据层，可扩展为向量检索（规划中） |
| Prompt 工程与调优 | 每个 Agent 单独设计 Prompt，评测驱动持续优化 |
| 评估意识 / 指标量化 | 完整评测体系：40 条用例 × 3 维度 × 分层分析 |
| 工程化能力（Python） | 736 行结构化代码，类型注解 + 异常处理 + 双模式切换 |

---

## 项目截图 / Demo

```bash
# 克隆并运行（Mock 模式，无需 API Key）
git clone https://github.com/fenghaojin880818-lgtm/multi-agent-customer-support.git
cd multi-agent-customer-support
pip install -r requirements.txt
python phase4_projects/02_multi_agent_support/main.py

# 运行评测
python phase4_projects/02_multi_agent_support/run_evaluation.py
```
