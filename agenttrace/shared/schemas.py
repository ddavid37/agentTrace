"""Typed schemas for AgentTrace trajectories and security decisions.

Fields that do not apply to every event are optional. The design goal is that
an ordered list of AgentEvent records can reconstruct what the agent was doing
over time, including goal, tools, data access, and prior risk signals.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def new_id() -> str:
    return uuid4().hex


class EventType(str, Enum):
    GOAL_SET = "goal_set"
    TOOL_REQUEST = "tool_request"
    TOOL_RESULT = "tool_result"
    POLICY_DECISION = "policy_decision"
    AGENT_MESSAGE = "agent_message"
    SESSION_END = "session_end"


class DecisionType(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class AgentGoal(BaseModel):
    text: str
    task_scope: list[str] = Field(default_factory=list)


class AgentIdentity(BaseModel):
    agent_id: str
    role: str = "research_agent"
    permissions: list[str] = Field(default_factory=list)


class ToolRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    planned_next_action: str | None = None


class ToolResult(BaseModel):
    success: bool
    output: Any = None
    error: str | None = None
    data_accessed: list[str] = Field(default_factory=list)
    executed: bool = True


class SecuritySignal(BaseModel):
    signal_id: str = Field(default_factory=new_id)
    detector_name: str
    signal_type: str
    severity: float = Field(ge=0.0, le=1.0)
    message: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    related_event_ids: list[str] = Field(default_factory=list)


class SecurityDecision(BaseModel):
    decision: DecisionType
    risk_score: float = Field(ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)
    related_event_ids: list[str] = Field(default_factory=list)
    signals: list[SecuritySignal] = Field(default_factory=list)


class AgentEvent(BaseModel):
    event_id: str = Field(default_factory=new_id)
    trace_id: str
    session_id: str
    timestamp: datetime
    agent_id: str
    step_number: int
    event_type: EventType
    previous_event_id: str | None = None
    goal: AgentGoal | None = None
    identity: AgentIdentity | None = None
    environment: str | None = None
    tool_name: str | None = None
    tool_arguments: dict[str, Any] | None = None
    data_accessed: list[str] | None = None
    model_output: str | None = None
    result: ToolResult | None = None
    risk_signals: list[SecuritySignal] = Field(default_factory=list)
    security_decision: SecurityDecision | None = None


class AgentTrajectory(BaseModel):
    trace_id: str
    session_id: str
    goal: AgentGoal | None = None
    identity: AgentIdentity | None = None
    environment: str | None = None
    events: list[AgentEvent] = Field(default_factory=list)

    def ordered_events(self) -> list[AgentEvent]:
        """Return events in causal order via previous_event_id, then step number."""
        if not self.events:
            return []
        successors: dict[str | None, list[AgentEvent]] = {}
        for event in self.events:
            successors.setdefault(event.previous_event_id, []).append(event)
        for group in successors.values():
            group.sort(key=lambda item: item.step_number)

        ordered: list[AgentEvent] = []
        visited: set[str] = set()
        queue = list(successors.get(None, []))
        while queue:
            current = queue.pop(0)
            if current.event_id in visited:
                continue
            visited.add(current.event_id)
            ordered.append(current)
            queue.extend(successors.get(current.event_id, []))

        missing = [event for event in self.events if event.event_id not in visited]
        missing.sort(key=lambda item: item.step_number)
        ordered.extend(missing)
        return ordered

    def last_event(self) -> AgentEvent | None:
        ordered = self.ordered_events()
        return ordered[-1] if ordered else None

    @staticmethod
    def from_events(
        events: list[AgentEvent],
        *,
        trace_id: str | None = None,
        session_id: str | None = None,
    ) -> AgentTrajectory:
        if not events:
            return AgentTrajectory(
                trace_id=trace_id or new_id(),
                session_id=session_id or new_id(),
            )
        first = events[0]
        goal = next((event.goal for event in events if event.goal is not None), None)
        identity = next((event.identity for event in events if event.identity is not None), None)
        environment = next((event.environment for event in events if event.environment), None)
        return AgentTrajectory(
            trace_id=trace_id or first.trace_id,
            session_id=session_id or first.session_id,
            goal=goal,
            identity=identity,
            environment=environment,
            events=events,
        )
