#!/usr/bin/env python3
"""Export the current benchmark summary for the grant packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.turn_taking.evaluator import evaluation_payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Export physiology turn-taking eval summary.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of markdown.")
    parser.add_argument("--output", type=Path, help="Optional output path.")
    args = parser.parse_args()

    payload = evaluation_payload()
    text = json.dumps(payload, indent=2) if args.json else _markdown(payload)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(text)
    return 0


def _markdown(payload: dict[str, object]) -> str:
    metrics = payload["metrics"]
    key_events = payload["key_events"]
    lines = [
        "# Evaluation Snapshot",
        "",
        "Synthetic benchmark comparing baseline silence/VAD endpointing against physiology-aware turn gating.",
        "",
        "## Metrics",
        "",
        "| Policy | False interruptions | End latency ms | Unneeded wait ms | Clarify hits | Score |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for metric in metrics:  # type: ignore[assignment]
        lines.append(
            f"| {metric['policy']} | {metric['false_interruptions']} | "
            f"{metric['true_end_latency_ms']} | {metric['unnecessary_wait_ms']} | "
            f"{metric['clarify_hits']} | {metric['score']} |"
        )

    lines.extend(["", "## Key Events", ""])
    for event in key_events:  # type: ignore[assignment]
        lines.append(
            f"- `{event['scenario_id']}` at {event['at_ms']}ms: truth `{event['truth']}`, "
            f"breath `{event['breath_phase']}`, baseline `{event['baseline_action']}`, "
            f"physiology `{event['physiology_action']}`."
        )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
