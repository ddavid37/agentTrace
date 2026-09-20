"""Session loop connecting goal, agent, executor, telemetry, and enforcement."""

from __future__ import annotations

from dataclasses import dataclass, field

from agenttrace.agent.executor import (
    AllowApprovals,
    ApprovalHandler,
    DenyApprovals,
    ExecutionOutcome,
    GuardedExecutor,
)
from agenttrace.agent.scripted import AgentFinish
from agenttrace.detection.base import Detector
from agenttrace.enforcement.policy import PolicyEngine
from agenttrace.shared.schemas import (
    AgentGoal,
    AgentIdentity,
    AgentTrajectory,
    EventType,
    SecurityDecision,
    ToolRequest,
)
from agenttrace.telemetry.tracer import Tracer
from agenttrace.tools.base import ToolRegistry
from agenttrace.tools.environment import SyntheticEnvironment


@dataclass
class SessionResult:
    trajectory: AgentTrajectory
    outcomes: list[ExecutionOutcome] = field(default_factory=list)
    final_message: str | None = None

    def decisions(self) -> list[SecurityDecision]:
        return [outcome.decision for outcome in self.outcomes]


class AgentLoop:
    def __init__(
        self,
        *,
        identity: AgentIdentity,
        environment: SyntheticEnvironment,
        registry: ToolRegistry,
        detector: Detector,
        policy: PolicyEngine,
        approval_handler: ApprovalHandler | None = None,
        max_steps: int = 12,
    ) -> None:
        self.identity = identity
        self.environment = environment
        self.registry = registry
        self.detector = detector
        self.policy = policy
        self.approval_handler = approval_handler or DenyApprovals()
        self.max_steps = max_steps

    def run(self, goal: AgentGoal, agent: object) -> SessionResult:
        tracer = Tracer(identity=self.identity, environment=self.environment.name)
        tracer.emit(EventType.GOAL_SET, goal=goal)
        executor = GuardedExecutor(
            tracer=tracer,
            registry=self.registry,
            environment=self.environment,
            detector=self.detector,
            policy=self.policy,
            approval_handler=self.approval_handler,
        )
        outcomes: list[ExecutionOutcome] = []
        observation: ExecutionOutcome | None = None
        final_message: str | None = None

        for _ in range(self.max_steps):
            action = agent.next_action(observation)
            if isinstance(action, AgentFinish):
                final_message = action.summary
                tracer.emit(EventType.AGENT_MESSAGE, model_output=action.summary)
                break
            if not isinstance(action, ToolRequest):
                raise TypeError(f"agent returned unsupported action: {type(action)}")
            observation = executor.execute(action)
            outcomes.append(observation)
            if not observation.executed:
                final_message = f"Stopped by policy: {observation.decision.decision.value}"
                tracer.emit(EventType.AGENT_MESSAGE, model_output=final_message)
                break

        tracer.emit(EventType.SESSION_END)
        return SessionResult(
            trajectory=tracer.trajectory(),
            outcomes=outcomes,
            final_message=final_message,
        )


def approval_handler_from_mode(mode: str) -> ApprovalHandler:
    if mode == "allow":
        return AllowApprovals()
    return DenyApprovals()
