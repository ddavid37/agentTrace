"""CLI demo for the first AgentTrace vertical slice."""

from __future__ import annotations

import json
from collections.abc import Iterable

from agenttrace.agent.loop import SessionResult
from agenttrace.attacks.prompt_injection import (
    PROMPT_INJECTION_SCENARIO,
    run_benign_revenue_scenario,
    run_prompt_injection_scenario,
)
from agenttrace.evaluation.metrics import observe_session
from agenttrace.evaluation.scenarios import scenario_manifest
from agenttrace.shared.schemas import AgentEvent, DecisionType


def _print_header(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def _summarize_event(event: AgentEvent) -> dict[str, object]:
    payload: dict[str, object] = {
        "step": event.step_number,
        "type": event.event_type.value,
        "event_id": event.event_id,
        "previous_event_id": event.previous_event_id,
    }
    if event.tool_name:
        payload["tool"] = event.tool_name
        payload["arguments"] = event.tool_arguments
    if event.result is not None:
        payload["executed"] = event.result.executed
        payload["success"] = event.result.success
        if event.result.error:
            payload["error"] = event.result.error
    if event.security_decision is not None:
        payload["decision"] = event.security_decision.decision.value
        payload["risk_score"] = event.security_decision.risk_score
        payload["reasons"] = event.security_decision.reasons
    if event.model_output:
        payload["message"] = event.model_output
    return payload


def _print_session(title: str, result: SessionResult) -> None:
    _print_header(title)
    observation = observe_session(result)
    print(json.dumps({
        "trace_id": result.trajectory.trace_id,
        "session_id": result.trajectory.session_id,
        "goal": result.trajectory.goal.text if result.trajectory.goal else None,
        "final_message": result.final_message,
        "observation": {
            "steps": observation.steps,
            "blocked": observation.blocked,
            "required_approval": observation.required_approval,
            "secret_file_executed": observation.secret_file_executed,
            "first_non_allow_step": observation.first_non_allow_step,
        },
        "events": [_summarize_event(event) for event in result.trajectory.ordered_events()],
    }, indent=2))


def main(argv: Iterable[str] | None = None) -> int:
    del argv
    _print_header("AgentTrace local demo")
    print("Research question:")
    print('  Can we detect when an AI agent is moving toward an unsafe outcome')
    print("  by analyzing its trajectory before the final tool call?")
    print()
    print("This demo uses a deterministic mock agent and synthetic local data.")
    print("It does not call an LLM and does not contact external systems.")
    print()
    print("Scenario definition:")
    print(json.dumps(scenario_manifest(PROMPT_INJECTION_SCENARIO), indent=2))

    benign = run_benign_revenue_scenario()
    _print_session("Benign trajectory (no injected instructions)", benign)

    attack = run_prompt_injection_scenario()
    _print_session("Synthetic prompt-injection trajectory", attack)

    decisions = [outcome.decision.decision for outcome in attack.outcomes]
    if DecisionType.BLOCK in decisions or DecisionType.REQUIRE_APPROVAL in decisions:
        print()
        print("Enforcement stopped the redirected secret-access attempt.")
    else:
        print()
        print("Warning: the redirected secret-access attempt was not stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
