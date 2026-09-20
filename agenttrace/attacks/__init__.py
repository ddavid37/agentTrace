"""Controlled local attack simulations for evaluation."""

from agenttrace.attacks.prompt_injection import (
    PROMPT_INJECTION_SCENARIO,
    AttackScenario,
    run_benign_revenue_scenario,
    run_prompt_injection_scenario,
)

__all__ = [
    "AttackScenario",
    "PROMPT_INJECTION_SCENARIO",
    "run_benign_revenue_scenario",
    "run_prompt_injection_scenario",
]
