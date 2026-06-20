# Physiological Interactivity

Simulator-first research demo for physiology-aware voice AI turn-taking.

The core question: can breath phase and speech cadence help a real-time voice agent decide when to `WAIT`, `RESPOND`, or ask a tiny clarifying question instead of interrupting after a fixed silence threshold?

## Start Here

- High-signal benchmark writeup: [Synthetic overlap analysis](docs/synthetic-overlap-analysis.md)
- Synthetic fixture: [examples/synthetic_overlap_001.json](examples/synthetic_overlap_001.json)
- Reproducible analyzer: [tools/analyze_overlapping_breath_speech.py](tools/analyze_overlapping_breath_speech.py)

## What The Demo Shows

In the synthetic overlap fixture, baseline VAD responds after silence exceeds 650 ms. The physiology-aware policy also looks at breath phase, force trend, WPM/cadence, and false starts.

Result on 7 silent decision points:

| Metric | Baseline VAD | Physiology-aware |
| --- | ---: | ---: |
| False interruptions on continuation pauses | 3 | 0 |
| Correct endpoint responses | 2 / 2 | 2 / 2 |
| Clarify hits | 0 / 1 | 1 / 1 |
| Strict action accuracy | 3 / 7 | 7 / 7 |

The clean positioning: this is not emotion detection, health inference, or diagnosis. It uses physiological timing signals as interaction-control signals for real-time voice AI.

## Run It

```bash
python3 tools/smoke.py
python3 tools/analyze_overlapping_breath_speech.py
python3 -m src.app --mode simulator --film
```

Open:

```txt
http://127.0.0.1:8787/film.html
```

## Final Vernier + Voice Capture

Use this when Daley has Vernier Graphical Analysis open and wants timestamped audio, transcript, force, and markers.

```bash
python3 -m src.app \
  --mode simulator \
  --final-demo \
  --session-id daley_vernier_001 \
  --with-audio \
  --audio-device 0
```

Open:

```txt
http://127.0.0.1:8787/final-demo.html
```

Flow:

1. Click `Start Session`.
2. Start recording in Vernier Graphical Analysis.
3. Click `Mark Vernier Start`.
4. Speak normally while Graphical Analysis records the belt.
5. Click `Mark Vernier Stop`, then `Stop Session`.
6. Export the Vernier file as `.gambl`.
7. Align and bundle:

```bash
python3 tools/import_gambl.py /path/to/session.gambl \
  --session-id daley_vernier_001 \
  --markers data/daley_vernier_001.markers.jsonl

python3 tools/export_session_bundle.py --session-id daley_vernier_001
```

## Live Breath Screens

Minimal calibration screen:

```bash
python3 -m src.app --mode simulator --breath-screen --port 8787
```

Vernier-style force graph:

```bash
python3 -m src.app --mode simulator --vernier-breath --port 8788
```

Feed the Vernier Go Direct Respiration Belt:

```bash
bash tools/setup_vernier_env.sh
. .venv-vernier/bin/activate
python tools/vernier_stream.py --transport ble
```

Keep Vernier Graphical Analysis disconnected while Python owns BLE/USB.

## Privacy

Synthetic traces are safe to commit. Real audio, transcripts, breath streams, `.gambl` files, biometric exports, and session bundles stay local and ignored unless there is explicit consent and a retention plan.

## Project Notes

- Research plan: [docs/research-plan.md](docs/research-plan.md)
- Privacy notes: [docs/privacy.md](docs/privacy.md)
- Hardware strategy: [docs/hardware-signal-strategy.md](docs/hardware-signal-strategy.md)
- Vernier handoff: [docs/vernier-force-handoff.md](docs/vernier-force-handoff.md)
