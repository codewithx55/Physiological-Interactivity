# Hi Kenny

🫀 Frequency demo handoff.

Kenny direct data bundle: [exports/daley_vernier_001/README.md](exports/daley_vernier_001/README.md) and [exports/daley_vernier_001/daley_vernier_001.kenny_replay.html](exports/daley_vernier_001/daley_vernier_001.kenny_replay.html).

## Final Vernier + Voice Demo

Use this when Daley has Vernier Graphical Analysis open and wants a clean Kenny handoff with audio, transcript, force, and timestamps.

```bash
cd /Users/codex/Documents/Physiological-Interactivity
python3 -m pip install -r requirements.txt
python3 -m src.app \
  --mode simulator \
  --final-demo \
  --session-id daley_vernier_001 \
  --with-audio \
  --audio-device 0
```

Open:

```txt
http://127.0.0.1:8787/final-demo.html
```

Demo flow:

1. Click `Start Session` on the web page.
2. Start recording in Vernier Graphical Analysis.
3. Click `Mark Vernier Start`.
4. Speak normally while Graphical Analysis records the belt.
5. Click `Mark Vernier Stop`, then `Stop Session`.
6. Export the Vernier file from Graphical Analysis as `.gambl`.

Then align and bundle:

```bash
python3 tools/import_gambl.py /path/to/session.gambl \
  --session-id daley_vernier_001 \
  --markers data/daley_vernier_001.markers.jsonl

python3 tools/export_session_bundle.py --session-id daley_vernier_001
```

Kenny starts with:

```txt
exports/daley_vernier_001/README.md
exports/daley_vernier_001/manifest.json
exports/daley_vernier_001/daley_vernier_001.merged_timeline.csv
```

Local private outputs:

```txt
data/daley_vernier_001.audio.wav
data/daley_vernier_001.transcript.jsonl
data/daley_vernier_001.markers.jsonl
data/daley_vernier_001.vernier_force.csv
exports/daley_vernier_001/
```

All rows are timestamped. Vernier force uses the same rule everywhere: force rising means `inhale`; force falling means `exhale`.

## Kenny Live Data Stream

Fastest local stream for Kenny:

```bash
cd /Users/codex/Documents/Physiological-Interactivity
python3 -m pip install -r requirements.txt
python3 -m src.main \
  --device callibri \
  --session-id daley_kenny_calibri_001 \
  --host 0.0.0.0 \
  --port 8765 \
  --with-audio \
  --audio-device 0 \
  --transcript-note "Calibri on lower sternum/upper abdomen; Hollyland mic connected; labeling inhale/exhale test."
```

If the Callibri SDK is not installed, the command falls back to mock breath data so Kenny can still connect immediately. The mock `respiration_force` is a smooth inhale/exhale wave.

List mic devices if the Hollyland is not device `0`:

```bash
python3 - <<'PY'
import sounddevice as sd
print(sd.query_devices())
PY
```

Kenny connects to:

```txt
ws://<Daley laptop IP>:8765
```

Minimal local inhale/exhale screen:

```bash
python3 -m src.app --mode simulator --breath-screen --port 8787
```

Open:

```txt
http://127.0.0.1:8787/breath.html
```

Kenny Vernier-style inhale/exhale graph screen:

```bash
python3 -m src.app --mode simulator --vernier-breath --port 8788
```

Open:

```txt
http://127.0.0.1:8788/vernier.html
```

This is a new page, separate from `breath.html`. It clones the Vernier Graphical Analysis layout around the Go Direct Force signal in Newtons. Inhale/exhale is derived from slope: force going up means inhale, force going down means exhale. If no live Vernier stream is available, it uses a Vernier-shaped force trace so Kenny can still see the full behavior.

To feed the page from the Vernier Go Direct Respiration Belt:

```bash
bash tools/setup_vernier_env.sh
. .venv-vernier/bin/activate
python tools/vernier_stream.py --transport ble
```

Keep Vernier Graphical Analysis disconnected while Python owns BLE/USB. The page reads only the latest local force state from `build/vernier-live.json`; it does not save raw breath recordings.

Import a saved Vernier Graphical Analysis `.gambl` file:

```bash
python3 tools/import_gambl.py vernierp1test.gambl --session-id vernierp1test
```

The importer reads the `.gambl` bundle, extracts the Graphical Analysis Time and Force columns, and writes timestamped local files:

```txt
data/vernierp1test.events.jsonl
data/vernierp1test.vernier_force.csv
data/vernierp1test.gambl-summary.json
```

Each force event has `timestamp_ms`, `relative_time_s`, `value` in Newtons, and `breath_phase`. Those timestamps can be aligned with transcript events from the same session. `.gambl` files are treated as private biometric captures and ignored by git.

