"""Baseline policy: respond after enough audio silence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from src.features.physiology_features import TurnFeatures


AgentAction = Literal["LISTEN", "WAIT", "RESPOND", "ASK_SHORT_CLARIFYING_QUESTION"]


@dataclass(frozen=True)
class PolicyDecision:
    action: AgentAction
    end_of_turn_probability: float
    reason: str


class BaselineVadPolicy:
    def __init__(self, silence_threshold_ms: int = 650) -> None:
        self.silence_threshold_ms = silence_threshold_ms

    def decide(self, features: TurnFeatures) -> PolicyDecision:
        vad = features.speech.vad
        if vad.speech_active:
            return PolicyDecision("LISTEN", 0.05, "speech is active")
        if vad.silence_ms > self.silence_threshold_ms:
            return PolicyDecision(
                "RESPOND",
                min(0.95, vad.silence_ms / 1600),
                f"silence {vad.silence_ms}ms > {self.silence_threshold_ms}ms",
            )
        return PolicyDecision(
            "WAIT",
            max(0.1, vad.silence_ms / self.silence_threshold_ms * 0.45),
            f"silence {vad.silence_ms}ms <= {self.silence_threshold_ms}ms",
        )
