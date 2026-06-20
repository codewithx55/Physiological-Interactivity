"""Append-only capture writers."""

from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path
from typing import Any

from src.events import AudioEvent, BiometricEvent, TranscriptEvent


class CaptureWriter:
    def __init__(self, out_dir: Path, session_id: str) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path = Path("build") / "breath-latest.json"
        self.latest_path.parent.mkdir(parents=True, exist_ok=True)
        self.events_path = out_dir / f"{session_id}.events.jsonl"
        self.csv_path = out_dir / f"{session_id}.biometrics.csv"
        self.transcript_path = out_dir / f"{session_id}.transcript.jsonl"
        self._jsonl = self.events_path.open("a", encoding="utf-8")
        self._transcript = self.transcript_path.open("a", encoding="utf-8")
        self._csv_file = self.csv_path.open("a", newline="", encoding="utf-8")
        self._csv = csv.DictWriter(
            self._csv_file,
            fieldnames=[
                "timestamp_ms",
                "session_id",
                "device",
                "signal",
                "value",
                "unit",
                "quality",
            ],
        )
        if self.csv_path.stat().st_size == 0:
            self._csv.writeheader()

    def write(self, event: BiometricEvent | TranscriptEvent | AudioEvent) -> str:
        payload = event.to_json()
        self._jsonl.write(payload + "\n")
        self._jsonl.flush()
        if isinstance(event, BiometricEvent):
            row: dict[str, Any] = asdict(event)
            row.pop("type", None)
            self._csv.writerow(row)
            self._csv_file.flush()
            if event.signal == "respiration_force":
                self.latest_path.write_text(payload, encoding="utf-8")
        if isinstance(event, TranscriptEvent):
            self._transcript.write(payload + "\n")
            self._transcript.flush()
        return payload

    def close(self) -> None:
        self._jsonl.close()
        self._transcript.close()
        self._csv_file.close()
