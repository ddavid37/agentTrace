"""Evaluation: scenario metadata and session observations. No benchmark claims yet."""

from agenttrace.evaluation.metrics import SessionObservation, observe_session
from agenttrace.evaluation.scenarios import scenario_manifest

__all__ = ["SessionObservation", "observe_session", "scenario_manifest"]
