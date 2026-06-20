"""Run the physiology-aware turn-taking demo."""

from __future__ import annotations

import argparse
import http.server
import json
import subprocess
import socketserver
import sys
import time
from pathlib import Path

from src.ui.dashboard import render_dashboard
from src.ui.breath_phase_screen import render_breath_phase_screen
from src.ui.final_demo_dashboard import render_final_demo_dashboard
from src.ui.film_dashboard import render_film_dashboard
from src.ui.live_voice_dashboard import render_live_voice_dashboard
from src.ui.vernier_breath_dashboard import render_vernier_breath_dashboard


ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build"
DASHBOARD = BUILD_DIR / "dashboard.html"
FILM_DASHBOARD = BUILD_DIR / "film.html"
LIVE_VOICE_DASHBOARD = BUILD_DIR / "live-voice.html"
FINAL_DEMO_DASHBOARD = BUILD_DIR / "final-demo.html"
BREATH_PHASE_SCREEN = BUILD_DIR / "breath.html"
VERNIER_BREATH_DASHBOARD = BUILD_DIR / "vernier.html"
DATA_DIR = ROOT / "data"
DEFAULT_SESSION_ID = "daley_kenny_calibri_001"


class ReusableTcpServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


def _render_page(page_mode: str, session_id: str = DEFAULT_SESSION_ID) -> tuple[Path, str, str]:
    if page_mode == "film":
        return render_film_dashboard(FILM_DASHBOARD), "film.html", "Synthetic/mock Vernier frames."
    if page_mode == "live_voice":
        return render_live_voice_dashboard(LIVE_VOICE_DASHBOARD), "live-voice.html", "Browser speech-to-text plus live/simulated breath gate."
    if page_mode == "final_demo":
        return (
            render_final_demo_dashboard(FINAL_DEMO_DASHBOARD, session_id),
            "final-demo.html",
            "Final local capture page for browser transcript, WAV audio, and Vernier Graphical Analysis markers.",
        )
    if page_mode == "breath":
        return render_breath_phase_screen(BREATH_PHASE_SCREEN), "breath.html", "Minimal inhale/exhale screen using ws://localhost:8765."
    if page_mode == "vernier_breath":
        return (
            render_vernier_breath_dashboard(VERNIER_BREATH_DASHBOARD),
            "vernier.html",
            "Vernier-style inhale/exhale graphs using build/vernier-live.json or simulator fallback.",
        )
    return render_dashboard(DASHBOARD), "dashboard.html", "Synthetic data only."


