#!/usr/bin/env python3
"""Run local checks for the physiology interactivity demo."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str]) -> int:
    print(f"$ {' '.join(args)}", flush=True)
    result = subprocess.run(args, cwd=ROOT, text=True, check=False)
    print(flush=True)
    return result.returncode


def main() -> int:
    checks = [
        [sys.executable, "-m", "src.turn_taking.evaluator"],
        [sys.executable, "tools/export_eval_report.py", "--json"],
        [sys.executable, "tools/build_demo_viewer.py"],
        [sys.executable, "-m", "src.app", "--mode", "simulator", "--once"],
        [sys.executable, "-m", "src.app", "--mode", "simulator", "--film", "--once"],
        [sys.executable, "-m", "src.app", "--mode", "simulator", "--live-voice", "--once"],
    ]
    for check in checks:
        code = run(check)
        if code != 0:
            return code
    print("Smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
