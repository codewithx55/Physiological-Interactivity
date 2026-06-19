# Extracted Grant-Relevant Ideas: Physiology-Aware Turn-Taking for Real-Time AI

## Core Research Idea

Real-time voice AI systems still struggle with turn-taking. A major failure mode is deciding when the user is actually done speaking versus when they are pausing, breathing, searching for words, or preparing to continue.

Current systems often rely heavily on audio silence, VAD, or linguistic endpointing. This can cause two bad behaviors:

1. **False interruptions**: the AI responds while the human is still thinking or mid-turn.
2. **Excessive waiting**: the AI waits too long after the human has finished.

The proposed research direction is to explore whether additional human signals - especially respiration, heart rate, speech cadence, tone, and possibly EMG - can improve end-of-turn prediction in real-time interactive AI systems.

## Proposed Framing

**Physiology-Aware Turn-Taking for Real-Time Human-AI Interaction**

Alternative title:

**Human-State-Aware Endpointing for Real-Time Voice AI**

This project treats breath, voice cadence, and other biosignals as interaction signals, not as medical or diagnostic signals.

The key question:

> Can physiological and prosodic signals improve real-time AI turn-taking beyond audio silence and transcript-based endpointing?

## Why This Fits the Thinking Machines Lab Grant

The idea aligns with interactivity research because it focuses on making AI systems more fluid, responsive, and collaborative in real time.

Instead of treating interaction as a simple prompt-response loop, the project explores a richer model of human-AI interaction where the AI observes live signals and adapts its timing.

Relevant grant-aligned themes:

- Real-time interactivity
- Multimodal interaction
- Human-in-the-loop AI
- Better collaboration timing
- Open-ended research with measurable evaluation
- Simple reproducible experiments
- Potential use of interaction models
- Public GitHub demo and video-based benchmark

## Signals to Explore

### 1. Respiration / Breath

Breath may be highly informative for turn-taking.

Possible hypotheses:

- A user who inhales after a pause may be preparing to continue.
- A user who exhales at the end of a phrase may be more likely to yield the turn.
- Breath holds may indicate cognitive load or word search.
- Shallow or rapid breathing may correlate with rushed speech or overloaded interaction.

Primary hardware:

- Vernier Go Direct Respiration Belt

### 2. Speech Cadence / Words Per Minute

Speech rate may help distinguish between a completed thought and an unfinished thought.

Possible hypotheses:

- High WPM before a pause may indicate the user is still in the middle of a stream of thought.
- Sudden slowing may indicate the user is concluding.
- Repeated false starts may suggest the AI should wait or ask a short clarifying question.
- Personalized WPM baselines may improve prediction after the system learns the user's normal speaking rhythm.

### 3. Prosody / Tone

Prosodic cues may help identify whether a speaker is ending a turn.

Possible features:

- Pitch contour
- Falling intonation
- Rising intonation
- Volume decay
- Phrase-final lengthening
- Hesitation markers
- Filler words
- Pause shape

### 4. Heart Rate

Heart rate may provide weak but useful context about arousal or cognitive load.

Possible hypotheses:

- Elevated heart rate may suggest the user is under pressure or cognitively loaded.
- Heart-rate trends may help the model choose whether to respond immediately, wait, or simplify the next response.

This should be treated carefully and not framed as emotion detection.

### 5. EMG

EMG may provide an exploratory signal.

Possible directions:

- Jaw, throat, or facial muscle activation may indicate preparation to speak.
- Muscle tension may correlate with hesitation or readiness.
- EMG should remain optional and exploratory because the setup may be less reliable.

Hardware mentioned:

- Callibri / Calibri EMG sensor

## Proposed Benchmark

Build a small benchmark comparing:

1. **Baseline VAD endpointing**
2. **Physiology-aware endpointing**

The goal is not to solve turn-taking fully, but to show that breath/prosody/biometric signals can be evaluated as additional interaction signals.

## Data Collection Idea

Use recorded conversations or scripted voice interactions.

Important constraints:

- Only use consented recordings.
- Remove or avoid other speakers' private speech.
- Anonymize all data.
- Prefer synthetic or self-recorded data for public demos.
- Do not publish raw private calls.
- Use short, clean clips where the speaker's turn boundaries can be labeled.

A possible data pipeline:

1. Record single-speaker or consented two-speaker audio.
2. Label moments where the user is:
   - speaking
   - pausing but not done
   - done speaking
   - interrupted
3. Align labels with:
   - audio activity
   - transcript tokens
   - pause duration
   - breath phase
   - speech rate
   - optional heart-rate / EMG data
4. Compare endpointing policies.

## Evaluation Metrics

The evaluation should focus on interaction quality.

Suggested metrics:

### False Interruption Rate

How often does the AI respond before the user is done?