def run_server(
    port: int,
    page_mode: str,
    session_id: str,
    with_audio: bool,
    audio_device: str | None,
    sample_rate: int,
) -> None:
    _, page, note = _render_page(page_mode, session_id)
    audio_proc: subprocess.Popen[bytes] | None = None

    class BreathHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
            super().__init__(*args, directory=str(BUILD_DIR), **kwargs)

        def do_POST(self) -> None:
            if self.path == "/label":
                self._handle_breath_label()
                return
            if self.path == "/session/start":
                self._handle_session_start()
                return
            if self.path == "/session/marker":
                self._handle_session_marker()
                return
            if self.path == "/session/stop":
                self._handle_session_stop()
                return
            if self.path == "/transcript":
                self._handle_transcript()
                return
            self.send_error(404)

        def _payload(self) -> dict[str, object]:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8")
            return json.loads(raw or "{}")

        def _send_json(self, payload: dict[str, object]) -> None:
            body = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _handle_breath_label(self) -> None:
            try:
                payload = self._payload()
                active_session = str(payload.get("session_id") or session_id)
                label = {
                    "type": "breath_label",
                    "session_id": active_session,
                    "timestamp_ms": time.time_ns() // 1_000_000,
                    "label": str(payload.get("label") or "unknown"),
                    "display_phase": payload.get("display_phase"),
                    "signal_value": payload.get("signal_value"),
                    "source": "breath_screen_keyboard",
                }
                DATA_DIR.mkdir(parents=True, exist_ok=True)
                labels_path = DATA_DIR / f"{active_session}.breath_labels.jsonl"
                events_path = DATA_DIR / f"{active_session}.events.jsonl"
                line = json.dumps(label, separators=(",", ":")) + "\n"
                labels_path.open("a", encoding="utf-8").write(line)
                events_path.open("a", encoding="utf-8").write(line)
                self._send_json({"ok": True, "path": str(labels_path), "label": label})
            except Exception as exc:
                self.send_error(500, str(exc))

        def _handle_session_start(self) -> None:
            nonlocal audio_proc
            try:
                payload = self._payload()
                active_session = str(payload.get("session_id") or session_id)
                DATA_DIR.mkdir(parents=True, exist_ok=True)
                marker = _marker(active_session, "session_start", payload)
                _append_jsonl(_markers_path(active_session), marker)
                _append_jsonl(_events_path(active_session), marker)
                audio_path = DATA_DIR / f"{active_session}.audio.wav"
                if with_audio and audio_proc is None:
                    audio_proc = _start_audio_recorder(audio_path, audio_device, sample_rate)
                if with_audio:
                    audio_event = {
                        "type": "audio",
                        "session_id": active_session,
                        "timestamp_ms": marker["timestamp_ms"],
                        "path": str(audio_path),
                        "sample_rate_hz": sample_rate,
                        "source": audio_device or "default_input",
                    }
                    _append_jsonl(_events_path(active_session), audio_event)
                _write_manifest(active_session, marker, payload, with_audio, audio_device, sample_rate, "running")
                self._send_json({"ok": True, "marker": marker, "paths": _paths(active_session, with_audio)})
            except Exception as exc:
                self.send_error(500, str(exc))

        def _handle_session_marker(self) -> None:
            try:
                payload = self._payload()
                active_session = str(payload.get("session_id") or session_id)
                label = str(payload.get("label") or "marker")
                marker = _marker(active_session, label, payload)
                _append_jsonl(_markers_path(active_session), marker)
                _append_jsonl(_events_path(active_session), marker)
                _merge_manifest(active_session, {f"{label}_at_ms": marker["timestamp_ms"]})
                self._send_json({"ok": True, "marker": marker})
            except Exception as exc:
                self.send_error(500, str(exc))

        def _handle_session_stop(self) -> None:
            nonlocal audio_proc
            try:
                payload = self._payload()
                active_session = str(payload.get("session_id") or session_id)
                marker = _marker(active_session, "session_stop", payload)
                _append_jsonl(_markers_path(active_session), marker)
                _append_jsonl(_events_path(active_session), marker)
                _merge_manifest(active_session, {"session_stopped_at_ms": marker["timestamp_ms"], "status": "stopped"})
                if audio_proc is not None:
                    audio_proc.terminate()
                    try:
                        audio_proc.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        audio_proc.kill()
                    audio_proc = None
                self._send_json({"ok": True, "marker": marker})
            except Exception as exc:
                self.send_error(500, str(exc))

        def _handle_transcript(self) -> None:
            try:
                payload = self._payload()
                active_session = str(payload.get("session_id") or session_id)
                text = str(payload.get("text") or "").strip()
                if not text:
                    self.send_error(400, "Transcript text is required.")
                    return
                event = {
                    "type": "transcript",
                    "session_id": active_session,
                    "timestamp_ms": time.time_ns() // 1_000_000,
                    "speaker": str(payload.get("speaker") or "daley"),
                    "text": text,
                    "is_final": bool(payload.get("is_final", True)),
                    "confidence": payload.get("confidence"),
                    "source": "browser_speech_recognition",
                }
                _append_jsonl(_transcript_path(active_session), event)
                _append_jsonl(_events_path(active_session), event)
                self._send_json({"ok": True, "event": event})
            except Exception as exc:
                self.send_error(500, str(exc))

    try:
        with ReusableTcpServer(("127.0.0.1", port), BreathHandler) as httpd:
            print(f"Dashboard: http://127.0.0.1:{port}/{page}")
            print(note)
            if page_mode == "final_demo":
                print(f"Session: {session_id}")
                print(f"Audio: {'enabled' if with_audio else 'disabled'}")
                print("Privacy: audio, transcript, markers, Vernier exports, and bundles stay local and ignored by git.")
            else:
                print("Privacy: browser mic transcription stays in the page; no audio is saved by this app.")
            httpd.serve_forever()
    finally:
        if audio_proc is not None and audio_proc.poll() is None:
            audio_proc.terminate()
            try:
                audio_proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                audio_proc.kill()


