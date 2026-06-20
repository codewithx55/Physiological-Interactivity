"""Shared event models for live biometric and transcript capture."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import time
from typing import Literal


EventType = Literal["biometric", "transcript", "audio"]


def now_ms() -> int:
    return time.time_ns() // 1_000_000


@dataclass(frozen=True)
class BiometricEvent:
    session_id: str
    device: str
    timestamp_ms: int
    signal: str
    value: float
    unit: str
    quality: float
    type: EventType = "biometric"

    def to_json(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"))


@dataclass(frozen=True)
class TranscriptEvent:
    session_id: str
    timestamp_ms: int
    speaker: str
    text: str
    is_final: bool
    source: str
    type: EventType = "transcript"

    def to_json(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"))


@dataclass(frozen=True)
class AudioEvent:
    session_id: str
    timestamp_ms: int
    path: str
    sample_rate_hz: int
    source: str
    type: EventType = "audio"

    def to_json(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"))