### End-of-Turn Latency

How long does the AI wait after the user is truly done?

### Unnecessary Wait Time

How much extra silence does the AI introduce?

### Turn-Taking F1 / Accuracy

How well does the model classify "done" vs "not done"?

### Human Preference

In a small user study or demo, compare whether users prefer baseline VAD or physiology-aware turn-taking.

## Demo Concept

Create a short video demo showing:

1. A user speaking to a real-time AI interface.
2. The user pauses mid-thought.
3. A baseline VAD system would respond too early.
4. The physiology-aware system observes breath/cadence and waits.
5. The user continues speaking.
6. The system responds only after a better end-of-turn signal.

The UI should visualize:

- Speech activity
- Transcript tokens
- Pause duration
- Breath phase
- End-of-turn probability
- Baseline decision
- Physiology-aware decision
- Final AI action: wait, respond, or ask a short clarifying question

## Hardware / SDK Plan

### Primary Sensor

**Vernier Go Direct Respiration Belt**

Purpose:

- Capture live breathing waveform
- Estimate inhale/exhale/hold phases
- Compute respiration rate
- Align breath phase with speech pauses

Development plan:

- Build simulator first
- Add adapter for Vernier Go Direct SDK / Graphical Analysis sensor detection flow
- Output normalized breath stream into the same interface as simulated data

### Secondary Sensor

**Callibri / Calibri EMG Sensor**

Purpose:

- Explore optional EMG signals related to speech preparation, tension, or physiological state
- Keep optional for the first grant demo

### Optional Sensor

**Heart-rate strap**

Purpose:

- Capture HR / HRV-like trend signals
- Treat as contextual signal, not a primary endpointing feature

## MVP Software Plan

Build a simple open-source GitHub repo.

Suggested modules:

```txt
src/
  app.py
  sensors/
    simulator.py
    vernier_respiration.py
    callibri_emg.py
    heart_rate_ble.py
  audio/
    vad.py
    prosody.py
    transcript_events.py
  features/
    breath_features.py
    speech_features.py
    physiology_features.py
  turn_taking/
    baseline_vad_policy.py
    physiology_aware_policy.py
    evaluator.py
  ui/
    dashboard.py
```

## Policy Logic

### Baseline

Respond after silence exceeds a fixed threshold.

Example:

```txt
if silence_ms > 700:
    respond
```

### Physiology-Aware

Respond based on a richer estimate.

Example signals:

```txt
silence duration
recent WPM
breath phase
pause pattern
prosody
optional HR
optional EMG
```

Example rules:

- If silence is short and user just inhaled: wait.
- If silence follows fast speech: wait longer.
- If silence follows falling cadence and exhale: respond.
- If user appears to be searching for words: ask a short clarifying question.
- If user has repeated pauses but keeps inhaling to continue: do not interrupt.

## Open-Source Positioning

The public repo should emphasize:

- Research demo
- Open-source implementation
- Reproducible simulator
- Clear benchmark
- Hardware adapters optional
- No medical claims
- No hidden recording
- No emotion surveillance
- No diagnosis
- No claim of sponsorship or endorsement

## Public GitHub README One-Liner

> This repo explores whether respiration, speech cadence, and optional physiological signals can improve end-of-turn detection for real-time voice AI systems.

## Research Contribution

The contribution is not a new sensor or a production voice assistant.

The contribution is a testable interaction hypothesis:

> Real-time AI systems can make better turn-taking decisions when they model human physiological timing in addition to speech silence and language.

## One-Month Pilot Plan

### Week 1: Simulator + Baseline

- Build simulator
- Implement baseline VAD endpointing
- Create first dashboard
- Define labels and metrics

### Week 2: Respiration Integration

- Connect Vernier Go Direct Respiration Belt if possible
- Extract breath phase and respiration rate
- Align breath data with speech pauses

### Week 3: Physiology-Aware Policy

- Implement heuristic policy
- Compare against baseline
- Add example scenarios and evaluation

### Week 4: Demo + Writeup

- Record short demo video
- Publish GitHub repo
- Write technical summary
- Document limitations and next steps

## Longer-Term Research Directions

- Personalized turn-taking models
- Learning user-specific speaking cadence
- Breath-aware response timing
- Multimodal endpointing with audio + respiration + text
- Real-time adaptive AI interfaces
- Better interruption behavior in voice agents
- Extension to coaching, education, high-performance work, or embodied AI systems

## Material to Exclude From Public Repo

Do not include:

- Private call transcripts
- Names of private individuals
- Employment details
- Drug or mental health references
- Personal relationship details
- Private company speculation
- Legal speculation
- Financial speculation
- Non-consented audio
- Claims about private access to unreleased models
- Any content that implies endorsement from Thinking Machines Lab
