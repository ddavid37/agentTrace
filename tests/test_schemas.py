from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from agenttrace.shared.schemas import (
    AgentEvent,
    AgentGoal,
    DecisionType,
    EventType,
    SecurityDecision,
    SecuritySignal,
    ToolRequest,
    ToolResult,
)


def test_optional_event_fields_can_be_omitted() -> None:
    event = AgentEvent(
        trace_id="t1",
        session_id="s1",
        timestamp=datetime.now(UTC),
        agent_id="a1",
        step_number=1,
        event_type=EventType.GOAL_SET,
        goal=AgentGoal(text="summarize the report"),
    )
    assert event.tool_name is None
    assert event.result is None
    assert event.risk_signals == []


def test_security_decision_requires_valid_risk_score() -> None:
    with pytest.raises(ValidationError):
        SecurityDecision(decision=DecisionType.ALLOW, risk_score=1.5, reasons=[])


def test_tool_request_and_result_round_trip() -> None:
    request = ToolRequest(tool_name="read_file", arguments={"path": "/workspace/reports/q1_revenue.txt"})
    result = ToolResult(success=True, output="ok", data_accessed=["/workspace/reports/q1_revenue.txt"])
    assert request.tool_name == "read_file"
    assert result.data_accessed == ["/workspace/reports/q1_revenue.txt"]


def test_signal_severity_bounds() -> None:
    signal = SecuritySignal(
        detector_name="baseline_rules",
        signal_type="test",
        severity=0.0,
        message="none",
    )
    assert signal.signal_id
    with pytest.raises(ValidationError):
        SecuritySignal(
            detector_name="baseline_rules",
            signal_type="test",
            severity=-0.1,
            message="bad",
        )
