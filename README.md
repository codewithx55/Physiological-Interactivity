# Hi Kenny

🫀 Frequency demo handoff.

## Hardware

- Vernier Go Direct Respiration Belt
- Optional later: Callibri/Calibri EMG sensor
- Optional later: BLE heart-rate strap

## SDK Links

- Vernier Go Direct Python guide: https://vernierst.github.io/godirect-examples/python/
- Vernier `godirect-py`: https://github.com/VernierST/godirect-py
- Hardware sanity check: `python3 tools/check_vernier.py`

## What Already Exists

I built a simulator-first Python demo for physiology-aware turn-taking in real-time voice AI. It compares baseline VAD against a breath/cadence-aware policy so we can show the assistant waiting during a thinking inhale instead of interrupting.

Run it:

```bash
python3 tools/smoke.py
python3 -m src.app --mode simulator --film
```

Then open:

```txt
http://127.0.0.1:8787/dashboard.html
```

For the film UI, open:

```txt
http://127.0.0.1:8787/film.html
```

## How I Think You Should Move Forward

Connect the Vernier belt through `godirect-py`, make it emit the same fields as `src/sensors/simulator.py`, and keep all real recordings/transcripts/sensor exports local and ignored.

More context: [privacy](docs/privacy.md), [research plan](docs/research-plan.md), [grant notes](docs/grant-relevant-ideas.md).
