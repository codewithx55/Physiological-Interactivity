#!/usr/bin/env python3
"""Train a tiny inhale/exhale classifier from keyboard calibration labels."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def latest_window(labels: list[dict[str, Any]]) -> tuple[int, int | None]:
    starts = [int(row["timestamp_ms"]) for row in labels if row.get("label") == "calibration_start"]
    if not starts:
        raise RuntimeError("No calibration_start label found. Run calibration first.")
    start = max(starts)
    ends = [
        int(row["timestamp_ms"])
        for row in labels
        if row.get("label") == "calibration_end" and int(row["timestamp_ms"]) >= start
    ]
    return start, min(ends) if ends else None


def dedupe_labels(labels: list[dict[str, Any]], min_gap_ms: int) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    last_by_label: dict[str, int] = {}
    for row in labels:
        label = str(row.get("label"))
        timestamp_ms = int(row["timestamp_ms"])
        if timestamp_ms - last_by_label.get(label, 0) >= min_gap_ms:
            deduped.append(row)
            last_by_label[label] = timestamp_ms
    return deduped


def slope_near(samples: list[tuple[int, float]], timestamp_ms: int, window_ms: int) -> float | None:
    before = [value for ts, value in samples if timestamp_ms - window_ms <= ts <= timestamp_ms]
    after = [value for ts, value in samples if timestamp_ms <= ts <= timestamp_ms + window_ms]
    if not before or not after:
        return None
    return after[-1] - before[0]


def score_window(samples: list[tuple[int, float]], labels: list[dict[str, Any]], window_ms: int) -> dict[str, Any]:
    rows = []
    for label in labels:
        slope = slope_near(samples, int(label["timestamp_ms"]), window_ms)
        if slope is None:
            continue
        rows.append((str(label["label"]), slope))
    if not rows:
        return {"window_ms": window_ms, "accuracy": 0.0, "margin": 0.0, "rows": []}
    inhale = [slope for label, slope in rows if label == "inhale"]
    exhale = [slope for label, slope in rows if label == "exhale"]
    normal_correct = sum(1 for label, slope in rows if (slope >= 0 and label == "inhale") or (slope < 0 and label == "exhale"))
    inverted_correct = len(rows) - normal_correct
    polarity = 1 if normal_correct >= inverted_correct else -1
    accuracy = max(normal_correct, inverted_correct) / len(rows)
    margin = abs((statistics.mean(inhale) if inhale else 0.0) - (statistics.mean(exhale) if exhale else 0.0))
    return {
        "window_ms": window_ms,
        "accuracy": accuracy,
        "margin": margin,
        "polarity": polarity,
        "rows": rows,
        "inhale_mean_slope": statistics.mean(inhale) if inhale else 0.0,
        "exhale_mean_slope": statistics.mean(exhale) if exhale else 0.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Train breath phase model.")
    parser.add_argument("--session-id", default="daley_kenny_calibri_001")
    parser.add_argument("--skip-ms", type=int, default=5000)
    parser.add_argument("--dedupe-ms", type=int, default=350)
    args = parser.parse_args()

    events_path = ROOT / "data" / f"{args.session_id}.events.jsonl"
    labels_path = ROOT / "data" / f"{args.session_id}.breath_labels.jsonl"
    model_path = ROOT / "build" / "breath-model.json"

    events = load_jsonl(events_path)
    labels = load_jsonl(labels_path)
    start, end = latest_window(labels)
    training_labels = [
        row
        for row in labels
        if row.get("label") in {"inhale", "exhale"}
        and int(row["timestamp_ms"]) >= start + args.skip_ms
        and (end is None or int(row["timestamp_ms"]) <= end)
    ]
    training_labels = dedupe_labels(training_labels, args.dedupe_ms)
    samples = [
        (int(row["timestamp_ms"]), float(row["value"]))
        for row in events
        if row.get("type") == "biometric"
        and row.get("signal") == "respiration_force"
        and int(row["timestamp_ms"]) >= start - 2000
        and (end is None or int(row["timestamp_ms"]) <= end + 2000)
    ]

    candidates = [score_window(samples, training_labels, window_ms) for window_ms in (300, 500, 700, 900, 1200)]
    best = max(candidates, key=lambda row: (row["accuracy"], row["margin"]))
    confidence = "low"
    if best["accuracy"] >= 0.72 and best["margin"] >= 0.25:
        confidence = "high"
    elif best["accuracy"] >= 0.62 or best["margin"] >= 0.18:
        confidence = "medium"

    model = {
        "session_id": args.session_id,
        "trained_at_ms": max(int(row["timestamp_ms"]) for row in labels) if labels else None,
        "calibration_start_ms": start,
        "calibration_end_ms": end,
        "skip_ms": args.skip_ms,
        "dedupe_ms": args.dedupe_ms,
        "signal": "respiration_force",
        "method": "slope_sign",
        "window_ms": best["window_ms"],
        "polarity": best["polarity"],
        "accuracy": round(best["accuracy"], 4),
        "margin": round(best["margin"], 4),
        "confidence": confidence,
        "training_labels": len(training_labels),
        "inhale_labels": sum(1 for row in training_labels if row.get("label") == "inhale"),
        "exhale_labels": sum(1 for row in training_labels if row.get("label") == "exhale"),
        "inhale_mean_slope": round(best["inhale_mean_slope"], 4),
        "exhale_mean_slope": round(best["exhale_mean_slope"], 4),
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(model, indent=2))
    if confidence == "low":
        print("warning: calibration is weak; use this live view as a UI/data-path test, not a validated physiology classifier")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
