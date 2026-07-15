"""Stateful troubleshooting loop used by the demo UI.

This module keeps the long-running support state separate from retrieval.  It
remembers the detected model and evidence already shown, avoids repeating a
step, and escalates risky or exhausted sessions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from uuid import uuid4

from device_rag import DeviceKnowledgeBase, SearchResult


@dataclass
class TroubleshootingState:
    session_id: str
    model: str | None = None
    turn_count: int = 0
    attempted_document_ids: list[str] = field(default_factory=list)
    status: str = "diagnosing"  # diagnosing / resolved / escalated
    escalation_reason: str = ""


@dataclass
class TroubleshootingReply:
    message: str
    state: TroubleshootingState
    evidence: list[SearchResult] = field(default_factory=list)


class TroubleshootingManager:
    RESOLVED_SIGNALS = ("解决了", "好了", "恢复了", "可以用了", "正常了")

    def __init__(self, knowledge_base: DeviceKnowledgeBase | None = None, max_turns: int = 3):
        self.knowledge_base = knowledge_base or DeviceKnowledgeBase()
        self.max_turns = max_turns
        self.sessions: dict[str, TroubleshootingState] = {}

    def create_session(self) -> TroubleshootingState:
        state = TroubleshootingState(session_id=str(uuid4()))
        self.sessions[state.session_id] = state
        return state

    def get_state(self, session_id: str) -> TroubleshootingState:
        if session_id not in self.sessions:
            self.sessions[session_id] = TroubleshootingState(session_id=session_id)
        return self.sessions[session_id]

    def handle(self, session_id: str, message: str) -> TroubleshootingReply:
        state = self.get_state(session_id)
        if state.status != "diagnosing":
            return TroubleshootingReply("当前排障已结束，请新建会话处理其他问题。", state)

        if any(signal in message for signal in self.RESOLVED_SIGNALS):
            state.status = "resolved"
            return TroubleshootingReply("已记录问题解决。建议观察一段时间，如再次出现请携带本次记录联系售后。", state)

        detected_model = self.knowledge_base.detect_model(message)
        if detected_model:
            matching = next(
                (doc.model for doc in self.knowledge_base.documents if self.knowledge_base.normalize_model(doc.model) == detected_model),
                None,
            )
            state.model = matching

        if not state.model:
            return TroubleshootingReply(
                "请先告诉我产品型号：EarPro、EarLite、WatchPro、WatchS、Band5 或 Band6。",
                state,
            )

        results = self.knowledge_base.search(message, model=state.model, top_k=5)
        unseen = [result for result in results if result.document.id not in state.attempted_document_ids]
        if not unseen:
            state.status = "escalated"
            state.escalation_reason = "没有新的可靠排查证据"
            return TroubleshootingReply("没有检索到新的可靠步骤，已建议转人工售后。", state)

        selected = unseen[0]
        state.turn_count += 1
        state.attempted_document_ids.append(selected.document.id)

        if selected.document.risk_level == "high":
            state.status = "escalated"
            state.escalation_reason = "命中高风险安全规则"
            message_text = (
                f"⚠️ {selected.document.content}\n\n依据：{selected.citation}\n"
                "该情况不适合远程继续操作，已建议立即停止使用并转人工售后。"
            )
        else:
            message_text = (
                f"第 {state.turn_count} 步：{selected.document.content}\n\n"
                f"依据：{selected.citation}\n完成后请回复“解决了”，或描述新的现象。"
            )
            if state.turn_count >= self.max_turns:
                state.status = "escalated"
                state.escalation_reason = "达到最大自动排障轮数"
                message_text += "\n\n已达到自动排障上限，若仍未解决请转人工售后。"

        return TroubleshootingReply(message_text, state, [selected])

    def snapshot(self, session_id: str) -> dict:
        return asdict(self.get_state(session_id))
