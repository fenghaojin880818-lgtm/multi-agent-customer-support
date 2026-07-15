"""Deterministic checks for multi-turn state, safety and non-repetition."""

from troubleshooting import TroubleshootingManager


def main() -> None:
    manager = TroubleshootingManager(max_turns=3)

    missing_model = manager.create_session()
    reply = manager.handle(missing_model.session_id, "耳机一边没声音")
    assert "产品型号" in reply.message and reply.state.turn_count == 0

    safe = manager.create_session()
    first = manager.handle(safe.session_id, "EarPro一边没声音")
    assert first.state.model == "EarPro"
    assert first.evidence[0].document.id == "earpro-audio-01"
    second = manager.handle(safe.session_id, "还是没有声音")
    assert second.evidence[0].document.id != first.evidence[0].document.id
    resolved = manager.handle(safe.session_id, "已经解决了")
    assert resolved.state.status == "resolved"

    dangerous = manager.create_session()
    risky = manager.handle(dangerous.session_id, "WatchPro后盖鼓起来发热")
    assert risky.state.status == "escalated"
    assert risky.evidence[0].document.risk_level == "high"

    print("PASS missing-model clarification")
    print("PASS stateful non-repeating troubleshooting")
    print("PASS resolved-state termination")
    print("PASS high-risk forced escalation")


if __name__ == "__main__":
    main()
