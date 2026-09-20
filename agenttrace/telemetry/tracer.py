"""In-memory event tracer and trajectory reconstruction."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from agenttrace.shared.schemas import (
    AgentEvent,
    AgentGoal,
    AgentIdentity,
    AgentTrajectory,
    EventType,
    SecurityDecision,
    SecuritySignal,
    ToolResult,
    new_id,
)


class InMemoryTraceStore:
    def __init__(self) -> None:
        self._events: list[AgentEvent] = []

    def append(self, event: AgentEvent) -> None:
        self._events.append(event)

    def events(self) -> list[AgentEvent]:
        return list(self._events)


class Tracer:
    """Records a linked sequence of AgentEvent records for one session."""

    def __init__(
        self,
        identity: AgentIdentity,
        environment: str,
        *,
        trace_id: str | None = None,
        session_id: str | None = None,
        store: InMemoryTraceStore | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.identity = identity
        self.environment = environment
        self.trace_id = trace_id or new_id()
        self.session_id = session_id or new_id()
        self.store = store or InMemoryTraceStore()
        self._clock = clock or (lambda: datetime.now(UTC))
        self._step = 0
        self._previous_event_id: str | None = None
        self._goal: AgentGoal | None = None

    def emit(
        self,
        event_type: EventType,
        *,
        goal: AgentGoal | None = None,
        tool_name: str | None = None,
        tool_arguments: dict[str, Any] | None = None,
        data_accessed: list[str] | None = None,
        model_output: str | None = None,
        result: ToolResult | None = None,
        risk_signals: list[SecuritySignal] | None = None,
        security_decision: SecurityDecision | None = None,
    ) -> AgentEvent:
        self._step += 1
        if goal is not None:
            self._goal = goal
        event = AgentEvent(
            trace_id=self.trace_id,
            session_id=self.session_id,
            timestamp=self._clock(),
            agent_id=self.identity.agent_id,
            step_number=self._step,
            event_type=event_type,
            previous_event_id=self._previous_event_id,
            goal=self._goal,
            identity=self.identity,
            environment=self.environment,
            tool_name=tool_name,
            tool_arguments=tool_arguments,
            data_accessed=data_accessed,
            model_output=model_output,
            result=result,
            risk_signals=risk_signals or [],
            security_decision=security_decision,
        )
        self.store.append(event)
        self._previous_event_id = event.event_id
        return event

    def trajectory(self) -> AgentTrajectory:
        return AgentTrajectory.from_events(
            self.store.events(),
            trace_id=self.trace_id,
            session_id=self.session_id,
        )
