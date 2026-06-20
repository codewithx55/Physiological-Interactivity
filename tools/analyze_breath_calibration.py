#!/usr/bin/env python3
"""Analyze I/E calibration labels against timestamped respiration samples."""

from __future__ import annotations

import argparse
import json
import statistics
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Sample:
    timestamp_ms: int
    value: float


@dataclass(frozen=True)
class Label:
    timestamp_ms: int
    label: str
    display_phase: str | None
    signal_value: float | None


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def latest_window(labels: list[Label]) -> tuple[int | None, int | None]:
    starts = [label.timestamp_ms for label in labels if label.label == "calibration_start"]
    if not starts:
        return None, None
    start = max(starts)
    ends = [label.timestamp_ms for label in labels if label.label == "calibration_end" and label.timestamp_ms >= start]
    return start, min(ends) if ends else None


def slope_near(samples: list[Sample], timestamp_ms: int, window_ms: int) -> float | None:
    before = [s for s in samples if timestamp_ms - window_ms <= s.timestamp_ms <= timestamp_ms]
    after = [s for s in samples if timestamp_ms <= s.timestamp_ms <= timestamp_ms + window_ms]
    if not before or not after:
        return None
    return after[-1].value - before[0].value


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze breath calibration labels.")
    parser.add_argument("--session-id", default="daley_kenny_calibri_001")
    parser.add_argument("--window-ms", type=int, default=900)
    args = parser.parse_args()

    events_path = ROOT / "data" / f"{args.session_id}.events.jsonl"
    labels_path = ROOT / "data" / f"{args.session_id}.breath_labels.jsonl"

    event_rows = load_jsonl(events_path)
    label_rows = load_jsonl(labels_path)
    samples = [
        Sample(int(row["timestamp_ms"]), float(row["value"]))
        for row in event_rows
        if row.get("type") == "biometric" and row.get("signal") == "respiration_force"
    ]
    labels = [
        Label(
            timestamp_ms=int(row["timestamp_ms"]),
            label=str(row["label"]),
            display_phase=row.get("display_phase"),
            signal_value=float(row["signal_value"]) if row.get("signal_value") is not None else None,
        )
        for row in label_rows
        if row.get("type") == "breath_label"
    ]

    start, end = latest_window(labels)
    if start is not None:
        labels = [label for label in labels if label.timestamp_ms >= start and (end is None or label.timestamp_ms <= end)]
        samples = [sample for sample in samples if sample.timestamp_ms >= start - 1500 and (end is None or sample.timestamp_ms <= end + 1500)]

    training = [label for label in labels if label.label in {"inhale", "exhale"}]
    inhale_slopes = [s for label in training if label.label == "inhale" if (s := slope_near(samples, label.timestamp_ms, args.window_ms)) is not None]
    exhale_slopes = [s for label in training if label.label == "exhale" if (s := slope_near(samples, label.timestamp_ms, args.window_ms)) is not None]

    print("Breath calibration analysis")
    print(f"session_id: {args.session_id}")
    print(f"events: {events_path}")
    print(f"labels: {labels_path}")
    print(f"window: {start or 'all'} -> {end or 'open'}")
    print(f"samples: {len(samples)}")
    print(f"training_labels: {len(training)}")
    print(f"inhale_labels: {sum(1 for label in training if label.label == 'inhale')}")
    print(f"exhale_labels: {sum(1 for label in training if label.label == 'exhale')}")

    if not inhale_slopes or not exhale_slopes:
        print("decision: need more labels; press I/E during a 30-second calibration run")
        return 1

    inhale_mean = statistics.mean(inhale_slopes)
    exhale_mean = statistics.mean(exhale_slopes)
    print(f"inhale_mean_slope: {inhale_mean:.4f}")
    print(f"exhale_mean_slope: {exhale_mean:.4f}")

    if inhale_mean > 0 and exhale_mean < 0:
        print("decision: phase direction looks correct")
    elif inhale_mean < 0 and exhale_mean > 0:
        print("decision: phase direction looks inverted; press F on the screen")
    else:
        print("decision: signal/labels are ambiguous; collect another run or switch to Vernier")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
