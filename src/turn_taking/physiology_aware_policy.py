"""Heuristic physiology-aware turn-taking policy."""

from __future__ import annotations

from src.features.physiology_features import TurnFeatures
from src.turn_taking.baseline_vad_policy import PolicyDecision


class PhysiologyAwarePolicy:
    def decide(self, features: TurnFeatures) -> PolicyDecision:
        event = features.event
        vad = features.speech.vad
        prosody = features.speech.prosody
        breath = features.breath
        hr = features.heart_rate_bpm or 0
        emg = features.emg_tension or 0.0

        if vad.speech_active:
            return PolicyDecision("LISTEN", 0.03, "speech is active")

        probability = 0.2
        reasons: list[str] = []

        if vad.silence_ms >= 900:
            probability += 0.28
            reasons.append("substantial silence")
        elif vad.silence_ms >= 500:
            probability += 0.12
            reasons.append("brief silence")

        if breath.suggests_completion:
            probability += 0.34
            reasons.append("final exhale")
        elif breath.phase == "inhale":
            probability -= 0.28
            reasons.append("inhale suggests continuation")
        elif breath.phase == "hold":
            probability -= 0.22
            reasons.append("breath hold suggests searching")

        if prosody.cadence == "falling":
            probability += 0.16
            reasons.append("falling cadence")
        elif prosody.cadence == "rising_or_rambling":
            probability -= 0.18
            reasons.append("high WPM")

        if features.speech.repeated_false_starts >= 2:
            probability -= 0.14
            reasons.append("repeated false starts")

        if hr >= 95 or emg >= 0.55:
            probability -= 0.08
            reasons.append("elevated arousal/tension")

        probability = min(0.98, max(0.02, probability))

        if (
            vad.silence_ms >= 1500
            and breath.phase == "hold"
            and (hr >= 92 or emg >= 0.5 or features.speech.repeated_false_starts >= 1)
        ):
            return PolicyDecision(
                "ASK_SHORT_CLARIFYING_QUESTION",
                probability,
                "long searching pause; use a tiny prompt instead of a full answer",
            )

        if probability >= 0.68:
            return PolicyDecision("RESPOND", probability, "; ".join(reasons))

        return PolicyDecision("WAIT", probability, "; ".join(reasons) or "not enough evidence")
