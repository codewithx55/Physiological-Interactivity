"""Live biometric + audio capture stream for Kenny."""

from __future__ import annotations

import argparse
import asyncio
import subprocess
import sys
from pathlib import Path

from src.csv_writer import CaptureWriter
from src.events import AudioEvent, TranscriptEvent, now_ms
from src.mock_sensor import MockSensor
from src.sensors.callibri_sensor import CallibriSensor
from src.websocket_server import WebSocketBroadcaster


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stream biometrics + optional mic capture.")
    parser.add_argument("--device", choices=["mock", "callibri", "vernier"], default="mock")
    parser.add_argument("--session-id", default="daley_kenny_calibri_001")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--out-dir", type=Path, default=Path("data"))
    parser.add_argument("--rate-hz", type=float, default=4)
    parser.add_argument("--with-audio", action="store_true")
    parser.add_argument("--audio-device", default=None, help="Optional sounddevice input name/index.")
    parser.add_argument("--sample-rate", type=int, default=48000)
    parser.add_argument("--transcript-note", default="", help="Optional manual label for the session.")
    parser.add_argument("--no-fallback", action="store_true")
    return parser.parse_args()


def make_sensor(args: argparse.Namespace) -> MockSensor | CallibriSensor:
    if args.device == "callibri":
        return CallibriSensor(args.session_id, args.rate_hz)
    if args.device == "vernier":
        raise RuntimeError("Vernier adapter is not wired into src.main yet; use tools/vernier_stream.py or --device mock.")
    return MockSensor(args.session_id, args.rate_hz)


async def stream_sensor(args: argparse.Namespace, writer: CaptureWriter, broadcaster: WebSocketBroadcaster) -> None:
    sensor = make_sensor(args)
    try:
        async for event in sensor.events():
            payload = writer.write(event)
            await broadcaster.broadcast(payload)
            print(payload, flush=True)
    except RuntimeError as exc:
        if args.no_fallback or args.device == "mock":
            raise
        print(f"{exc}\nFalling back to mock biometrics.", file=sys.stderr)
        args.device = "mock"
        sensor = MockSensor(args.session_id, args.rate_hz)
        async for event in sensor.events():
            payload = writer.write(event)
            await broadcaster.broadcast(payload)
            print(payload, flush=True)


async def record_audio(args: argparse.Namespace, writer: CaptureWriter, broadcaster: WebSocketBroadcaster) -> None:
    if not args.with_audio:
        return
    audio_path = args.out_dir / f"{args.session_id}.audio.wav"
    audio_path.parent.mkdir(parents=True, exist_ok=True)

    event = AudioEvent(
        session_id=args.session_id,
        timestamp_ms=now_ms(),
        path=str(audio_path),
        sample_rate_hz=args.sample_rate,
        source=args.audio_device or "default_input",
    )
    await broadcaster.broadcast(writer.write(event))
    print(event.to_json(), flush=True)

    cmd = [
        sys.executable,
        "-m",
        "src.audio_recorder",
        "--out",
        str(audio_path),
        "--sample-rate",
        str(args.sample_rate),
    ]
    if args.audio_device is not None:
        cmd.extend(["--device", str(args.audio_device)])
    proc = subprocess.Popen(cmd, cwd=Path(__file__).resolve().parents[1])
    try:
        while proc.poll() is None:
            await asyncio.sleep(0.25)
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()


async def emit_transcript_note(args: argparse.Namespace, writer: CaptureWriter, broadcaster: WebSocketBroadcaster) -> None:
    if not args.transcript_note:
        return
    event = TranscriptEvent(
        session_id=args.session_id,
        timestamp_ms=now_ms(),
        speaker="daley",
        text=args.transcript_note,
        is_final=True,
        source="manual_session_label",
    )
    await broadcaster.broadcast(writer.write(event))
    print(event.to_json(), flush=True)


async def amain() -> int:
    args = parse_args()
    writer = CaptureWriter(args.out_dir, args.session_id)
    broadcaster = WebSocketBroadcaster(args.host, args.port)
    await broadcaster.start()
    await emit_transcript_note(args, writer, broadcaster)
    print(f"WebSocket: ws://{args.host}:{args.port}")
    print(f"Events: {writer.events_path}")
    print(f"Biometrics CSV: {writer.csv_path}")
    if args.with_audio:
        print(f"Audio: {args.out_dir / f'{args.session_id}.audio.wav'}")
    print("Stop with Ctrl+C.")

    tasks = [
        asyncio.create_task(stream_sensor(args, writer, broadcaster)),
        asyncio.create_task(record_audio(args, writer, broadcaster)),
    ]
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        return 0
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await broadcaster.stop()
        writer.close()


def main() -> int:
    try:
        return asyncio.run(amain())
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
