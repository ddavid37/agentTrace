from datetime import UTC, datetime

from agenttrace.shared.schemas import AgentEvent, EventType
from agenttrace.shared.schemas import AgentIdentity
from agenttrace.telemetry.tracer import Tracer


def test_tracer_links_events_into_a_reconstructable_trajectory() -> None:
    clock_times = [
        datetime(2026, 1, 1, tzinfo=UTC),
        datetime(2026, 1, 1, 0, 0, 1, tzinfo=UTC),
        datetime(2026, 1, 1, 0, 0, 2, tzinfo=UTC),
        datetime(2026, 1, 1, 0, 0, 3, tzinfo=UTC),
    ]
    index = {"n": 0}

    def clock() -> datetime:
        value = clock_times[index["n"]]
        index["n"] += 1
        return value

    tracer = Tracer(
        identity=AgentIdentity(agent_id="a1"),
        environment="synthetic-local",
        clock=clock,
        trace_id="trace-fixed",
        session_id="session-fixed",
    )
    first = tracer.emit(EventType.GOAL_SET)
    second = tracer.emit(EventType.TOOL_REQUEST, tool_name="search_files")
    third = tracer.emit(EventType.TOOL_RESULT, tool_name="search_files")
    fourth = tracer.emit(EventType.SESSION_END)

    trajectory = tracer.trajectory()
    ordered = trajectory.ordered_events()
    assert [event.event_id for event in ordered] == [
        first.event_id,
        second.event_id,
        third.event_id,
        fourth.event_id,
    ]
    assert second.previous_event_id == first.event_id
    assert third.previous_event_id == second.event_id
    assert fourth.previous_event_id == third.event_id
    assert trajectory.trace_id == "trace-fixed"


def test_trajectory_reconstruction_from_unordered_events() -> None:
    events = [
        AgentEvent(
            event_id="c",
            trace_id="t",
            session_id="s",
            timestamp=datetime.now(UTC),
            agent_id="a",
            step_number=3,
            event_type=EventType.SESSION_END,
            previous_event_id="b",
        ),
        AgentEvent(
            event_id="a",
            trace_id="t",
            session_id="s",
            timestamp=datetime.now(UTC),
            agent_id="a1",
            step_number=1,
            event_type=EventType.GOAL_SET,
            previous_event_id=None,
        ),
        AgentEvent(
            event_id="b",
            trace_id="t",
            session_id="s",
            timestamp=datetime.now(UTC),
            agent_id="a1",
            step_number=2,
            event_type=EventType.TOOL_REQUEST,
            previous_event_id="a",
        ),
    ]
    from agenttrace.shared.schemas import AgentTrajectory

    ordered = AgentTrajectory.from_events(events).ordered_events()
    assert [event.event_id for event in ordered] == ["a", "b", "c"]
