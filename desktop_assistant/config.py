from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AssistantConfig:
    wake_words: list[str]
    require_wake_word: bool
    dangerous_action_confirm_seconds: int
    apps: dict[str, list[str]]


def _expand_argv(argv: list[str]) -> list[str]:
    return [os.path.expandvars(os.path.expanduser(x)) for x in argv]


def load_config(path: str | Path) -> AssistantConfig:
    p = Path(path)
    raw: dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
    wake_words = [str(x).strip().lower() for x in raw.get("wake_words", ["assistant"]) if str(x).strip()]
    require_wake_word = bool(raw.get("require_wake_word", True))
    dangerous_action_confirm_seconds = int(raw.get("dangerous_action_confirm_seconds", 12))
    apps_raw = raw.get("apps", {}) or {}
    apps: dict[str, list[str]] = {}
    for k, v in apps_raw.items():
        if isinstance(v, list) and all(isinstance(x, str) for x in v) and v:
            apps[str(k).strip().lower()] = _expand_argv(v)
    return AssistantConfig(
        wake_words=wake_words or ["assistant"],
        require_wake_word=require_wake_word,
        dangerous_action_confirm_seconds=max(3, dangerous_action_confirm_seconds),
        apps=apps,
    )

