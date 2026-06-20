#!/usr/bin/env python3
"""Import Vernier Graphical Analysis .gambl force data into local events."""

from __future__ import annotations

import argparse
import csv
import json
import tarfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Column:
    id: int
    name: str
    unit: str
    start_time_s: float
    values: list[float]


def main() -> int:
    parser = argparse.ArgumentParser(description="Import Vernier .gambl force samples.")
    parser.add_argument("gambl", type=Path)
    parser.add_argument("--session-id", default=None)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--markers", type=Path, default=None, help="Session markers JSONL; uses vernier_start as the time-zero anchor.")
    parser.add_argument("--start-timestamp-ms", type=int, default=None, help="Wall-clock timestamp for Vernier Time(s)=0.")
    args = parser.parse_args()

    session_id = args.session_id or args.gambl.stem
    alignment_start_ms = args.start_timestamp_ms
    alignment_source = "gambl_column_start_time"
    if alignment_start_ms is None and args.markers is not None:
        alignment_start_ms = read_marker_timestamp(args.markers, "vernier_start")
        alignment_source = str(args.markers)
    elif alignment_start_ms is not None:
        alignment_source = "start_timestamp_ms_arg"

    columns, x_id, y_id = read_gambl(args.gambl)
    time_col = columns[x_id]
    force_col = columns[y_id]
    rows = build_rows(session_id, args.gambl, time_col, force_col, alignment_start_ms)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    events_path = args.out_dir / f"{session_id}.events.jsonl"
    csv_path = args.out_dir / f"{session_id}.vernier_force.csv"
    summary_path = args.out_dir / f"{session_id}.gambl-summary.json"

    event_mode = "a" if alignment_start_ms is not None else "w"
    with events_path.open(event_mode, encoding="utf-8") as out:
        for row in rows:
            out.write(json.dumps(row["event"], separators=(",", ":")) + "\n")

    with csv_path.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(
            out,
            fieldnames=[
                "timestamp_ms",
                "time_s",
                "force_n",
                "breath_phase",
                "source_file",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row["csv"])

    summary = {
        "source_file": str(args.gambl),
        "session_id": session_id,
        "time_column_id": time_col.id,
        "force_column_id": force_col.id,
        "start_time_s": time_col.start_time_s,
        "alignment_start_timestamp_ms": alignment_start_ms,
        "alignment_source": alignment_source,
        "events_mode": event_mode,
        "sample_count": len(rows),
        "first_timestamp_ms": rows[0]["event"]["timestamp_ms"] if rows else None,
        "last_timestamp_ms": rows[-1]["event"]["timestamp_ms"] if rows else None,
        "event_path": str(events_path),
        "csv_path": str(csv_path),
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0


def read_marker_timestamp(path: Path, label: str) -> int:
    if not path.exists():
        raise RuntimeError(f"Markers file does not exist: {path}")
    fallback: int | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        timestamp = event.get("timestamp_ms")
        if not isinstance(timestamp, int):
            continue
        if event.get("label") == label:
            return timestamp
        if event.get("label") == "session_start" and fallback is None:
            fallback = timestamp
    if fallback is not None:
        return fallback
    raise RuntimeError(f"Could not find {label} or session_start in markers file: {path}")


def read_gambl(path: Path) -> tuple[dict[int, Column], int, int]:
    with tarfile.open(path) as bundle:
        member = bundle.extractfile("vstudm/data.udm")
        if member is None:
            raise RuntimeError("Missing vstudm/data.udm inside .gambl file.")
        root = ET.fromstring(member.read())

    columns = {
        column.id: column
        for column in (_parse_column(node) for node in root.findall(".//DataColumn"))
        if column.values
    }
    x_id, y_id = _select_force_trace(root, columns)
    return columns, x_id, y_id


def _parse_column(node: ET.Element) -> Column:
    id_text = node.findtext("ID") or "0"
    cells = node.findtext("ColumnCells") or ""
    return Column(
        id=int(id_text),
        name=node.findtext("DataObjectName") or "",
        unit=node.findtext("ColumnUnits") or "",
        start_time_s=float(node.findtext("StartTime") or node.findtext("ColumnStartCollectTime") or 0),
        values=_parse_numeric_cells(cells),
    )


def _parse_numeric_cells(cells: str) -> list[float]:
    values: list[float] = []
    for raw in cells.splitlines():
        text = raw.strip()
        if not text:
            continue
        try:
            values.append(float(text))
        except ValueError:
            # Vernier uses compact repeated-value markers in some derived columns.
            # Force and Time columns are numeric in the files we import.
            continue
    return values


def _select_force_trace(root: ET.Element, columns: dict[int, Column]) -> tuple[int, int]:
    for graph in root.findall(".//PageGraphCartesian"):
        pairs_text = graph.findtext("GraphPlotTraceIDPairs") or ""
        ints = [int(part) for part in pairs_text.split() if part.lstrip("-").isdigit()]
        for index in range(0, len(ints) - 2, 3):
            x_id = ints[index + 1]
            y_id = ints[index + 2]
            x_col = columns.get(x_id)
            y_col = columns.get(y_id)
            if x_col and y_col and x_col.name.lower() == "time" and y_col.name.lower() == "force":
                return x_id, y_id

    time_cols = [column for column in columns.values() if column.name.lower() == "time"]
    force_cols = [column for column in columns.values() if column.name.lower() == "force"]
    if not time_cols or not force_cols:
        raise RuntimeError("Could not find Time and Force columns in .gambl file.")
    time_col = max(time_cols, key=lambda column: column.id)
    force_col = max(force_cols, key=lambda column: column.id)
    return time_col.id, force_col.id


def build_rows(
    session_id: str,
    source_file: Path,
    time_col: Column,
    force_col: Column,
    alignment_start_ms: int | None = None,
) -> list[dict[str, object]]:
    count = min(len(time_col.values), len(force_col.values))
    rows: list[dict[str, object]] = []
    previous_force: float | None = None
    phase = "hold"

    for index in range(count):
        time_s = time_col.values[index]
        force_n = force_col.values[index]
        if previous_force is not None:
            delta = force_n - previous_force
            if delta > 0.25:
                phase = "inhale"
            elif delta < -0.25:
                phase = "exhale"
        previous_force = force_n

        if alignment_start_ms is None:
            timestamp_ms = int(round((time_col.start_time_s + time_s) * 1000))
        else:
            timestamp_ms = int(round(alignment_start_ms + time_s * 1000))
        event = {
            "type": "biometric",
            "session_id": session_id,
            "device": "vernier_gambl",
            "timestamp_ms": timestamp_ms,
            "signal": "respiration_force",
            "value": round(force_n, 6),
            "unit": "N",
            "quality": 1.0,
            "breath_phase": phase,
            "source_file": str(source_file),
            "relative_time_s": round(time_s, 6),
            "alignment_start_timestamp_ms": alignment_start_ms,
        }
        rows.append(
            {
                "event": event,
                "csv": {
                    "timestamp_ms": timestamp_ms,
                    "time_s": round(time_s, 6),
                    "force_n": round(force_n, 6),
                    "breath_phase": phase,
                    "source_file": str(source_file),
                },
            }
        )
    return rows


if __name__ == "__main__":
    raise SystemExit(main())
