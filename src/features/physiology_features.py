"""Combined physiology and speech features for policy decisions."""

from __future__ import annotations

from dataclasses import dataclass

from src.features.breath_features import BreathFeatures, extract_breath_features
from src.features.speech_features import SpeechFeatures, extract_speech_features
from src.sensors.simulator import TimelineEvent


@dataclass(frozen=True)
class TurnFeatures:
    event: TimelineEvent
    speech: SpeechFeatures
    breath: BreathFeatures
    heart_rate_bpm: int | None
    emg_tension: float | None


def extract_turn_features(event: TimelineEvent) -> TurnFeatures:
    return TurnFeatures(
        event=event,
        speech=extract_speech_features(event),
        breath=extract_breath_features(event),
        heart_rate_bpm=event.heart_rate_bpm,
        emg_tension=event.emg_tension,
    )
