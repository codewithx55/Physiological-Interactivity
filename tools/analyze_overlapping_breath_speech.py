#!/usr/bin/env python3
"""Analyze a timestamp-aligned breath + speech fixture for turn-taking cues."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.features.physiology_features import extract_turn_features
from src.sensors.simulator import TimelineEvent
from src.turn_taking.baseline_vad_policy import BaselineVadPolicy, PolicyDecision
from src.turn_taking.physiology_aware_policy import PhysiologyAwarePolicy


DEFAULT_INPUT = ROOT / "examples" / "synthetic_overlap_001.json"


def boolish(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def load_events(path: Path) -> list[TimelineEvent]:
    rows = load_rows(path)

    events: list[TimelineEvent] = []
    false_starts = 0
    for row in rows:
        note = row["note"]
        if "false start" in note.lower():
            false_starts += 1
        elif row["ground_truth"] == "done":
            false_starts = 0

        events.append(
            TimelineEvent(
                at_ms=int(row["timestamp_ms"]),
                speech_active=boolish(row["speech_active"]),
                token=row["token"],
                silence_ms=int(row["silence_ms"]),
                words_per_minute=int(row["words_per_minute"]),
                breath_phase=row["breath_phase"],  # type: ignore[arg-type]
                breath_rate_bpm=float(row["breath_rate_bpm"]),
                breath_signal=_force_to_signal(float(row["force_n"]), row["breath_phase"]),
                heart_rate_bpm=None,
                emg_tension=None,
                repeated_false_starts=false_starts,
                ground_truth=row["ground_truth"],  # type: ignore[arg-type]
                note=note,
            )
        )
    return events


def load_rows(path: Path) -> list[dict[str, str]]:
    if path.suffix == ".json":
        raw_rows = json.loads(path.read_text(encoding="utf-8"))
        return [{key: str(value) for key, value in row.items()} for row in raw_rows]
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _force_to_signal(force_n: float, phase: str) -> float:
    """Normalize force enough to reuse the existing heuristic policy."""
    centered = max(-1.0, min(1.0, (force_n - 11.8) / 3.8))
    if phase == "exhale":
        return min(centered, -0.78)
    if phase == "inhale":
        return max(centered, 0.35)
    return centered * 0.25


def is_false_interrupt(decision: PolicyDecision, event: TimelineEvent) -> bool:
    return decision.action == "RESPOND" and event.ground_truth == "continue"


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze overlapping synthetic breath + speech data.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args()

    events = load_events(args.input)
    baseline = BaselineVadPolicy()
    physiology = PhysiologyAwarePolicy()

    rows = []
    for event in events:
        features = extract_turn_features(event)
        rows.append((event, baseline.decide(features), physiology.decide(features)))

    silent_rows = [(event, base, phys) for event, base, phys in rows if not event.speech_active]
    baseline_false = sum(is_false_interrupt(base, event) for event, base, _ in silent_rows)
    physiology_false = sum(is_false_interrupt(phys, event) for event, _, phys in silent_rows)
    clarify_hits = sum(
        event.ground_truth == "clarify" and phys.action == "ASK_SHORT_CLARIFYING_QUESTION"
        for event, _, phys in silent_rows
    )

    print("Overlapping breath + speech turn-taking analysis")
    print(f"input: {args.input}")
    print(f"events: {len(events)}")
    print(f"silent decision points: {len(silent_rows)}")
    print()
    print("summary")
    print(f"baseline_false_interruptions: {baseline_false}")
    print(f"physiology_false_interruptions: {physiology_false}")
    print(f"physiology_clarify_hits: {clarify_hits}")
    print()
    print("silent decision points")
    print("time_ms,truth,breath,silence_ms,wpm,baseline,physiology,physiology_reason")
    for event, base, phys in silent_rows:
        print(
            f"{event.at_ms},{event.ground_truth},{event.breath_phase},{event.silence_ms},"
            f"{event.words_per_minute},{base.action},{phys.action},{phys.reason}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
