"""Guarded executor: the only path from a tool request to a tool implementation."""

from __future__ import annotations

from dataclasses import dataclass

from agenttrace.detection.base import Detector
from agenttrace.enforcement.policy import PolicyEngine
from agenttrace.shared.schemas import (
    DecisionType,
    EventType,
    SecurityDecision,
    ToolRequest,
    ToolResult,
)
from agenttrace.telemetry.tracer import Tracer
from agenttrace.tools.base import ToolRegistry
from agenttrace.tools.environment import SyntheticEnvironment


@dataclass
class ExecutionOutcome:
    request: ToolRequest
    decision: SecurityDecision
    result: ToolResult
    executed: bool


class ApprovalHandler:
    def approve(self, decision: SecurityDecision, request: ToolRequest) -> bool:
        raise NotImplementedError


class DenyApprovals(ApprovalHandler):
    def approve(self, decision: SecurityDecision, request: ToolRequest) -> bool:
        return False


class AllowApprovals(ApprovalHandler):
    def approve(self, decision: SecurityDecision, request: ToolRequest) -> bool:
        return True


class GuardedExecutor:
    def __init__(
        self,
        tracer: Tracer,
        registry: ToolRegistry,
        environment: SyntheticEnvironment,
        detector: Detector,
        policy: PolicyEngine,
        approval_handler: ApprovalHandler | None = None,
    ) -> None:
        self.tracer = tracer
        self.registry = registry
        self.environment = environment
        self.detector = detector
        self.policy = policy
        self.approval_handler = approval_handler or DenyApprovals()

    def execute(self, request: ToolRequest) -> ExecutionOutcome:
        self.tracer.emit(
            EventType.TOOL_REQUEST,
            tool_name=request.tool_name,
            tool_arguments=request.arguments,
        )
        trajectory = self.tracer.trajectory()
        signals = self.detector.evaluate(trajectory, request)
        decision = self.policy.decide(signals)
        self.tracer.emit(
            EventType.POLICY_DECISION,
            tool_name=request.tool_name,
            tool_arguments=request.arguments,
            risk_signals=signals,
            security_decision=decision,
        )

        allowed = decision.decision == DecisionType.ALLOW
        if decision.decision == DecisionType.REQUIRE_APPROVAL:
            allowed = self.approval_handler.approve(decision, request)

        if not allowed:
            result = ToolResult(
                success=False,
                executed=False,
                error=f"action {decision.decision.value}",
                output=None,
            )
            self.tracer.emit(
                EventType.TOOL_RESULT,
                tool_name=request.tool_name,
                tool_arguments=request.arguments,
                result=result,
                risk_signals=signals,
                security_decision=decision,
            )
            return ExecutionOutcome(
                request=request,
                decision=decision,
                result=result,
                executed=False,
            )

        result = self.registry.invoke(request.tool_name, request.arguments, self.environment)
        self.tracer.emit(
            EventType.TOOL_RESULT,
            tool_name=request.tool_name,
            tool_arguments=request.arguments,
            data_accessed=result.data_accessed,
            result=result,
            risk_signals=signals,
            security_decision=decision,
        )
        return ExecutionOutcome(
            request=request,
            decision=decision,
            result=result,
            executed=True,
        )
