from __future__ import annotations

import json
import queue
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import sounddevice as sd
from vosk import KaldiRecognizer, Model


@dataclass(frozen=True)
class RecognizedUtterance:
    text: str
    is_final: bool


class VoskListener:
    """
    Offline speech recognition using Vosk + sounddevice.

    Notes:
    - You must download a Vosk model and point `model_path` to it.
    - If your mic device is wrong, pass `device` (int or name).
    """

    def __init__(
        self,
        model_path: str | Path,
        sample_rate: int = 16000,
        device: int | str | None = None,
        blocksize: int = 8000,
    ) -> None:
        self.sample_rate = sample_rate
        self.device = device
        self.blocksize = blocksize
        self._q: queue.Queue[bytes] = queue.Queue()

        mp = Path(model_path)
        self._model = Model(str(mp))
        self._rec = KaldiRecognizer(self._model, self.sample_rate)
        self._rec.SetWords(False)

    def _callback(self, indata: np.ndarray, frames: int, time, status) -> None:  # noqa: ANN001
        if status:
            # Ignore overflow/underflow; the loop will continue.
            pass
        # Convert float32 [-1,1] to 16-bit PCM little-endian
        pcm16 = (indata[:, 0] * 32767).astype(np.int16).tobytes()
        self._q.put(pcm16)

    def listen(self):
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            callback=self._callback,
            device=self.device,
            blocksize=self.blocksize,
        ):
            while True:
                data = self._q.get()
                if self._rec.AcceptWaveform(data):
                    payload = json.loads(self._rec.Result() or "{}")
                    text = (payload.get("text") or "").strip()
                    if text:
                        yield RecognizedUtterance(text=text, is_final=True)
                else:
                    payload = json.loads(self._rec.PartialResult() or "{}")
                    text = (payload.get("partial") or "").strip()
                    if text:
                        yield RecognizedUtterance(text=text, is_final=False)

