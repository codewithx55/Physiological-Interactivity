#!/usr/bin/env python3
"""Check whether likely physiology hardware is visible on this Mac."""

from __future__ import annotations

import shutil
import subprocess


TERMS = (
    "vernier",
    "go direct",
    "gdx",
    "respiration",
    "callibri",
    "calibri",
    "brainbit",
    "heart",
    "polar",
)


def main() -> int:
    if not shutil.which("system_profiler"):
        print("system_profiler is not available on this machine.")
        return 2

    usb = _profile("SPUSBDataType")
    bluetooth = _profile("SPBluetoothDataType")
    matches = _matches("USB", usb) + _matches("Bluetooth", bluetooth)

    print("Hardware visibility check")
    print()
    if matches:
        for match in matches:
            print(match)
    else:
        print("No Vernier, Callibri/Calibri, BrainBit, or heart-rate device is visible over USB/Bluetooth.")

    print()
    try:
        import godirect  # type: ignore
    except ImportError:
        print("Vernier SDK: missing godirect")
        print("Install when ready: python3 -m pip install godirect")
    else:
        print(f"Vernier SDK: godirect import ok ({getattr(godirect, '__file__', 'unknown')})")

    print()
    print("Privacy: this command reads device names only; it does not record sensor data.")
    return 0 if matches else 1


def _profile(data_type: str) -> str:
    result = subprocess.run(
        ["system_profiler", data_type],
        check=False,
        text=True,
        capture_output=True,
    )
    return result.stdout


def _matches(label: str, text: str) -> list[str]:
    lines = text.splitlines()
    found: list[str] = []
    for index, line in enumerate(lines):
        lower = line.lower()
        if any(term in lower for term in TERMS):
            start = max(0, index - 2)
            end = min(len(lines), index + 3)
            snippet = "\n".join(lines[start:end])
            found.append(f"[{label}]\n{snippet}")
    return found


if __name__ == "__main__":
    raise SystemExit(main())
