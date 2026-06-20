"""Run the physiology-aware turn-taking demo."""

from __future__ import annotations

import argparse
import http.server
import json
import socketserver
import time
from pathlib import Path

from src.ui.dashboard import render_dashboard
from src.ui.breath_phase_screen import render_breath_phase_screen
from src.ui.film_dashboard import render_film_dashboard
from src.ui.live_voice_dashboard import render_live_voice_dashboard


ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build"
DASHBOARD = BUILD_DIR / "dashboard.html"
FILM_DASHBOARD = BUILD_DIR / "film.html"
LIVE_VOICE_DASHBOARD = BUILD_DIR / "live-voice.html"
BREATH_PHASE_SCREEN = BUILD_DIR / "breath.html"
DATA_DIR = ROOT / "data"
DEFAULT_SESSION_ID = "daley_kenny_calibri_001"


class ReusableTcpServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


def _render_page(page_mode: str) -> tuple[Path, str, str]:
    if page_mode == "film":
        return render_film_dashboard(FILM_DASHBOARD), "film.html", "Synthetic/mock Vernier frames."
    if page_mode == "live_voice":
        return render_live_voice_dashboard(LIVE_VOICE_DASHBOARD), "live-voice.html", "Browser speech-to-text plus live/simulated breath gate."
    if page_mode == "breath":
        return render_breath_phase_screen(BREATH_PHASE_SCREEN), "breath.html", "Minimal inhale/exhale screen using ws://localhost:8765."
    return render_dashboard(DASHBOARD), "dashboard.html", "Synthetic data only."


def run_server(port: int, page_mode: str) -> None:
    _, page, note = _render_page(page_mode)

    class BreathHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
            super().__init__(*args, directory=str(BUILD_DIR), **kwargs)

        def do_POST(self) -> None:
            if self.path != "/label":
                self.send_error(404)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length).decode("utf-8")
                payload = json.loads(raw or "{}")
                session_id = str(payload.get("session_id") or DEFAULT_SESSION_ID)
                label = {
                    "type": "breath_label",
                    "session_id": session_id,
                    "timestamp_ms": time.time_ns() // 1_000_000,
                    "label": str(payload.get("label") or "unknown"),
                    "display_phase": payload.get("display_phase"),
                    "signal_value": payload.get("signal_value"),
                    "source": "breath_screen_keyboard",
                }
                DATA_DIR.mkdir(parents=True, exist_ok=True)
                labels_path = DATA_DIR / f"{session_id}.breath_labels.jsonl"
                events_path = DATA_DIR / f"{session_id}.events.jsonl"
                line = json.dumps(label, separators=(",", ":")) + "\n"
                labels_path.open("a", encoding="utf-8").write(line)
                events_path.open("a", encoding="utf-8").write(line)
                body = json.dumps({"ok": True, "path": str(labels_path), "label": label}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as exc:
                self.send_error(500, str(exc))

    with ReusableTcpServer(("127.0.0.1", port), BreathHandler) as httpd:
        print(f"Dashboard: http://127.0.0.1:{port}/{page}")
        print(note)
        print("Privacy: browser mic transcription stays in the page; no audio is saved by this app.")
        httpd.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description="Physiology-aware turn-taking demo runner.")
    parser.add_argument("--mode", choices=["simulator", "vernier"], default="simulator")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--film", action="store_true", help="Render the minimal film-mode dashboard.")
    parser.add_argument("--live-voice", action="store_true", help="Render browser speech-to-text + breath gate dashboard.")
    parser.add_argument("--breath-screen", action="store_true", help="Render minimal inhale/exhale screen.")
    parser.add_argument("--once", action="store_true", help="Render dashboard and exit.")
    args = parser.parse_args()

    if args.mode == "vernier":
        print("Vernier live mode is stubbed. Use --mode simulator for the current demo.")
        return 2

    page_mode = "breath" if args.breath_screen else "live_voice" if args.live_voice else "film" if args.film else "dashboard"
    path, _, _ = _render_page(page_mode)
    print(f"Rendered dashboard: {path}")
    if args.once:
        return 0

    run_server(args.port, page_mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
