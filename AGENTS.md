# Agent Guide

Build the smallest runnable demo that helps Kenny and Daley reason about physiology-aware voice interaction.

## Priorities

- Keep the README short and Kenny-readable.
- Simulator first; never block on hardware SDKs.
- Treat real voice, breath, HR, EMG, transcripts, and sensor exports as private by default.
- Commit synthetic traces only.
- Keep commands local and reproducible.
- Update docs when run commands, privacy posture, or adapter boundaries change.

## Verification

```bash
python3 tools/smoke.py
python3 -m src.turn_taking.evaluator
python3 -m src.app --mode simulator --once
```

## Do Not Commit

- Raw audio/video
- Real transcripts
- Biometric streams or exports
- Sensor vendor exports
- `.env*` secrets
- Local dashboard builds unless explicitly needed as an artifact
- Python caches, venvs, node modules, or model files
