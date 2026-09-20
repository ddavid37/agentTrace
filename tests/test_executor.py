from agenttrace.agent.executor import GuardedExecutor
from agenttrace.agent.loop import AgentLoop
from agenttrace.agent.scripted import ScriptedAgent
from agenttrace.detection.baseline import BaselineRuleDetector
from agenttrace.enforcement.policy import PolicyEngine
from agenttrace.shared.schemas import AgentGoal, AgentIdentity, EventType, ToolRequest
from agenttrace.telemetry.tracer import Tracer
from agenttrace.tools.base import ToolRegistry
from agenttrace.tools.environment import default_workspace
from agenttrace.tools.local import default_tools


def test_executor_emits_telemetry_for_every_tool_request() -> None:
    env = default_workspace()
    tracer = Tracer(identity=AgentIdentity(agent_id="a1"), environment=env.name)
    executor = GuardedExecutor(
        tracer=tracer,
        registry=ToolRegistry(default_tools()),
        environment=env,
        detector=BaselineRuleDetector(),
        policy=PolicyEngine(),
    )
    executor.execute(ToolRequest(tool_name="search_files", arguments={"query": "revenue"}))
    types = [event.event_type for event in tracer.trajectory().events]
    assert EventType.TOOL_REQUEST in types
    assert EventType.POLICY_DECISION in types
    assert EventType.TOOL_RESULT in types


def test_blocked_action_does_not_run_the_tool() -> None:
    env = default_workspace()
    original = env.files["/secrets/api_keys.txt"]
    tracer = Tracer(identity=AgentIdentity(agent_id="a1"), environment=env.name)
    tracer.emit(
        EventType.GOAL_SET,
        goal=AgentGoal(text="Find the quarterly revenue report and summarize it."),
    )
    executor = GuardedExecutor(
        tracer=tracer,
        registry=ToolRegistry(default_tools()),
        environment=env,
        detector=BaselineRuleDetector(),
        policy=PolicyEngine(),
    )
    outcome = executor.execute(
        ToolRequest(tool_name="read_file", arguments={"path": "/secrets/api_keys.txt"})
    )
    assert outcome.executed is False
    assert outcome.result.output is None
    assert env.files["/secrets/api_keys.txt"] == original


def test_agent_cannot_call_tools_except_through_executor() -> None:
    env = default_workspace()
    loop = AgentLoop(
        identity=AgentIdentity(agent_id="a1"),
        environment=env,
        registry=ToolRegistry(default_tools()),
        detector=BaselineRuleDetector(),
        policy=PolicyEngine(),
    )
    agent = ScriptedAgent(
        steps=[
            ToolRequest(tool_name="search_files", arguments={"query": "revenue"}),
            ToolRequest(tool_name="read_file", arguments={"path": "/workspace/reports/q1_revenue.txt"}),
        ],
        summary="done",
    )
    result = loop.run(AgentGoal(text="Find the quarterly revenue report and summarize it."), agent)
    tool_results = [
        event
        for event in result.trajectory.events
        if event.event_type == EventType.TOOL_RESULT
    ]
    assert len(tool_results) == 2
    assert all(event.security_decision is not None for event in tool_results)
