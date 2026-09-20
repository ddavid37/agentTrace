"""Evaluation helpers. Metrics are not claimed until experiments are run."""

from agenttrace.attacks.prompt_injection import AttackScenario


def scenario_manifest(scenario: AttackScenario) -> dict[str, str]:
    return {
        "name": scenario.name,
        "threat_category": scenario.threat_category,
        "initial_goal": scenario.initial_goal,
        "environment": scenario.environment_name,
        "available_tools": ", ".join(scenario.available_tools),
        "attack_condition": scenario.attack_condition,
        "expected_unsafe_behavior": scenario.expected_unsafe_behavior,
        "expected_security_boundary": scenario.expected_security_boundary,
        "expected_detection_point": scenario.expected_detection_point,
    }
