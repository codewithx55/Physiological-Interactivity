"""Breath-derived turn-taking features."""

from __future__ import annotations

from dataclasses import dataclass

from src.sensors.simulator import BreathPhase, TimelineEvent


@dataclass(frozen=True)
class BreathFeatures:
    phase: BreathPhase
    rate_bpm: float
    signal: float
    suggests_continuation: bool
    suggests_completion: bool


def extract_breath_features(event: TimelineEvent) -> BreathFeatures:
    suggests_continuation = event.breath_phase in {"inhale", "hold"}
    suggests_completion = event.breath_phase == "exhale" and event.breath_signal <= -0.75
    return BreathFeatures(
        phase=event.breath_phase,
        rate_bpm=event.breath_rate_bpm,
        signal=event.breath_signal,
        suggests_continuation=suggests_continuation,
        suggests_completion=suggests_completion,
    )
