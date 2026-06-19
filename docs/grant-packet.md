# Thinking Machines Interactivity Grant Packet

## Public Links

- GitHub: https://github.com/codewithx55/Physiological-Interactivity
- Local film demo: `python3 -m src.app --mode simulator --film`
- Local eval: `python3 tools/export_eval_report.py`
- Local video viewer: `python3 tools/build_demo_viewer.py`, then open `build/demo-viewer.html`

## Two-Sentence Demo Summary

This demo shows a real-time voice agent turn gate that uses breath phase and speech cadence to decide whether to listen, wait, respond, or ask a short clarifying question. The key filmed moment is a thinking inhale where baseline VAD would interrupt, while the physiology-aware gate waits until a cleaner exhale endpoint.

## Grant Fit

The project is interactivity research, not wellness or medical sensing. It asks whether physiological timing signals can improve collaborative AI behavior beyond transcript endpointing and audio silence.

## Evaluation Framework

Current benchmark:

- Synthetic, labeled turn-taking scenarios.
- Baseline policy: fixed silence/VAD threshold.
- Physiology policy: silence + WPM + breath phase + false starts + optional HR/EMG.
- Metrics: false interruptions, true end-of-turn latency, unnecessary wait time, clarifying-question hits, aggregate score.

Near-term eval expansion:

- Add scripted, consented single-speaker clips with hand-labeled turn boundaries.
- Align transcript tokens, VAD, respiration, and policy decisions on a common timeline.
- Compare baseline VAD, physiology-aware heuristics, and future model-based policies.
- Report failures as interaction timing errors, not medical states.

## Video Demo Plan

Film the browser at `http://127.0.0.1:8787/film.html`.

Shot list:

1. Show `SIMULATED VERNIER-SHAPED SIGNAL` label.
2. Press Play or scrub to 1760ms.
3. Hold on the key frame: `INHALE`, agent `WAITING`, baseline `RESPOND`, physiology `WAIT`.
4. Scrub to 3880ms: `EXHALE`, agent `RESPONDING`.
5. Narrate: "The model is not detecting emotion; it is using timing signals to avoid interrupting."

## Privacy Position

The public repo contains synthetic data only. Real recordings, transcripts, breath streams, HR, EMG, and sensor exports stay local until consent and retention rules are written.

## Next Milestone

Connect the Vernier Go Direct Respiration Belt through `godirect-py`, map raw samples into the existing mock stream shape, and rerun the same UI/eval with live respiration data.

## AI-Native Operating Mode

Frequency Labs should use agents as the default research and engineering loop:

- Agents maintain public demo code, private run notes, eval outputs, screenshots, and video artifacts.
- Every useful artifact should have a runnable command and a visible proof path.
- Subagents can split focused work: UI QA, hardware SDK scouting, eval design, and grant copy review.
- Generated demos stay local unless intentionally published; private recordings and biosignals never enter git.
