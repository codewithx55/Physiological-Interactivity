"""Speech-derived turn-taking features."""

from __future__ import annotations

from dataclasses import dataclass

from src.audio.prosody import ProsodyFeatures, extract_prosody_features
from src.audio.vad import VadFeatures, extract_vad_features
from src.sensors.simulator import TimelineEvent


@dataclass(frozen=True)
class SpeechFeatures:
    vad: VadFeatures
    prosody: ProsodyFeatures
    repeated_false_starts: int


def extract_speech_features(event: TimelineEvent) -> SpeechFeatures:
    return SpeechFeatures(
        vad=extract_vad_features(event),
        prosody=extract_prosody_features(event),
        repeated_false_starts=event.repeated_false_starts,
    )
