"""Vernier-shaped mock stream for filming without hardware."""

from __future__ import annotations

from dataclasses import asdict

from src.features.physiology_features import extract_turn_features
from src.sensors.simulator import TimelineEvent, short_thinking_pause
from src.turn_taking.baseline_vad_policy import BaselineVadPolicy
from src.turn_taking.physiology_aware_policy import PhysiologyAwarePolicy


def mock_vernier_frames() -> list[dict[str, object]]:
    """Return frames shaped like normalized Vernier respiration samples.

    Expected live adapter target:
    - timestamp_ms: monotonic sample time
    - raw: raw sensor reading from Go Direct
    - breath_signal: normalized waveform value in roughly [-1, 1]
    - breath_phase: inhale/exhale/hold phase derived from recent samples
    - breath_rate_bpm: derived respiration rate
    """
    scenario = short_thinking_pause()
    baseline = BaselineVadPolicy()
    physiology = PhysiologyAwarePolicy()
    frames: list[dict[str, object]] = []

    for event in scenario.events:
        features = extract_turn_features(event)
        baseline_decision = baseline.decide(features)
        physiology_decision = physiology.decide(features)
        frames.append(
            {
                "sample": _sample_from_event(event),
                "event": asdict(event),
                "baseline": asdict(baseline_decision),
                "physiology": asdict(physiology_decision),
                "agent_line": _agent_line(event, baseline_decision.action, physiology_decision.action),
            }
        )
    return frames


def _sample_from_event(event: TimelineEvent) -> dict[str, object]:
    raw = round(1.8 + event.breath_signal * 0.42, 3)
    return {
        "source": "mock_vernier_respiration_belt",
        "timestamp_ms": event.at_ms,
        "channel": "respiration",
        "raw": raw,
        "units": "a.u.",
        "breath_signal": event.breath_signal,
        "breath_phase": event.breath_phase,
        "breath_rate_bpm": event.breath_rate_bpm,
    }


def _agent_line(event: TimelineEvent, baseline_action: str, physiology_action: str) -> str:
    if baseline_action == "RESPOND" and physiology_action == "WAIT" and event.breath_phase == "inhale":
        return "Baseline jumps in. Physiology waits through the inhale."
    if physiology_action == "RESPOND":
        return "Exhale endpoint. Agent responds."
    if event.speech_active:
        return "User has the floor."
    return "Holding the turn."
