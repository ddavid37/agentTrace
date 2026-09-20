"""Local synthetic tools. They only operate on in-memory environment data."""

from __future__ import annotations

from typing import Any

from agenttrace.shared.schemas import ToolResult
from agenttrace.tools.environment import SyntheticEnvironment


class SearchFilesTool:
    name = "search_files"
    description = "Search synthetic file paths and contents for a query string."

    def run(self, arguments: dict[str, Any], environment: SyntheticEnvironment) -> ToolResult:
        query = str(arguments.get("query", "")).lower()
        matches = [
            path
            for path, content in environment.files.items()
            if query in path.lower() or query in content.lower()
        ]
        return ToolResult(success=True, output=matches, data_accessed=matches)


class ReadFileTool:
    name = "read_file"
    description = "Read a synthetic file by path."

    def run(self, arguments: dict[str, Any], environment: SyntheticEnvironment) -> ToolResult:
        path = str(arguments.get("path", ""))
        if path not in environment.files:
            return ToolResult(
                success=False,
                error=f"file not found: {path}",
                data_accessed=[],
            )
        return ToolResult(
            success=True,
            output=environment.files[path],
            data_accessed=[path],
        )


class QueryDatabaseTool:
    name = "query_database"
    description = "Query a synthetic in-memory table by substring match."

    def run(self, arguments: dict[str, Any], environment: SyntheticEnvironment) -> ToolResult:
        table = str(arguments.get("table", ""))
        query = str(arguments.get("query", "")).lower()
        if table not in environment.tables:
            return ToolResult(success=False, error=f"table not found: {table}")
        rows = [
            row
            for row in environment.tables[table]
            if query in str(row).lower()
        ]
        return ToolResult(
            success=True,
            output=rows,
            data_accessed=[f"db:{table}"],
        )


class SendEmailTool:
    name = "send_email"
    description = (
        "Record a synthetic outbound message. This does not contact any network."
    )

    def run(self, arguments: dict[str, Any], environment: SyntheticEnvironment) -> ToolResult:
        message = {
            "to": arguments.get("to"),
            "body": arguments.get("body"),
        }
        environment.outbox.append(message)
        return ToolResult(
            success=True,
            output={"queued": True, "to": message["to"]},
            data_accessed=["outbox"],
        )


def default_tools() -> list[SearchFilesTool | ReadFileTool | QueryDatabaseTool | SendEmailTool]:
    return [SearchFilesTool(), ReadFileTool(), QueryDatabaseTool(), SendEmailTool()]
