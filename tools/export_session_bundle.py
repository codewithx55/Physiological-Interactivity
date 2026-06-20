#!/usr/bin/env python3
"""Create a Kenny-ready local bundle for one Vernier + voice session."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
EXPORTS_DIR = ROOT / "exports"


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a local session bundle for Kenny.")
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--out-dir", type=Path, default=EXPORTS_DIR)
    args = parser.parse_args()

    bundle_dir = args.out_dir / args.session_id
    bundle_dir.mkdir(parents=True, exist_ok=True)

    paths = SessionPaths(args.data_dir, args.session_id)
    copied = copy_artifacts(paths, bundle_dir)
    transcript_csv = write_transcript_csv(paths.transcript, bundle_dir / f"{args.session_id}.transcript.csv")
    merged_csv = write_merged_timeline(paths, bundle_dir / f"{args.session_id}.merged_timeline.csv")
    pairing_csv = write_pairing_csv(paths, bundle_dir / f"{args.session_id}.breath_word_pairing.csv")
    replay_html = write_replay_html(args.session_id, paths, bundle_dir / f"{args.session_id}.kenny_replay.html", pairing_csv)
    manifest = build_manifest(args.session_id, paths, bundle_dir, copied, transcript_csv, merged_csv, pairing_csv, replay_html)
    manifest_path = bundle_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    readme_path = bundle_dir / "README.md"
    readme_path.write_text(readme(args.session_id, manifest), encoding="utf-8")

    print(json.dumps({"bundle_dir": str(bundle_dir), "manifest": str(manifest_path), "readme": str(readme_path)}, indent=2))
    return 0


class SessionPaths:
    def __init__(self, data_dir: Path, session_id: str) -> None:
        self.data_dir = data_dir
        self.session_id = session_id
        self.events = data_dir / f"{session_id}.events.jsonl"
        self.transcript = data_dir / f"{session_id}.transcript.jsonl"
        self.markers = data_dir / f"{session_id}.markers.jsonl"
        self.audio = data_dir / f"{session_id}.audio.wav"
        self.force_csv = data_dir / f"{session_id}.vernier_force.csv"
        self.gambl_summary = data_dir / f"{session_id}.gambl-summary.json"
        self.session_manifest = data_dir / f"{session_id}.manifest.json"


def copy_artifacts(paths: SessionPaths, bundle_dir: Path) -> dict[str, str]:
    copied: dict[str, str] = {}
    for label, source in [
        ("events_jsonl", paths.events),
        ("transcript_jsonl", paths.transcript),
        ("markers_jsonl", paths.markers),
        ("audio_wav", paths.audio),
        ("vernier_force_csv", paths.force_csv),
        ("gambl_summary_json", paths.gambl_summary),
        ("session_manifest_json", paths.session_manifest),
    ]:
        if source.exists():
            target = bundle_dir / source.name
            shutil.copy2(source, target)
            copied[label] = str(target)

    source_gambl = source_gambl_path(paths.gambl_summary)
    if source_gambl and source_gambl.exists():
        target = bundle_dir / source_gambl.name
        shutil.copy2(source_gambl, target)
        copied["source_gambl"] = str(target)
    return copied


def source_gambl_path(summary_path: Path) -> Path | None:
    if not summary_path.exists():
        return None
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    source = summary.get("source_file")
    if not isinstance(source, str) or not source:
        return None
    return Path(source)


def write_transcript_csv(source: Path, target: Path) -> str | None:
    rows = read_jsonl(source)
    if not rows:
        return None
    with target.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(
            out,
            fieldnames=["timestamp_ms", "speaker", "text", "is_final", "confidence", "source"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "timestamp_ms": row.get("timestamp_ms", ""),
                    "speaker": row.get("speaker", ""),
                    "text": row.get("text", ""),
                    "is_final": row.get("is_final", ""),
                    "confidence": row.get("confidence", ""),
                    "source": row.get("source", ""),
                }
            )
    return str(target)


def write_merged_timeline(paths: SessionPaths, target: Path) -> str:
    session_start = first_marker_ms(paths.markers) or first_event_ms(paths.events)
    rows: list[dict[str, Any]] = []

    for marker in read_jsonl(paths.markers):
        rows.append(
            timeline_row(
                session_start,
                marker.get("timestamp_ms"),
                "marker",
                marker.get("label"),
                notes=marker.get("notes"),
            )
        )

    for transcript in read_jsonl(paths.transcript):
        rows.append(
            timeline_row(
                session_start,
                transcript.get("timestamp_ms"),
                "transcript",
                transcript.get("text"),
                speaker=transcript.get("speaker"),
                confidence=transcript.get("confidence"),
            )
        )

    if paths.force_csv.exists():
        with paths.force_csv.open(newline="", encoding="utf-8") as src:
            for force in csv.DictReader(src):
                rows.append(
                    timeline_row(
                        session_start,
                        parse_int(force.get("timestamp_ms")),
                        "vernier_force",
                        "",
                        force_n=force.get("force_n"),
                        breath_phase=force.get("breath_phase"),
                        source_file=force.get("source_file"),
                    )
                )

    if paths.audio.exists():
        rows.append(
            timeline_row(
                session_start,
                first_event_ms(paths.events),
                "audio",
                str(paths.audio),
            )
        )

    rows.sort(key=lambda row: (row["timestamp_ms"] == "", row["timestamp_ms"]))
    with target.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(
            out,
            fieldnames=[
                "timestamp_ms",
                "relative_time_s",
                "type",
                "value",
                "speaker",
                "force_n",
                "breath_phase",
                "confidence",
                "notes",
                "source_file",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    return str(target)


def write_pairing_csv(paths: SessionPaths, target: Path) -> str:
    force_rows = read_force_rows(paths.force_csv)
    transcript_rows = read_jsonl(paths.transcript)
    with target.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(
            out,
            fieldnames=[
                "transcript_timestamp_ms",
                "transcript_relative_time_s",
                "text",
                "nearest_force_timestamp_ms",
                "nearest_force_relative_time_s",
                "nearest_force_n",
                "nearest_breath_phase",
                "delta_ms",
                "pairing_status",
            ],
        )
        writer.writeheader()
        for transcript in transcript_rows:
            timestamp = parse_int(transcript.get("timestamp_ms"))
            nearest = nearest_force(timestamp, force_rows)
            if timestamp is None or nearest is None:
                writer.writerow(
                    {
                        "transcript_timestamp_ms": timestamp or "",
                        "transcript_relative_time_s": "",
                        "text": transcript.get("text", ""),
                        "nearest_force_timestamp_ms": "",
                        "nearest_force_relative_time_s": "",
                        "nearest_force_n": "",
                        "nearest_breath_phase": "",
                        "delta_ms": "",
                        "pairing_status": "missing_force_or_transcript_time",
                    }
                )
                continue
            delta_ms = timestamp - nearest["timestamp_ms"]
            writer.writerow(
                {
                    "transcript_timestamp_ms": timestamp,
                    "transcript_relative_time_s": "",
                    "text": transcript.get("text", ""),
                    "nearest_force_timestamp_ms": nearest["timestamp_ms"],
                    "nearest_force_relative_time_s": nearest.get("time_s", ""),
                    "nearest_force_n": nearest.get("force_n", ""),
                    "nearest_breath_phase": nearest.get("breath_phase", ""),
                    "delta_ms": delta_ms,
                    "pairing_status": "paired" if abs(delta_ms) <= 500 else "no_overlap",
                }
            )
    return str(target)


def write_replay_html(session_id: str, paths: SessionPaths, target: Path, pairing_csv: str) -> str:
    force_rows = read_force_rows(paths.force_csv)
    transcript_rows = read_jsonl(paths.transcript)
    marker_rows = read_jsonl(paths.markers)
    session_start = first_marker_ms(paths.markers) or first_event_ms(paths.events)
    force_duration = 0.0
    if force_rows:
        force_duration = (force_rows[-1]["timestamp_ms"] - force_rows[0]["timestamp_ms"]) / 1000
    first_transcript_delta = None
    if force_rows and transcript_rows:
        first_transcript = parse_int(transcript_rows[0].get("timestamp_ms"))
        if first_transcript is not None:
            first_transcript_delta = round((first_transcript - force_rows[-1]["timestamp_ms"]) / 1000, 3)
    payload = {
        "session_id": session_id,
        "session_start_ms": session_start,
        "force_rows": force_rows,
        "transcript_rows": transcript_rows,
        "marker_rows": marker_rows,
        "pairing_csv": Path(pairing_csv).name,
        "force_duration_s": round(force_duration, 3),
        "first_transcript_after_force_s": first_transcript_delta,
    }
    target.write_text(replay_template(payload), encoding="utf-8")
    return str(target)


def read_force_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as src:
        for row in csv.DictReader(src):
            timestamp = parse_int(row.get("timestamp_ms"))
            if timestamp is None:
                continue
            rows.append(
                {
                    "timestamp_ms": timestamp,
                    "time_s": parse_float(row.get("time_s")),
                    "force_n": parse_float(row.get("force_n")),
                    "breath_phase": row.get("breath_phase", ""),
                }
            )
    return rows


def nearest_force(timestamp_ms: int | None, force_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if timestamp_ms is None or not force_rows:
        return None
    return min(force_rows, key=lambda row: abs(int(row["timestamp_ms"]) - timestamp_ms))


def replay_template(payload: dict[str, Any]) -> str:
    data = json.dumps(payload)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Kenny Breath + Word Replay</title>
  <style>
    :root {{ --ink:#151817; --muted:#66716c; --line:#d8ded9; --paper:#f6f7f3; --panel:#fff; --green:#217a57; --red:#b64b47; --gold:#a7741f; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--paper); color: var(--ink); font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; letter-spacing: 0; }}
    main {{ width: min(1200px, calc(100vw - 32px)); margin: 16px auto; display: grid; gap: 12px; }}
    section {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 16px; }}
    h1 {{ margin: 0; font-size: 24px; }}
    h2 {{ margin: 0 0 10px; font-size: 16px; }}
    .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }}
    .metric {{ border: 1px solid var(--line); border-radius: 8px; padding: 10px; }}
    .label {{ color: var(--muted); font-size: 12px; font-weight: 800; text-transform: uppercase; }}
    .value {{ margin-top: 6px; font-size: 22px; font-weight: 850; }}
    .warning {{ border-color: #e3c36b; background: #fff7df; }}
    canvas {{ width: 100%; height: 260px; border: 1px solid var(--line); border-radius: 8px; background: #fbfcfa; display: block; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 8px; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-size: 11px; text-transform: uppercase; }}
    .no {{ color: var(--red); font-weight: 800; }}
    .yes {{ color: var(--green); font-weight: 800; }}
    .phase {{ font-weight: 800; }}
    @media (max-width: 900px) {{ .summary {{ grid-template-columns: 1fr 1fr; }} }}
  </style>
</head>
<body>
<main>
  <section>
    <h1>Kenny Breath + Word Replay</h1>
    <p id="subtitle"></p>
  </section>
  <section class="summary">
    <div class="metric"><div class="label">Force Samples</div><div class="value" id="forceCount"></div></div>
    <div class="metric"><div class="label">Force Duration</div><div class="value" id="forceDuration"></div></div>
    <div class="metric"><div class="label">Transcript Events</div><div class="value" id="transcriptCount"></div></div>
    <div class="metric warning"><div class="label">Pairing Result</div><div class="value" id="pairingResult"></div></div>
  </section>
  <section>
    <h2>Force Trace + Transcript Timing</h2>
    <canvas id="chart" width="1160" height="260"></canvas>
  </section>
  <section>
    <h2>Breath/Word Pairing Table</h2>
    <table>
      <thead><tr><th>Speech Time</th><th>Transcript Event</th><th>Nearest Breath</th><th>Delta</th><th>Status</th></tr></thead>
      <tbody id="pairs"></tbody>
    </table>
  </section>
</main>
<script>
const data = {data};
const start = data.session_start_ms || Math.min(...data.force_rows.map(r => r.timestamp_ms), ...data.transcript_rows.map(r => r.timestamp_ms));
document.querySelector("#subtitle").textContent = `Session ${{data.session_id}}. Pairing CSV: ${{data.pairing_csv}}`;
document.querySelector("#forceCount").textContent = data.force_rows.length;
document.querySelector("#forceDuration").textContent = data.force_duration_s + "s";
document.querySelector("#transcriptCount").textContent = data.transcript_rows.length;
document.querySelector("#pairingResult").textContent = data.first_transcript_after_force_s === null ? "No data" : `Speech starts ${{data.first_transcript_after_force_s}}s after force ends`;

const c = document.querySelector("#chart");
const ctx = c.getContext("2d");
const allTimes = [...data.force_rows.map(r => rel(r.timestamp_ms)), ...data.transcript_rows.map(r => rel(r.timestamp_ms))];
const maxT = Math.max(2, ...allTimes);
const forces = data.force_rows.map(r => r.force_n).filter(Number.isFinite);
const minF = Math.min(...forces);
const maxF = Math.max(...forces);
function rel(ms) {{ return (ms - start) / 1000; }}
function x(t) {{ return 50 + (t / maxT) * (c.width - 80); }}
function y(v) {{ return 210 - ((v - minF) / Math.max(0.001, maxF - minF)) * 150; }}
ctx.clearRect(0,0,c.width,c.height);
ctx.strokeStyle = "#d8ded9"; ctx.lineWidth = 1;
for (let i=0; i<=5; i++) {{ const xx=x(maxT*i/5); ctx.beginPath(); ctx.moveTo(xx,20); ctx.lineTo(xx,220); ctx.stroke(); ctx.fillStyle="#66716c"; ctx.fillText((maxT*i/5).toFixed(1)+"s", xx-12, 240); }}
ctx.strokeStyle = "#217a57"; ctx.lineWidth = 4; ctx.beginPath();
data.force_rows.forEach((r,i) => {{ const xx=x(rel(r.timestamp_ms)); const yy=y(r.force_n); if(i===0) ctx.moveTo(xx,yy); else ctx.lineTo(xx,yy); }});
ctx.stroke();
data.transcript_rows.forEach((r, i) => {{ const xx=x(rel(r.timestamp_ms)); ctx.strokeStyle="#b64b47"; ctx.lineWidth=2; ctx.beginPath(); ctx.moveTo(xx,22); ctx.lineTo(xx,218); ctx.stroke(); ctx.fillStyle="#b64b47"; ctx.fillText("T"+(i+1), xx+3, 34 + (i%4)*16); }});

const tbody = document.querySelector("#pairs");
function nearest(ts) {{ if (!data.force_rows.length) return null; return data.force_rows.reduce((best,r) => Math.abs(r.timestamp_ms-ts) < Math.abs(best.timestamp_ms-ts) ? r : best, data.force_rows[0]); }}
data.transcript_rows.forEach((t, i) => {{
  const n = nearest(t.timestamp_ms);
  const delta = n ? t.timestamp_ms - n.timestamp_ms : null;
  const paired = delta !== null && Math.abs(delta) <= 500;
  const tr = document.createElement("tr");
  tr.innerHTML = `<td>${{rel(t.timestamp_ms).toFixed(3)}}s</td><td><strong>T${{i+1}}</strong>: ${{escapeHtml(t.text || "")}}</td><td>${{n ? rel(n.timestamp_ms).toFixed(3)+"s, "+Number(n.force_n).toFixed(3)+" N, <span class='phase'>"+n.breath_phase+"</span>" : ""}}</td><td>${{delta === null ? "" : delta+" ms"}}</td><td class="${{paired ? "yes" : "no"}}">${{paired ? "paired" : "no overlap"}}</td>`;
  tbody.appendChild(tr);
}});
function escapeHtml(s) {{ return s.replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c])); }}
</script>
</body>
</html>
"""


