"""
multi_agent_customer_support/eval_dataset.py

评测数据集 - 包含 40 个标注测试用例，覆盖 4 种意图及边界情况
"""
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class TestCase:
    id: str
    query: str
    expected_intent: str          # 期望意图
    expected_keywords: List[str]  # 回复中应出现的关键词
    should_escalate: bool         # 是否应该升级人工
    difficulty: str               # easy / medium / hard
    category: str                 # 场景分类

# ==================== 评测数据集（40条）====================

EVAL_DATASET = [
    # ========== 技术支持（12条）==========
    TestCase("T001", "我的蓝牙耳机连不上手机了", "tech_support",
             ["蓝牙", "重启", "检查"], False, "easy", "连接问题"),
    TestCase("T002", "手表充电充不进去", "tech_support",
             ["充电", "电量"], False, "easy", "充电问题"),
    TestCase("T003", "耳机一边没声音了怎么办", "tech_support",
             ["重启", "检查"], False, "medium", "设备故障"),
    TestCase("T004", "智能手表屏幕触摸不灵敏", "tech_support",
             ["重启", "检查"], False, "medium", "设备故障"),
    TestCase("T005", "手机连不上蓝牙耳机，已经重启过了还是不行", "tech_support",
             ["联系", "人工"], True, "hard", "连接问题"),
    TestCase("T006", "耳机充电盒指示灯不亮", "tech_support",
             ["充电", "检查", "电量"], False, "medium", "充电问题"),
    TestCase("T007", "手表的表带怎么换", "tech_support",
             ["联系", "人工"], False, "medium", "使用问题"),
    TestCase("T008", "耳机连接后声音断断续续", "tech_support",
             ["重启", "蓝牙", "检查"], False, "medium", "连接问题"),
    TestCase("T009", "App显示设备离线怎么办", "tech_support",
             ["重启", "检查"], False, "medium", "软件问题"),
    TestCase("T010", "充电线丢了能用别的充电器吗", "tech_support",
             ["充电", "检查"], False, "easy", "配件问题"),
    TestCase("T011", "设备系统怎么更新", "tech_support",
             ["App", "检查"], False, "medium", "软件问题"),
    TestCase("T012", "耳机防水吗？能戴着跑步吗", "tech_support",
             ["防护", "等级"], False, "easy", "产品参数"),

    # ========== 订单服务（10条）==========
    TestCase("O001", "帮我查一下订单ORD001的物流", "order_service",
             ["订单", "物流", "发货", "ORD001"], False, "easy", "物流查询"),
    TestCase("O002", "ORD002什么时候能到", "order_service",
             ["订单", "ORD002", "预计"], False, "easy", "物流查询"),
    TestCase("O003", "我想改一下收货地址", "order_service",
             ["订单", "人工"], True, "medium", "订单修改"),
    TestCase("O004", "怎么申请退货", "order_service",
             ["退货", "客服"], False, "medium", "售后服务"),
    TestCase("O005", "订单ORD003怎么还没发货", "order_service",
             ["订单", "ORD003", "发货"], False, "easy", "物流查询"),
    TestCase("O006", "我买的东西少发了一件", "order_service",
             ["订单", "人工"], True, "hard", "售后问题"),
    TestCase("O007", "能帮我查查顺丰快递SF123的单号吗", "order_service",
             ["物流", "快递", "SF123"], False, "medium", "物流查询"),
    TestCase("O008", "退款什么时候到账", "order_service",
             ["退款", "客服"], False, "medium", "退款问题"),
    TestCase("O009", "订单怎么拆分发货", "order_service",
             ["订单", "客服"], False, "hard", "订单修改"),
    TestCase("O010", "发票怎么开", "order_service",
             ["订单", "客服"], False, "medium", "售后服务"),

    # ========== 产品咨询（10条）==========
    TestCase("P001", "想买个智能手表，预算1500左右", "product_consult",
             ["推荐", "手表", "Pro"], False, "easy", "产品推荐"),
    TestCase("P002", "无线耳机有什么功能", "product_consult",
             ["推荐", "耳机", "功能"], False, "easy", "产品咨询"),
    TestCase("P003", "你们有适合运动的手环吗", "product_consult",
             ["推荐", "手环", "运动"], False, "medium", "产品推荐"),
    TestCase("P004", "智能手表能测心率吗", "product_consult",
             ["功能", "手表"], False, "easy", "功能咨询"),
    TestCase("P005", "推荐一款性价比高的耳机", "product_consult",
             ["推荐", "耳机"], False, "easy", "产品推荐"),
    TestCase("P006", "手环的续航怎么样", "product_consult",
             ["推荐", "手环"], False, "medium", "产品参数"),
    TestCase("P007", "你们的产品和某某品牌比哪个好", "product_consult",
             ["推荐", "对比"], False, "hard", "产品对比"),
    TestCase("P008", "有没有适合送人的智能设备", "product_consult",
             ["推荐", "礼物"], False, "medium", "产品推荐"),
    TestCase("P009", "手表有粉色的吗", "product_consult",
             ["推荐", "颜色"], False, "medium", "产品参数"),
    TestCase("P010", "耳机降噪效果怎么样", "product_consult",
             ["推荐", "功能", "降噪"], False, "medium", "功能咨询"),

    # ========== 人工升级（8条）==========
    TestCase("E001", "我要投诉！这已经是第三次坏了", "escalate",
             ["转接", "人工", "专员"], True, "easy", "投诉处理"),
    TestCase("E002", "叫你们经理过来", "escalate",
             ["转接", "人工", "专员"], True, "easy", "投诉处理"),
    TestCase("E003", "你们什么破质量，我要退款", "escalate",
             ["转接", "人工", "专员"], True, "medium", "退款纠纷"),
    TestCase("E004", "你们就是骗人的", "escalate",
             ["转接", "人工", "专员"], True, "medium", "投诉处理"),
    TestCase("E005", "我要找你们领导谈谈", "escalate",
             ["转接", "人工", "专员"], True, "easy", "投诉处理"),
    TestCase("E006", "不给解决我就去12315投诉", "escalate",
             ["转接", "人工", "专员"], True, "hard", "投诉处理"),
    TestCase("E007", "你们客服态度太差了", "escalate",
             ["转接", "人工", "专员"], True, "medium", "服务投诉"),
    TestCase("E008", "我要求全额赔偿", "escalate",
             ["转接", "人工", "专员"], True, "medium", "赔偿要求"),
]
