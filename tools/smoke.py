#!/usr/bin/env python3
"""Run local checks for the physiology interactivity demo."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str]) -> int:
    print(f"$ {' '.join(args)}", flush=True)
    result = subprocess.run(args, cwd=ROOT, text=True, check=False)
    print(flush=True)
    return result.returncode


def post_json(port: int, path: str, payload: dict[str, object]) -> dict[str, object]:
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def wait_for_server(port: int) -> None:
    url = f"http://127.0.0.1:{port}/final-demo.html"
    deadline = time.time() + 8
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.2)
    raise RuntimeError("Final demo server did not start.")


def run_final_demo_endpoint_smoke() -> int:
    session_id = "final_demo_smoke"
    port = 8799
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "src.app",
            "--mode",
            "simulator",
            "--final-demo",
            "--session-id",
            session_id,
            "--port",
            str(port),
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        wait_for_server(port)
        post_json(port, "/session/start", {"session_id": session_id, "notes": "smoke"})
        post_json(port, "/transcript", {"session_id": session_id, "text": "smoke transcript", "is_final": True})
        post_json(port, "/session/marker", {"session_id": session_id, "label": "vernier_start"})
        post_json(port, "/session/marker", {"session_id": session_id, "label": "vernier_stop"})
        post_json(port, "/session/stop", {"session_id": session_id})
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
    return 0


def main() -> int:
    checks = [
        [sys.executable, "-m", "src.turn_taking.evaluator"],
        [sys.executable, "tools/export_eval_report.py", "--json"],
        [sys.executable, "tools/build_demo_viewer.py"],
        [sys.executable, "-m", "src.app", "--mode", "simulator", "--once"],
        [sys.executable, "-m", "src.app", "--mode", "simulator", "--film", "--once"],
        [sys.executable, "-m", "src.app", "--mode", "simulator", "--live-voice", "--once"],
        [sys.executable, "-m", "src.app", "--mode", "simulator", "--final-demo", "--session-id", "final_demo_smoke", "--once"],
        [sys.executable, "-m", "src.app", "--mode", "simulator", "--vernier-breath", "--once"],
    ]
    for check in checks:
        code = run(check)
        if code != 0:
            return code
    code = run_final_demo_endpoint_smoke()
    if code != 0:
        return code
    gambl_fixture = ROOT / "vernierp1test.gambl"
    if gambl_fixture.exists():
        for check in [
            [
                sys.executable,
                "tools/import_gambl.py",
                str(gambl_fixture),
                "--session-id",
                "vernierp1test_smoke",
            ],
            [
                sys.executable,
                "tools/import_gambl.py",
                str(gambl_fixture),
                "--session-id",
                "final_demo_smoke",
                "--markers",
                "data/final_demo_smoke.markers.jsonl",
            ],
            [sys.executable, "tools/export_session_bundle.py", "--session-id", "final_demo_smoke"],
        ]:
            code = run(check)
            if code != 0:
                return code
    print("Smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
