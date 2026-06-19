# Privacy Notes

This repo is designed to be public-safe by default.

## Current Data

The current simulator data is synthetic. It includes invented speech tokens, breath phase, respiration rate, heart-rate values, EMG tension values, and ground-truth turn labels.

## Data We Should Treat As Sensitive

- Raw audio or video
- Transcripts from real people
- Breath belt streams
- Heart-rate streams
- EMG streams
- Device identifiers and BLE logs
- Personal notes, grant admin details, or private screenshots

## Working Rule

Real capture data stays local and ignored until there is a written consent and retention plan.

Recommended local-only paths:

```txt
data/
captures/
recordings/
transcripts/
sensor_exports/
```

These paths are ignored by `.gitignore`.

## Live Hardware Checklist

Before adding live Vernier, Callibri, or heart-rate data:

1. Label the UI as live or synthetic.
2. Add a visible recording/capture state.
3. Add a stop button or clear shutdown command.
4. Keep raw streams out of git.
5. Store only the minimum sample needed for debugging.
6. Document retention before collecting human data.
