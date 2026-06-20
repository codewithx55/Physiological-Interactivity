"""Standalone WAV recorder used by src.main.

CoreAudio is most reliable when sounddevice recording runs in the process main
thread, so the live stream launches this module as a helper process.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import signal
import wave


def main() -> int:
    parser = argparse.ArgumentParser(description="Record microphone audio to WAV.")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--device", default=None)
    parser.add_argument("--sample-rate", type=int, default=48000)
    args = parser.parse_args()

    import sounddevice as sd

    device: int | str | None = args.device
    if isinstance(device, str) and device.isdigit():
        device = int(device)

    running = True

    def stop(signum, frame) -> None:  # type: ignore[no-untyped-def]
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    chunk_frames = int(args.sample_rate * 0.25)
    with wave.open(str(args.out), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(args.sample_rate)
        while running:
            audio = sd.rec(
                chunk_frames,
                samplerate=args.sample_rate,
                channels=1,
                dtype="int16",
                device=device,
            )
            sd.wait()
            wav.writeframes(audio.tobytes())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
