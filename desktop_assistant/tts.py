from __future__ import annotations

import threading

import pyttsx3


class Speaker:
    def __init__(self, rate: int = 175, volume: float = 1.0):
        self._engine = pyttsx3.init()
        self._engine.setProperty("rate", rate)
        self._engine.setProperty("volume", volume)
        self._lock = threading.Lock()

    def say(self, text: str) -> None:
        text = (text or "").strip()
        if not text:
            return
        with self._lock:
            self._engine.say(text)
            self._engine.runAndWait()

