"""Detector interface. Detectors observe trajectories; they do not mutate agent state."""

from __future__ import annotations

from typing import Protocol

from agenttrace.shared.schemas import AgentTrajectory, SecuritySignal, ToolRequest


class Detector(Protocol):
    name: str

    def evaluate(
        self,
        trajectory: AgentTrajectory,
        pending_request: ToolRequest,
    ) -> list[SecuritySignal]:
        ...


class CompositeDetector:
    """Runs multiple detectors and concatenates their signals."""

    name = "composite"

    def __init__(self, detectors: list[Detector]) -> None:
        self.detectors = detectors

    def evaluate(
        self,
        trajectory: AgentTrajectory,
        pending_request: ToolRequest,
    ) -> list[SecuritySignal]:
        signals: list[SecuritySignal] = []
        for detector in self.detectors:
            signals.extend(detector.evaluate(trajectory, pending_request))
        return signals