Two-step calibration flow on `breath.html`:

1. Click `Start calibration`.
2. For 30 seconds, press `I` while actually inhaling and `E` while actually exhaling.

Then analyze the run:

```bash
python3 tools/analyze_breath_calibration.py --session-id daley_kenny_calibri_001
python3 tools/train_breath_model.py --session-id daley_kenny_calibri_001
```

The trained model is written to:

```txt
build/breath-model.json
```

After a model exists, the page opens directly into live inhale/exhale mode and shows model confidence in the bottom-left status.

Calibration controls:

- Press `I` while actually inhaling.
- Press `E` while actually exhaling.
- Press `F` if the display is consistently inverted.

Labels are timestamped here and also appended into the main event stream:

```txt
data/daley_kenny_calibri_001.breath_labels.jsonl
data/daley_kenny_calibri_001.events.jsonl
```

Get the laptop IP:

```bash
ipconfig getifaddr en0
```

Outputs are local and ignored by git:

```txt
data/daley_kenny_calibri_001.events.jsonl
data/daley_kenny_calibri_001.biometrics.csv
data/daley_kenny_calibri_001.transcript.jsonl
data/daley_kenny_calibri_001.audio.wav
```

Event shape:

```json
{"type":"biometric","session_id":"daley_kenny_calibri_001","device":"mock","timestamp_ms":1781929425580,"signal":"respiration_force","value":0.57,"unit":"arbitrary","quality":0.92}
```

Browser client:

```js
const ws = new WebSocket("ws://<Daley laptop IP>:8765");
ws.onmessage = (msg) => console.log(JSON.parse(msg.data));
```

Check whether macOS sees the Callibri:

```bash
system_profiler SPBluetoothDataType | grep -i -A 8 -B 4 "callibri\\|calibri\\|brainbit\\|neuro"
```

Current Callibri integration point:

```txt
src/sensors/callibri_sensor.py
```

## Hardware

- Vernier Go Direct Respiration Belt
- Optional later: Callibri/Calibri EMG sensor
- Optional later: BLE heart-rate strap

## SDK Links

- Vernier Go Direct Python guide: https://vernierst.github.io/godirect-examples/python/
- Vernier `godirect-py`: https://github.com/VernierST/godirect-py
- Hardware sanity check after setup: `python tools/check_hardware.py`

## Connect The Vernier

Current status on this Mac: `godirect` works in `.venv-vernier`, but the Vernier is not visible over USB/Bluetooth yet.

Start with USB before Bluetooth:

```bash
cd /Users/codex/Documents/Physiological-Interactivity
bash tools/setup_vernier_env.sh
. .venv-vernier/bin/activate
python tools/check_hardware.py
```

Why the setup script exists: Apple's built-in Python 3.9 can accidentally try to build PyObjC 12, which currently fails on this Mac. The local Vernier environment pins PyObjC below 12 and installs cleanly.

Physical setup:

1. Charge or power on the Vernier Go Direct Respiration Belt.
2. Connect it to the Mac with a USB cable first.
3. Run `python tools/check_hardware.py`.
4. If the Mac sees it, run `python tools/check_vernier.py`.
5. Only after USB works, try Bluetooth pairing from macOS Bluetooth settings or Vernier's Graphical Analysis app.

The repo does not record real breath data yet. The live adapter boundary is `src/sensors/vernier_respiration.py`; the current demo still uses synthetic/mock traces.

## Live Voice + Breath MVP

The smallest useful next demo is a local browser page that shows live browser speech-to-text beside a breath phase gate.

Run the page:

```bash
python3 -m src.app --mode simulator --live-voice
```

Open:

```txt
http://127.0.0.1:8787/live-voice.html
```

By default it uses simulated breath. To try the Vernier as the breath source, first disconnect Graphical Analysis from the sensor, then run this in a second terminal:

```bash
cd /Users/codex/Documents/Physiological-Interactivity
. .venv-vernier/bin/activate
python tools/vernier_stream.py --transport ble
```

The stream writes only the latest derived state to `build/vernier-live.json`; it does not save raw recordings.

Strap placement: wear it over a shirt if that is more comfortable. Direct skin is not required. Start with the sensor box just below the sternum or high upper abdomen, tighten until the tension indicator is green, and avoid making it tight enough to restrict breathing.

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

More context: [grant packet](docs/grant-packet.md), [hardware strategy](docs/hardware-signal-strategy.md), [privacy](docs/privacy.md), [research plan](docs/research-plan.md), [grant notes](docs/grant-relevant-ideas.md).
