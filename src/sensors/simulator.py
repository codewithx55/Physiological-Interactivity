"""Synthetic physiology and voice timelines for the turn-taking demo."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal


BreathPhase = Literal["inhale", "exhale", "hold"]
GroundTruthAction = Literal["continue", "done", "clarify"]


@dataclass(frozen=True)
class TimelineEvent:
    at_ms: int
    speech_active: bool
    token: str
    silence_ms: int
    words_per_minute: int
    breath_phase: BreathPhase
    breath_rate_bpm: float
    breath_signal: float
    heart_rate_bpm: int | None
    emg_tension: float | None
    repeated_false_starts: int
    ground_truth: GroundTruthAction
    note: str


@dataclass(frozen=True)
class Scenario:
    id: str
    title: str
    description: str
    events: list[TimelineEvent]


def _event(
    at_ms: int,
    speech_active: bool,
    token: str,
    silence_ms: int,
    words_per_minute: int,
    breath_phase: BreathPhase,
    breath_rate_bpm: float,
    breath_signal: float,
    ground_truth: GroundTruthAction,
    note: str,
    heart_rate_bpm: int | None = None,
    emg_tension: float | None = None,
    repeated_false_starts: int = 0,
) -> TimelineEvent:
    return TimelineEvent(
        at_ms=at_ms,
        speech_active=speech_active,
        token=token,
        silence_ms=silence_ms,
        words_per_minute=words_per_minute,
        breath_phase=breath_phase,
        breath_rate_bpm=breath_rate_bpm,
        breath_signal=breath_signal,
        heart_rate_bpm=heart_rate_bpm,
        emg_tension=emg_tension,
        repeated_false_starts=repeated_false_starts,
        ground_truth=ground_truth,
        note=note,
    )


def short_thinking_pause() -> Scenario:
    return Scenario(
        id="short_thinking_pause",
        title="Short thinking pause",
        description="User pauses mid-thought, inhales, and continues. VAD fires early; physiology-aware policy waits.",
        events=[
            _event(0, True, "I", 0, 132, "exhale", 13.0, -0.3, "continue", "speech begins", 74, 0.15),
            _event(520, True, "think", 0, 128, "exhale", 13.1, -0.5, "continue", "cadence steady", 75, 0.16),
            _event(1040, True, "we should", 0, 121, "exhale", 13.2, -0.7, "continue", "phrase not complete", 75, 0.18),
            _event(1760, False, "", 720, 121, "inhale", 13.3, 0.45, "continue", "short inhale before continuing", 76, 0.19),
            _event(2360, True, "compare", 0, 118, "exhale", 13.0, -0.2, "continue", "user resumes", 75, 0.17),
            _event(3000, True, "the closed interaction model", 0, 112, "exhale", 12.9, -0.6, "continue", "still speaking", 75, 0.16),
            _event(3880, False, "", 940, 108, "exhale", 12.7, -0.9, "done", "final exhale and completed phrase", 74, 0.12),
        ],
    )


def true_end_of_turn() -> Scenario:
    return Scenario(
        id="true_end_of_turn",
        title="True end of turn",
        description="User completes a phrase, exhales, and falls silent. Both policies should respond, with low latency.",
        events=[
            _event(0, True, "Please", 0, 104, "exhale", 11.4, -0.2, "continue", "request starts", 70, 0.12),
            _event(600, True, "summarize the eval", 0, 98, "exhale", 11.2, -0.5, "continue", "cadence falling", 70, 0.11),
            _event(1280, True, "for the grant draft", 0, 90, "exhale", 11.0, -0.8, "continue", "final clause", 69, 0.1),
            _event(2180, False, "", 900, 82, "exhale", 10.8, -1.0, "done", "clean final exhale", 68, 0.09),
            _event(2880, False, "", 1600, 82, "hold", 10.6, -0.2, "done", "user has yielded floor", 68, 0.08),
        ],
    )


def cognitive_overload_searching() -> Scenario:
    return Scenario(
        id="cognitive_overload_searching",
        title="Cognitive overload / searching",
        description="User gets stuck, holds breath, and shows elevated HR. Policy should ask a short clarifying question.",
        events=[
            _event(0, True, "The thing I need is", 0, 96, "exhale", 15.0, -0.5, "continue", "uncertain phrase", 88, 0.34),
            _event(820, True, "uh", 0, 74, "inhale", 15.6, 0.4, "continue", "false start", 90, 0.42, 1),
            _event(1700, False, "", 880, 62, "hold", 16.8, 0.05, "continue", "searching pause", 94, 0.55, 1),
            _event(2850, False, "", 2030, 62, "hold", 17.6, 0.02, "clarify", "long breath hold; help with a tiny prompt", 98, 0.61, 2),
            _event(4100, True, "maybe the privacy receipt", 0, 70, "exhale", 16.2, -0.4, "continue", "user recovers", 94, 0.38, 2),
        ],
    )


def fast_rambling() -> Scenario:
    return Scenario(
        id="fast_rambling",
        title="Fast rambling",
        description="High WPM and shallow breathing indicate the assistant should wait for a better endpoint.",
        events=[
            _event(0, True, "Also compare Tinker to the closed model", 0, 184, "exhale", 19.5, -0.2, "continue", "fast start", 82, 0.24),
            _event(700, True, "but make sure it does not post to Slack", 0, 194, "inhale", 20.2, 0.35, "continue", "rapid steering", 84, 0.27),
            _event(1450, False, "", 520, 192, "inhale", 21.0, 0.55, "continue", "shallow inhale", 86, 0.29),
            _event(2140, True, "and include the consent boundary", 0, 176, "exhale", 19.8, -0.3, "continue", "continues quickly", 85, 0.25),
            _event(3100, False, "", 960, 168, "inhale", 19.2, 0.5, "continue", "still likely mid-stream", 84, 0.23),
            _event(4200, True, "then stop", 0, 122, "exhale", 16.0, -0.7, "continue", "cadence drops", 80, 0.17),
            _event(5100, False, "", 900, 96, "exhale", 14.0, -1.0, "done", "final endpoint", 76, 0.13),
        ],
    )


def load_scenarios() -> list[Scenario]:
    return [
        short_thinking_pause(),
        true_end_of_turn(),
        cognitive_overload_searching(),
        fast_rambling(),
    ]


def iter_events(scenarios: Iterable[Scenario]) -> Iterable[tuple[Scenario, TimelineEvent]]:
    for scenario in scenarios:
        for event in scenario.events:
            yield scenario, event
