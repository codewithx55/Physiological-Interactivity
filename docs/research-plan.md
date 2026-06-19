# Research Plan

This repo explores whether respiration, speech cadence, and optional physiological signals can improve end-of-turn detection for real-time voice AI systems.

## Benchmark

Compare two policies:

- Baseline VAD endpointing: respond after silence exceeds a fixed threshold.
- Physiology-aware endpointing: estimate turn readiness from silence, WPM, breath phase, pause pattern, prosody, optional HR, and optional EMG.

Current metrics:

- False interruption rate
- End-of-turn latency
- Unnecessary wait time
- Clarifying-question hits
- Simple aggregate score

## Interaction Hypotheses

- Inhale after a pause often means the user is preparing to continue.
- Exhale at the end of a phrase often means the user may be yielding the turn.
- Breath hold can indicate word search or cognitive load.
- High WPM before a pause can mean the user is still mid-stream.
- Falling cadence plus exhale is a stronger endpoint than silence alone.
- Repeated false starts should trigger waiting or a short clarifying question, not a long answer.

## One-Month Pilot

Week 1: simulator, baseline VAD, dashboard, labels, and metrics.

Week 2: Vernier Go Direct Respiration Belt integration if the SDK/BLE path is available.

Week 3: physiology-aware heuristic policy, scenario expansion, and baseline comparison.

Week 4: short demo video, public GitHub polish, technical summary, limitations, and next steps.

## Hardware Path

Primary sensor: Vernier Go Direct Respiration Belt.

Optional sensors:

- Callibri / Calibri EMG for exploratory muscle-tension or speech-preparation signals.
- BLE heart-rate strap for weak context about arousal or load.

The hardware adapters must emit the same shape as the simulator so the dashboard and evaluator keep working without live devices.

## Public Positioning

This is a research demo and reproducible benchmark. It is not a production assistant, medical device, diagnosis system, emotion detector, or claim of Thinking Machines sponsorship.