def timeline_row(
    session_start: int | None,
    timestamp_ms: object,
    row_type: str,
    value: object,
    **extra: object,
) -> dict[str, object]:
    timestamp = parse_int(timestamp_ms)
    relative = ""
    if session_start is not None and timestamp is not None:
        relative = round((timestamp - session_start) / 1000, 3)
    return {
        "timestamp_ms": timestamp if timestamp is not None else "",
        "relative_time_s": relative,
        "type": row_type,
        "value": value or "",
        "speaker": extra.get("speaker", ""),
        "force_n": extra.get("force_n", ""),
        "breath_phase": extra.get("breath_phase", ""),
        "confidence": extra.get("confidence", ""),
        "notes": extra.get("notes", ""),
        "source_file": extra.get("source_file", ""),
    }


def build_manifest(
    session_id: str,
    paths: SessionPaths,
    bundle_dir: Path,
    copied: dict[str, str],
    transcript_csv: str | None,
    merged_csv: str,
    pairing_csv: str,
    replay_html: str,
) -> dict[str, object]:
    markers = read_jsonl(paths.markers)
    transcripts = read_jsonl(paths.transcript)
    force_count = count_csv_rows(paths.force_csv)
    manifest: dict[str, object] = {
        "session_id": session_id,
        "bundle_dir": str(bundle_dir),
        "created_files": copied,
        "derived_files": {
            "transcript_csv": transcript_csv,
            "merged_timeline_csv": merged_csv,
            "breath_word_pairing_csv": pairing_csv,
            "kenny_replay_html": replay_html,
        },
        "counts": {
            "markers": len(markers),
            "transcript_events": len(transcripts),
            "vernier_force_samples": force_count,
        },
        "privacy": "Private local research capture. Do not commit or share without consent.",
        "next_step": "Open the merged timeline CSV first; use WAV, transcript JSONL, and force CSV for detailed review.",
    }
    if paths.session_manifest.exists():
        manifest["session_manifest"] = json.loads(paths.session_manifest.read_text(encoding="utf-8"))
    if paths.gambl_summary.exists():
        manifest["gambl_summary"] = json.loads(paths.gambl_summary.read_text(encoding="utf-8"))
    return manifest