def _append_jsonl(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.open("a", encoding="utf-8").write(json.dumps(payload, separators=(",", ":")) + "\n")


def _events_path(session_id: str) -> Path:
    return DATA_DIR / f"{session_id}.events.jsonl"


def _markers_path(session_id: str) -> Path:
    return DATA_DIR / f"{session_id}.markers.jsonl"


def _transcript_path(session_id: str) -> Path:
    return DATA_DIR / f"{session_id}.transcript.jsonl"


def _manifest_path(session_id: str) -> Path:
    return DATA_DIR / f"{session_id}.manifest.json"


def _marker(session_id: str, label: str, payload: dict[str, object]) -> dict[str, object]:
    return {
        "type": "session_marker",
        "session_id": session_id,
        "timestamp_ms": time.time_ns() // 1_000_000,
        "label": label,
        "notes": str(payload.get("notes") or ""),
        "source": "final_demo_page",
    }


def _paths(session_id: str, with_audio: bool) -> dict[str, str]:
    paths = {
        "events": str(_events_path(session_id)),
        "transcript": str(_transcript_path(session_id)),
        "markers": str(_markers_path(session_id)),
        "manifest": str(_manifest_path(session_id)),
    }
    if with_audio:
        paths["audio"] = str(DATA_DIR / f"{session_id}.audio.wav")
    return paths


def _write_manifest(
    session_id: str,
    marker: dict[str, object],
    payload: dict[str, object],
    with_audio: bool,
    audio_device: str | None,
    sample_rate: int,
    status: str,
) -> None:
    manifest = {
        "session_id": session_id,
        "status": status,
        "session_started_at_ms": marker["timestamp_ms"],
        "notes": str(payload.get("notes") or ""),
        "paths": _paths(session_id, with_audio),
        "audio": {
            "enabled": with_audio,
            "device": audio_device or "default_input",
            "sample_rate_hz": sample_rate,
        },
        "privacy": "Local private capture. Do not commit raw audio, transcripts, biometrics, .gambl, CSV, JSONL, or exports.",
    }
    _manifest_path(session_id).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _merge_manifest(session_id: str, updates: dict[str, object]) -> None:
    path = _manifest_path(session_id)
    manifest: dict[str, object] = {}
    if path.exists():
        manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest.update(updates)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _start_audio_recorder(audio_path: Path, audio_device: str | None, sample_rate: int) -> subprocess.Popen[bytes]:
    cmd = [
        sys.executable,
        "-m",
        "src.audio_recorder",
        "--out",
        str(audio_path),
        "--sample-rate",
        str(sample_rate),
    ]
    if audio_device is not None:
        cmd.extend(["--device", str(audio_device)])
    return subprocess.Popen(cmd, cwd=ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(description="Physiology-aware turn-taking demo runner.")
    parser.add_argument("--mode", choices=["simulator", "vernier"], default="simulator")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--film", action="store_true", help="Render the minimal film-mode dashboard.")
    parser.add_argument("--live-voice", action="store_true", help="Render browser speech-to-text + breath gate dashboard.")
    parser.add_argument("--final-demo", action="store_true", help="Render final Vernier Graphical Analysis + voice capture dashboard.")
    parser.add_argument("--breath-screen", action="store_true", help="Render minimal inhale/exhale screen.")
    parser.add_argument("--vernier-breath", action="store_true", help="Render Vernier-style inhale/exhale graph screen.")
    parser.add_argument("--session-id", default=DEFAULT_SESSION_ID)
    parser.add_argument("--with-audio", action="store_true", help="Record local WAV audio when final-demo session starts.")
    parser.add_argument("--audio-device", default=None, help="Optional sounddevice input name/index for final-demo WAV recording.")
    parser.add_argument("--sample-rate", type=int, default=48000)
    parser.add_argument("--once", action="store_true", help="Render dashboard and exit.")
    args = parser.parse_args()

    if args.mode == "vernier":
        print("Vernier live mode is stubbed. Use --mode simulator for the current demo.")
        return 2

    page_mode = (
        "vernier_breath"
        if args.vernier_breath
        else "breath"
        if args.breath_screen
        else "final_demo"
        if args.final_demo
        else "live_voice"
        if args.live_voice
        else "film"
        if args.film
        else "dashboard"
    )
    path, _, _ = _render_page(page_mode, args.session_id)
    print(f"Rendered dashboard: {path}")
    if args.once:
        return 0

    run_server(args.port, page_mode, args.session_id, args.with_audio, args.audio_device, args.sample_rate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
