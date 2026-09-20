from agenttrace.tools.base import ToolError, ToolRegistry
from agenttrace.tools.environment import default_workspace
from agenttrace.tools.local import default_tools


def test_search_and_read_operate_on_synthetic_files() -> None:
    env = default_workspace(injected_report=False)
    registry = ToolRegistry(default_tools())
    matches = registry.invoke("search_files", {"query": "quarterly revenue"}, env)
    assert matches.success
    assert "/workspace/reports/q1_revenue.txt" in matches.output

    result = registry.invoke(
        "read_file",
        {"path": "/workspace/reports/q1_revenue.txt"},
        env,
    )
    assert result.success
    assert "4.2M" in result.output
    assert result.data_accessed == ["/workspace/reports/q1_revenue.txt"]


def test_query_database_is_local_only() -> None:
    env = default_workspace()
    registry = ToolRegistry(default_tools())
    result = registry.invoke("query_database", {"table": "sales", "query": "NA"}, env)
    assert result.success
    assert result.data_accessed == ["db:sales"]
    assert result.output[0]["region"] == "NA"


def test_send_email_records_outbox_without_network() -> None:
    env = default_workspace()
    registry = ToolRegistry(default_tools())
    result = registry.invoke(
        "send_email",
        {"to": "analyst@example.test", "body": "summary"},
        env,
    )
    assert result.success
    assert env.outbox[0]["to"] == "analyst@example.test"


def test_unknown_tool_raises() -> None:
    registry = ToolRegistry(default_tools())
    try:
        registry.get("explode")
        raise AssertionError("expected ToolError")
    except ToolError as exc:
        assert "unknown tool" in str(exc)
