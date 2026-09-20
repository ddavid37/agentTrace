"""Explicit configuration. Secrets stay in environment variables, never in code."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


@dataclass(frozen=True)
class Settings:
    model_provider: str
    model_name: str
    api_key: str
    approval_mode: str

    @classmethod
    def from_env(cls) -> Settings:
        mode = _env("AGENTTRACE_APPROVAL_MODE", "deny").strip().lower()
        if mode not in {"deny", "allow"}:
            mode = "deny"
        return cls(
            model_provider=_env("AGENTTRACE_MODEL_PROVIDER"),
            model_name=_env("AGENTTRACE_MODEL_NAME"),
            api_key=_env("AGENTTRACE_API_KEY"),
            approval_mode=mode,
        )
