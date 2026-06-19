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
- Private call notes, relationship details, health/drug references, legal/financial speculation, or private company speculation
- Claims that imply sponsorship, endorsement, or private access from Thinking Machines Lab

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

## Public Repo Rule

The public repo should include synthetic examples, aggregate metrics, code, and docs. It should not include private names beyond explicit collaborators, non-consented speech, raw recordings, or claims that the demo is medically meaningful.

Sanitized, grant-relevant notes can be committed when they remove private personal details and are clearly used as research framing. Raw call transcripts stay ignored.

## Live Hardware Checklist

Before adding live Vernier, Callibri, or heart-rate data:

1. Label the UI as live or synthetic.
2. Add a visible recording/capture state.
3. Add a stop button or clear shutdown command.
4. Keep raw streams out of git.
5. Store only the minimum sample needed for debugging.
6. Document retention before collecting human data.
