# Hi Kenny

This repo is the tiny demo for Frequency Labs' Thinking Machines grant idea:

**Can a real-time voice assistant use breath, pause shape, speech cadence, and optional biosignals to avoid interrupting people at the wrong time?**

It is not a medical app, wellness app, emotion detector, or hidden recording system. Everything runs locally with synthetic data unless we explicitly connect hardware later.

## What You Can Run

```bash
python3 tools/smoke.py
python3 -m src.app --mode simulator
```

Then open:

```txt
http://127.0.0.1:8787/dashboard.html
```

## What The Demo Shows

- Baseline VAD responds after silence.
- Physiology-aware policy also looks at inhale/exhale/hold, WPM, false starts, optional HR, and optional EMG.
- In the key scenario, the user pauses and inhales because they are still thinking. Baseline responds too early. The physiology-aware policy waits.
- In a long searching pause, the policy asks a short clarifying question instead of dumping a full answer.

## Why This Matters

The grant framing is not "breath detection." It is a real-time interaction control layer for voice agents:

```txt
listen / wait / respond / ask a short clarifying question
```

The research question is whether physiological and prosodic cues improve turn timing in collaborative spoken AI.

## Privacy Defaults

- Commit only synthetic fixtures and aggregate results.
- Do not commit raw audio, transcripts from real people, biometric streams, sensor exports, `.env` files, API keys, or screenshots containing private data.
- Live hardware adapters should stay mockable and opt-in.
- If real Kenny/Daley/human data is collected later, keep it in ignored local folders and document consent + retention first.

See [docs/privacy.md](docs/privacy.md).

## Current Shape

```txt
src/sensors/simulator.py
  synthetic speech + breath + optional HR/EMG timelines

src/features/
  converts timeline events into turn-taking features

src/turn_taking/
  baseline VAD policy, physiology-aware policy, evaluator

src/ui/dashboard.py
  static local HTML dashboard
```

## Hardware Later

First target: Vernier Go Direct Respiration Belt.

The live adapter boundary is already here:

```txt
src/sensors/vernier_respiration.py
```

For now, `--mode vernier` intentionally exits with a clear message so the demo never depends on hardware being present.
