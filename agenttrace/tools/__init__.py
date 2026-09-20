"""Local synthetic tools and environment."""

from agenttrace.tools.base import Tool, ToolError, ToolRegistry
from agenttrace.tools.environment import SyntheticEnvironment, default_workspace
from agenttrace.tools.local import (
    QueryDatabaseTool,
    ReadFileTool,
    SearchFilesTool,
    SendEmailTool,
    default_tools,
)

__all__ = [
    "QueryDatabaseTool",
    "ReadFileTool",
    "SearchFilesTool",
    "SendEmailTool",
    "SyntheticEnvironment",
    "Tool",
    "ToolError",
    "ToolRegistry",
    "default_tools",
    "default_workspace",
]
