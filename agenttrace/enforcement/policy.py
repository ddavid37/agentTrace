"""Policy engine: map security signals to ALLOW / BLOCK / REQUIRE_APPROVAL."""

from __future__ import annotations

from agenttrace.shared.schemas import DecisionType, SecurityDecision, SecuritySignal


class PolicyEngine:
    def __init__(
        self,
        *,
        block_threshold: float = 0.85,
        approval_threshold: float = 0.5,
    ) -> None:
        self.block_threshold = block_threshold
        self.approval_threshold = approval_threshold

    def decide(self, signals: list[SecuritySignal]) -> SecurityDecision:
        related = sorted({event_id for signal in signals for event_id in signal.related_event_ids})
        risk_score = max((signal.severity for signal in signals), default=0.0)
        reasons = [signal.message for signal in signals]

        if risk_score >= self.block_threshold:
            decision = DecisionType.BLOCK
        elif risk_score >= self.approval_threshold:
            decision = DecisionType.REQUIRE_APPROVAL
        else:
            decision = DecisionType.ALLOW
            if not reasons:
                reasons = ["No security signals above threshold."]

        return SecurityDecision(
            decision=decision,
            risk_score=risk_score,
            reasons=reasons,
            related_event_ids=related,
            signals=signals,
        )
