#!/usr/bin/env python3
"""Sanity-check Vernier Go Direct availability without recording data."""

from __future__ import annotations

import sys


def main() -> int:
    try:
        import godirect  # type: ignore
    except ImportError:
        print("godirect is not installed.")
        print("Install it with: python3 -m pip install godirect")
        print("Then connect the Vernier Go Direct Respiration Belt over USB first.")
        return 2

    print("godirect import: ok")
    print(f"godirect module: {getattr(godirect, '__file__', 'unknown')}")
    print()
    print("Next hardware check:")
    print("1. Connect the Vernier Go Direct Respiration Belt over USB.")
    print("2. Run Vernier's getting-started example to list channels.")
    print("3. Map the respiration channel into src/sensors/vernier_respiration.py.")
    print()
    print("No sensor data was recorded or written by this check.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
