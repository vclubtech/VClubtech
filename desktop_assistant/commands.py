from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal


CommandType = Literal[
    "help",
    "open_app",
    "open_url",
    "search_web",
    "volume_up",
    "volume_down",
    "volume_mute",
    "media_play_pause",
    "media_next",
    "media_prev",
    "screenshot",
    "lock",
    "shutdown",
    "reboot",
    "cancel",
    "confirm"
]


@dataclass(frozen=True)
class Command:
    type: CommandType
    arg: str | None = None


_RE_URL = re.compile(r"^(https?://\S+)$", re.IGNORECASE)


def parse_command(text: str) -> Command | None:
    t = (text or "").strip().lower()
    if not t:
        return None

    if t in {"help", "what can you do", "commands"}:
        return Command("help")

    if t in {"cancel", "never mind", "stop"}:
        return Command("cancel")

    if t in {"confirm", "yes confirm", "confirm it", "do it"}:
        return Command("confirm")

    # Open URL directly
    m = _RE_URL.match(t)
    if m:
        return Command("open_url", m.group(1))

    # Open app
    m = re.match(r"^(open|launch|start)\s+(.+)$", t)
    if m:
        return Command("open_app", m.group(2).strip())

    # Search web
    m = re.match(r"^(search|google)\s+(for\s+)?(.+)$", t)
    if m:
        return Command("search_web", m.group(3).strip())

    # Volume
    if t in {"volume up", "turn up volume", "increase volume"}:
        return Command("volume_up")
    if t in {"volume down", "turn down volume", "decrease volume"}:
        return Command("volume_down")
    if t in {"mute", "volume mute", "mute volume"}:
        return Command("volume_mute")

    # Media
    if t in {"play", "pause", "play pause", "toggle", "play/pause"}:
        return Command("media_play_pause")
    if t in {"next", "next track", "skip"}:
        return Command("media_next")
    if t in {"previous", "prev", "previous track", "back"}:
        return Command("media_prev")

    # Desktop actions
    if t in {"screenshot", "take screenshot", "capture screen"}:
        return Command("screenshot")
    if t in {"lock", "lock screen"}:
        return Command("lock")

    # Dangerous
    if t in {"shutdown", "power off"}:
        return Command("shutdown")
    if t in {"reboot", "restart"}:
        return Command("reboot")

    return None

