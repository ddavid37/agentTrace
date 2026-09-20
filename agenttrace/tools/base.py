"""Tool interface. Tools never invoke themselves; the executor is the only caller."""

from __future__ import annotations

from typing import Any, Protocol

from agenttrace.shared.schemas import ToolResult
from agenttrace.tools.environment import SyntheticEnvironment


class Tool(Protocol):
    name: str
    description: str

    def run(self, arguments: dict[str, Any], environment: SyntheticEnvironment) -> ToolResult:
        ...


class ToolError(Exception):
    pass


class ToolRegistry:
    def __init__(self, tools: list[Tool]) -> None:
        self._tools = {tool.name: tool for tool in tools}

    def names(self) -> list[str]:
        return sorted(self._tools)

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolError(f"unknown tool: {name}") from exc

    def invoke(self, name: str, arguments: dict[str, Any], environment: SyntheticEnvironment) -> ToolResult:
        return self.get(name).run(arguments, environment)
