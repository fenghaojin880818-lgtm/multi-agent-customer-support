"""Streamlit demo for the stateful electronic-device support agent."""

import streamlit as st

from device_rag import DeviceKnowledgeBase
from troubleshooting import TroubleshootingManager


st.set_page_config(page_title="DeviceCare Agent", page_icon="🛠️", layout="wide")
st.title("🛠️ DeviceCare 电子产品售后 Agent")
st.caption("型号感知 RAG · 证据引用 · 多轮排障 · 高风险转人工")

if "manager" not in st.session_state:
    st.session_state.manager = TroubleshootingManager(DeviceKnowledgeBase())
if "support_session" not in st.session_state:
    st.session_state.support_session = st.session_state.manager.create_session().session_id
if "messages" not in st.session_state:
    st.session_state.messages = []

manager: TroubleshootingManager = st.session_state.manager
session_id: str = st.session_state.support_session

with st.sidebar:
    st.subheader("Agent 状态")
    state = manager.snapshot(session_id)
    st.json(state)
    st.caption(f"检索后端：{manager.knowledge_base.retrieval_backend}")
    st.caption(f"知识片段：{len(manager.knowledge_base.documents)} 条")
    if st.button("新建排障会话", use_container_width=True):
        st.session_state.support_session = manager.create_session().session_id
        st.session_state.messages = []
        st.rerun()

for item in st.session_state.messages:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])
        if item.get("evidence"):
            with st.expander("查看检索证据"):
                st.json(item["evidence"])

if prompt := st.chat_input("例如：WatchPro 后盖鼓起来而且发热"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reply = manager.handle(session_id, prompt)
    evidence = [
        {
            "document_id": result.document.id,
            "model": result.document.model,
            "section": result.document.section,
            "page": result.document.page,
            "risk_level": result.document.risk_level,
            "score": result.score,
        }
        for result in reply.evidence
    ]
    st.session_state.messages.append(
        {"role": "assistant", "content": reply.message, "evidence": evidence}
    )
    with st.chat_message("assistant"):
        st.markdown(reply.message)
        if evidence:
            with st.expander("查看检索证据"):
                st.json(evidence)
    st.rerun()
