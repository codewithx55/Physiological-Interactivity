"""Voice activity detection features for synthetic timeline events."""

from __future__ import annotations

from dataclasses import dataclass

from src.sensors.simulator import TimelineEvent


@dataclass(frozen=True)
class VadFeatures:
    speech_active: bool
    silence_ms: int


def extract_vad_features(event: TimelineEvent) -> VadFeatures:
    return VadFeatures(speech_active=event.speech_active, silence_ms=event.silence_ms)
