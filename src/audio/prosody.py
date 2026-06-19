"""Prosody features for turn-readiness heuristics."""

from __future__ import annotations

from dataclasses import dataclass

from src.sensors.simulator import TimelineEvent


@dataclass(frozen=True)
class ProsodyFeatures:
    words_per_minute: int
    cadence: str


def extract_prosody_features(event: TimelineEvent) -> ProsodyFeatures:
    if event.words_per_minute >= 165:
        cadence = "rising_or_rambling"
    elif event.words_per_minute <= 95:
        cadence = "falling"
    else:
        cadence = "steady"
    return ProsodyFeatures(words_per_minute=event.words_per_minute, cadence=cadence)
