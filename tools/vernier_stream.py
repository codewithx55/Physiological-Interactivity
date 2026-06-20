#!/usr/bin/env python3
"""Discover and stream Vernier Go Direct Respiration Belt samples.

This writes only small derived JSON state for the local demo. Do not commit real
sensor exports.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections import deque
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE = ROOT / "build" / "vernier-live.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Stream Vernier breath state to JSON.")
    parser.add_argument("--transport", choices=["ble", "usb"], default="ble")
    parser.add_argument("--device", default="proximity_pairing", help="Device name or proximity_pairing.")
    parser.add_argument("--period-ms", type=int, default=100)
    parser.add_argument("--seconds", type=float, default=0, help="0 means run until Ctrl-C.")
    parser.add_argument("--out", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--list", action="store_true", help="List devices/sensors, then exit.")
    args = parser.parse_args()

    try:
        from godirect.gdx import gdx  # type: ignore
    except ImportError:
        print("godirect is not installed. Run: bash tools/setup_vernier_env.sh", file=sys.stderr)
        return 2

    stream = gdx()
    try:
        if args.transport == "usb":
            stream.open_usb()
        else:
            stream.open_ble(args.device)

        if not stream.devices:
            print("No Go Direct device opened. If Graphical Analysis is connected, disconnect it first.")
            return 1

        device_info = stream.device_info()
        sensor_rows = stream.sensor_info() or []
        print(f"Device: {device_info}")
        print("Sensors:")
        for row in sensor_rows:
            print(f"  {row}")

        force_sensor = _select_force_sensor(sensor_rows)
        sensors = [force_sensor]
        print(f"Using force sensor number: {force_sensor}")

        if args.list:
            return 0

        args.out.parent.mkdir(parents=True, exist_ok=True)
        stream.select_sensors(sensors)
        stream.start(period=args.period_ms)
        _stream_force_samples(stream, args.out, args.seconds)
        return 0
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0
    finally:
        try:
            stream.stop()
        except Exception:
            pass
        try:
            stream.close()
        except Exception:
            pass


def _select_force_sensor(sensor_rows: list[list[Any]]) -> int:
    force: int | None = None
    for row in sensor_rows:
        if len(row) < 3:
            continue
        number = int(row[0])
        label = f"{row[1]} {row[2]}".lower()
        if force is None and ("force" in label or "(n" in label):
            force = number
    if force is None and sensor_rows:
        force = int(sensor_rows[0][0])
    if force is None:
        raise RuntimeError("No readable sensor channels found.")
    return force


def _stream_force_samples(stream: Any, output_path: Path, seconds: float) -> None:
    started = time.monotonic()
    recent = deque(maxlen=18)
    graph_samples = deque(maxlen=1300)
    last_phase = "hold"
    print(f"Writing live Vernier force state to {output_path}")
    while seconds <= 0 or time.monotonic() - started < seconds:
        values = stream.read()
        if not values:
            continue

        at_ms = int((time.monotonic() - started) * 1000)
        force = float(values[0])
        recent.append(force)
        graph_samples.append({"at_ms": at_ms, "force_n": round(force, 3)})
        phase = _phase_from_recent(recent, last_phase)
        last_phase = phase

        payload = {
            "source": "vernier_live",
            "at_ms": at_ms,
            "force_n": round(force, 3),
            "breath_phase": phase,
            "phase_rule": "force rising = inhale; force falling = exhale",
            "sample_count": len(recent),
            "recent_samples": list(graph_samples),
            "updated_at": time.time(),
        }
        output_path.write_text(json.dumps(payload), encoding="utf-8")
        print(json.dumps(payload), flush=True)


def _phase_from_recent(recent: deque[float], previous: str) -> str:
    if len(recent) < 6:
        return "hold"
    first = statistics.mean(list(recent)[:3])
    last = statistics.mean(list(recent)[-3:])
    delta = last - first
    if delta > 0.35:
        return "inhale"
    if delta < -0.35:
        return "exhale"
    return previous if previous in {"inhale", "exhale"} else "hold"


if __name__ == "__main__":
    raise SystemExit(main())
