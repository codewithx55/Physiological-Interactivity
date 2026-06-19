# Hardware and Signal Strategy

## Current Hardware Status

On this Mac, no Vernier, Callibri/Calibri, BrainBit, or heart-rate device is currently visible over USB or Bluetooth. The repo includes mock Vernier-shaped data so the grant demo remains filmable without live hardware.

Run:

```bash
python3 tools/check_hardware.py
python3 tools/check_vernier.py
```

## Recommended Signal Stack

Use multiple signals in the grant framing, but make respiration the first live integration.

1. **Respiration / breath phase**: primary signal for turn timing.
   - Why: inhale/exhale/hold maps directly to "still thinking" vs "yielding the floor."
   - Hardware: Vernier Go Direct Respiration Belt.
   - Integration target: `breath_signal`, `breath_phase`, `breath_rate_bpm`.

2. **Speech cadence / prosody**: primary non-hardware signal.
   - Why: high WPM and false starts help explain why silence is not enough.
   - Integration target: WPM, pause shape, falling/rising cadence, filler markers.

3. **Heart rate / ECG**: secondary context signal.
   - Why: useful for "slow down / simplify / ask a short question" decisions.
   - Caution: do not frame as emotion detection.

4. **EMG / muscle tension**: exploratory signal.
   - Why: jaw/throat/chest muscle activation may indicate preparation to speak or cognitive load.
   - Caution: electrode placement and signal quality may be fragile for tonight.

## Vernier

Vernier's Go Direct Python path is `godirect-py`, which can read Go Direct sensors over USB or BLE on macOS. The Go Direct Respiration Belt is designed to measure respiration effort and respiration rate around the chest.

Links:

- https://vernierst.github.io/godirect-examples/python/
- https://github.com/VernierST/godirect-py
- https://www.vernier.com/video/measure-respiration-rate-using-go-directrespiration-belt/

## Callibri / Calibri

Callibri appears to be the multimodal route: ECG, EMG, GSR, respiration, and motion are advertised through Bluetooth streaming and an SDK. It may support heart-rate-style signals through ECG with compatible electrodes/accessories, and EMG for muscle tension.

For this grant, Callibri is useful in the story as the "multi-signal future path," but Vernier breath is the cleaner first live demo because breath phase is the most legible interaction signal.

Links:

- https://callibri.com/specification
- https://brainbit.com/hardware-solutions/callibri-sensors/

## Grant Position

Apply with the multi-signal ambition:

```txt
voice/prosody + respiration + optional ECG/HR + optional EMG
  -> turn readiness
  -> wait / respond / ask short clarifying question
```

But film the demo around one crisp wedge:

```txt
thinking inhale: baseline interrupts, physiology-aware agent waits
```
