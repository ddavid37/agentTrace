from agenttrace.enforcement.policy import PolicyEngine
from agenttrace.shared.schemas import DecisionType, SecuritySignal


def test_no_signals_allow() -> None:
    decision = PolicyEngine().decide([])
    assert decision.decision == DecisionType.ALLOW
    assert decision.risk_score == 0.0
    assert decision.reasons


def test_mid_severity_requires_approval() -> None:
    decision = PolicyEngine().decide(
        [
            SecuritySignal(
                detector_name="baseline_rules",
                signal_type="sensitive_access",
                severity=0.55,
                message="credential-like access",
                related_event_ids=["e1"],
            )
        ]
    )
    assert decision.decision == DecisionType.REQUIRE_APPROVAL
    assert decision.related_event_ids == ["e1"]
    assert "credential-like access" in decision.reasons


def test_high_severity_blocks() -> None:
    decision = PolicyEngine().decide(
        [
            SecuritySignal(
                detector_name="baseline_rules",
                signal_type="post_injection_sensitive_access",
                severity=0.93,
                message="redirect after untrusted content",
                related_event_ids=["e2"],
            )
        ]
    )
    assert decision.decision == DecisionType.BLOCK
    assert decision.risk_score == 0.93