def readme(session_id: str, manifest: dict[str, object]) -> str:
    counts = manifest["counts"]
    return f"""# Kenny Session Bundle: {session_id}

Start with `{session_id}.kenny_replay.html`, then open `{session_id}.merged_timeline.csv`. The replay shows whether Vernier force samples overlap the transcript events; the CSV puts session markers, transcript events, audio path, and Vernier force samples on one wall-clock timeline.

## Files

- `manifest.json`: bundle index and capture metadata.
- `{session_id}.merged_timeline.csv`: combined timeline for review.
- `{session_id}.breath_word_pairing.csv`: nearest breath sample for each transcript event.
- `{session_id}.kenny_replay.html`: local visual replay of force timing against transcript timing.
- `{session_id}.transcript.csv`: spreadsheet-friendly transcript, when speech events exist.
- `{session_id}.audio.wav`: local audio recording, when enabled.
- `{session_id}.vernier_force.csv`: Vernier force in Newtons with breath phase.
- `{session_id}.markers.jsonl`: session, Vernier start, and Vernier stop markers.

## Counts

- Markers: {counts["markers"]}
- Transcript events: {counts["transcript_events"]}
- Vernier force samples: {counts["vernier_force_samples"]}

Privacy: this bundle may contain real voice and biometric data. Keep it local unless everyone has agreed to share it.
"""


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def first_marker_ms(path: Path) -> int | None:
    for row in read_jsonl(path):
        if row.get("label") == "session_start":
            return parse_int(row.get("timestamp_ms"))
    return None


def first_event_ms(path: Path) -> int | None:
    for row in read_jsonl(path):
        timestamp = parse_int(row.get("timestamp_ms"))
        if timestamp is not None:
            return timestamp
    return None


def parse_int(value: object) -> int | None:
    try:
        if value is None or value == "":
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_float(value: object) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(newline="", encoding="utf-8") as src:
        return sum(1 for _ in csv.DictReader(src))


if __name__ == "__main__":
    raise SystemExit(main())
