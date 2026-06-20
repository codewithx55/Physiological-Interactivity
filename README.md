# Physiological Interactivity

Research demo for voice AI that uses breath timing and speech cadence to avoid bad interruptions.

## Key Result

[Synthetic overlap analysis](docs/synthetic-overlap-analysis.md)

On 7 labeled silent pauses, a silence-only baseline made 3 false interruptions. The physiology-aware policy made 0, while still catching both true endpoints and the one clarifying-question moment.

| Metric | Baseline VAD | Physiology-aware |
| --- | ---: | ---: |
| False interruptions | 3 | 0 |
| Endpoint hits | 2 / 2 | 2 / 2 |
| Clarify hits | 0 / 1 | 1 / 1 |
| Accuracy | 3 / 7 | 7 / 7 |

The claim is simple: this is not emotion or health detection. It uses physiological timing as an interaction-control signal for real-time voice AI.

## Run

```bash
python3 tools/analyze_overlapping_breath_speech.py
python3 tools/smoke.py
python3 -m src.app --mode simulator --film
```

Open:

```txt
http://127.0.0.1:8787/film.html
```
