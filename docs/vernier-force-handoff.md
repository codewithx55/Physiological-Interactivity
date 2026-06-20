# Vernier Force Handoff

## Current State

This project now supports two Vernier Go Direct Respiration Belt paths:

- Live SDK stream: reads the Go Direct `Force` channel in Newtons and writes the latest local state to `build/vernier-live.json`.
- Saved Graphical Analysis import: reads `.gambl` files, extracts timestamped `Time (s)` and `Force (N)` samples, and writes local event/CSV outputs.

The Kenny-facing page is `vernier.html`. It clones the Vernier Graphical Analysis force view closely enough for demos and uses the same breath rule everywhere: force rising means `inhale`; force falling means `exhale`.

## What Works

- The actual belt was visible as `GDX-RB 0K7012Z9`.
- The local Vernier Python environment imports `godirect`.
- The SDK opened the belt over BLE and reported channels:
  - `1: Force (N)`
  - `2: Respiration Rate (bpm)`
  - `4: Steps`
  - `5: Step Rate (spm)`
- The live stream uses channel `1` only.
- The live JSON includes `recent_samples`, so the browser can draw a force trace immediately instead of a single point.
- The `.gambl` importer parsed `vernierp1test.gambl` and produced 3,001 timestamped samples over 300 seconds.

## Important Files

- `tools/vernier_stream.py`: live Go Direct BLE/USB force stream.
- `tools/import_gambl.py`: saved `.gambl` to timestamped event/CSV importer.
- `src/ui/vernier_breath_dashboard.py`: force-only Vernier-style page.
- `src/app.py`: app flag for rendering `vernier.html`.
- `README.md`: short runnable workflow.

## Privacy

Real Vernier captures are private biometric data. `.gambl`, generated data files, CSVs, JSONL, screenshots, audio, and build outputs are ignored by git.

## Next-Thread Prompt

Continue the Vernier Go Direct force/breath work in `/Users/codex/Documents/Physiological-Interactivity`. The current branch is `codex/breath-calibration-stream`. The goal is to align force-derived inhale/exhale with spoken words. Use the live SDK force stream when the belt is connected, and use `.gambl` imports when Daley records in Vernier Graphical Analysis. Do not use respiration rate unless it becomes clearly useful. The core rule is force rising = inhale, force falling = exhale. Start by reviewing `docs/vernier-force-handoff.md`, `tools/vernier_stream.py`, `tools/import_gambl.py`, and `src/ui/vernier_breath_dashboard.py`.
