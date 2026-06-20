"""Render a minimal inhale/exhale screen driven by the biometric WebSocket."""

from __future__ import annotations

from pathlib import Path


def render_breath_phase_screen(output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Breath Phase</title>
  <style>
    :root { color-scheme: dark; font-family: Arial, Helvetica, sans-serif; }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: #111;
      color: white;
      transition: background 180ms linear;
      overflow: hidden;
    }
    body.inhale { background: #126b5a; }
    body.exhale { background: #7a2634; }
    body.hold { background: #30343b; }
    main {
      width: min(92vw, 900px);
      text-align: center;
    }
    #phase {
      margin: 0;
      font-size: clamp(64px, 18vw, 180px);
      line-height: 0.9;
      letter-spacing: 0;
      font-weight: 900;
    }
    #value {
      margin-top: 28px;
      font-size: clamp(22px, 5vw, 42px);
      opacity: 0.88;
    }
    #status {
      position: fixed;
      left: 18px;
      bottom: 16px;
      font-size: 15px;
      opacity: 0.75;
    }
    #controls {
      position: fixed;
      right: 18px;
      bottom: 16px;
      display: flex;
      gap: 8px;
      align-items: center;
      font-size: 15px;
      opacity: 0.86;
    }
    button {
      border: 1px solid rgba(255,255,255,0.38);
      background: rgba(0,0,0,0.22);
      color: white;
      padding: 9px 11px;
      border-radius: 6px;
      font: inherit;
      cursor: pointer;
    }
    button:active { transform: translateY(1px); }
    #startBtn {
      margin-top: 34px;
      padding: 14px 18px;
      font-size: 20px;
    }
    #timer {
      margin-top: 18px;
      font-size: clamp(20px, 4vw, 34px);
      opacity: 0.9;
    }
    body.idle #controls, body.live #controls { display: none; }
    body.calibrating #startBtn { display: none; }
    body.done #startBtn { display: none; }
  </style>
</head>
<body class="idle hold">
  <main>
    <h1 id="phase">START CALIBRATION</h1>
    <div id="value">press start, then tap I while inhaling and E while exhaling</div>
    <button id="startBtn">Start calibration</button>
    <div id="timer">30 seconds</div>
  </main>
  <div id="status">connecting</div>
  <div id="controls">
    <button id="inhaleBtn">I Inhale</button>
    <button id="exhaleBtn">E Exhale</button>
    <button id="flipBtn">F Flip</button>
  </div>
  <script>
    const phaseEl = document.getElementById("phase");
    const valueEl = document.getElementById("value");
    const statusEl = document.getElementById("status");
    const startBtn = document.getElementById("startBtn");
    const timerEl = document.getElementById("timer");
    const inhaleBtn = document.getElementById("inhaleBtn");
    const exhaleBtn = document.getElementById("exhaleBtn");
    const flipBtn = document.getElementById("flipBtn");
    const samples = [];
    const wsHosts = ["127.0.0.1", "localhost", window.location.hostname].filter((v, i, a) => v && a.indexOf(v) === i);
    let wsIndex = 0;
    let lastEventMs = 0;
    let lastPhase = "hold";
    let lastValue = NaN;
    let inverted = window.localStorage.getItem("breath_phase_inverted") === "true";
    let model = { method: "slope_sign", window_ms: 900, polarity: 1, confidence: "untrained" };
    let mode = "idle";
    let calibrationEndsAt = 0;
    let labelCount = 0;

    function setPhase(phase, value) {
      document.body.className = mode + " " + phase;
      if (mode === "idle") return;
      phaseEl.textContent = phase.toUpperCase();
      valueEl.textContent = Number.isFinite(value) ? value.toFixed(3) : "waiting";
    }

    function classify(value) {
      samples.push({ t: performance.now(), value });
      const cutoff = performance.now() - Math.max(300, model.window_ms || 900);
      while (samples.length > 2 && samples[0].t < cutoff) samples.shift();
      if (samples.length < 3) return lastPhase;
      const first = samples[0].value;
      const last = samples[samples.length - 1].value;
      const polarity = inverted ? -1 : Number(model.polarity || 1);
      const slope = (last - first) * polarity;
      if (slope > 0.16) lastPhase = "inhale";
      else if (slope < -0.16) lastPhase = "exhale";
      return lastPhase;
    }

    function handleEvent(event, source) {
      if (event.type !== "biometric" || event.signal !== "respiration_force") return;
      const value = Number(event.value);
      lastValue = value;
      lastEventMs = Date.now();
      statusEl.textContent = source + " | " + event.device + " | " + event.timestamp_ms + " | model " + model.confidence;
      setPhase(classify(value), value);
    }

    async function loadModel() {
      try {
        const response = await fetch("breath-model.json?ts=" + Date.now(), { cache: "no-store" });
        if (response.ok) {
          model = await response.json();
          if (mode === "idle" && model.trained_at_ms) {
            mode = "live";
            startBtn.textContent = "Recalibrate";
            timerEl.textContent = "model " + model.confidence;
          }
        }
      } catch (error) {}
    }

    async function saveLabel(label, countTrainingLabel) {
      const payload = {
        session_id: "daley_kenny_calibri_001",
        label,
        display_phase: lastPhase,
        signal_value: Number.isFinite(lastValue) ? lastValue : null
      };
      try {
        const response = await fetch("/label", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (response.ok) {
          if (countTrainingLabel) labelCount += 1;
          statusEl.textContent = "saved " + label + " | labels " + labelCount;
        } else {
          statusEl.textContent = "label save failed";
        }
      } catch (error) {
        statusEl.textContent = "label save failed";
      }
    }

    async function labelBreath(label) {
      if (mode !== "calibrating") return;
      await saveLabel(label, label === "inhale" || label === "exhale");
    }

    function flipPhase() {
      inverted = !inverted;
      window.localStorage.setItem("breath_phase_inverted", inverted ? "true" : "false");
      samples.length = 0;
      lastPhase = "hold";
      statusEl.textContent = inverted ? "phase flipped" : "phase normal";
    }

    function startCalibration() {
      mode = "calibrating";
      labelCount = 0;
      samples.length = 0;
      calibrationEndsAt = Date.now() + 30000;
      phaseEl.textContent = "CALIBRATING";
      valueEl.textContent = "tap I on inhale, E on exhale";
      timerEl.textContent = "30 seconds";
      document.body.className = "calibrating hold";
      saveLabel("calibration_start", false);
    }

    function finishCalibration() {
      if (mode !== "calibrating") return;
      saveLabel("calibration_end", false);
      mode = "done";
      phaseEl.textContent = "CALIBRATION DONE";
      valueEl.textContent = "labels saved: " + labelCount;
      timerEl.textContent = "ready to analyze";
      document.body.className = "done hold";
      labelBreath("calibration_end");
    }

    function updateTimer() {
      if (mode !== "calibrating") return;
      const remainingMs = calibrationEndsAt - Date.now();
      if (remainingMs <= 0) {
        finishCalibration();
        return;
      }
      timerEl.textContent = Math.ceil(remainingMs / 1000) + " seconds";
    }

    function connect() {
      const host = wsHosts[wsIndex % wsHosts.length];
      wsIndex += 1;
      const ws = new WebSocket("ws://" + host + ":8765");
      statusEl.textContent = "connecting ws://" + host + ":8765";
      ws.onclose = () => {
        statusEl.textContent = "disconnected, retrying";
        setTimeout(connect, 700);
      };
      ws.onerror = () => { statusEl.textContent = "socket error"; };
      ws.onmessage = (msg) => {
        handleEvent(JSON.parse(msg.data), "websocket");
      };
    }

    async function pollLatest() {
      if (Date.now() - lastEventMs < 1200) return;
      try {
        const response = await fetch("breath-latest.json?ts=" + Date.now(), { cache: "no-store" });
        if (!response.ok) return;
        handleEvent(await response.json(), "file");
      } catch (error) {
        if (!lastEventMs) statusEl.textContent = "waiting for stream";
      }
    }

    loadModel();
    setInterval(loadModel, 5000);
    connect();
    setInterval(pollLatest, 350);
    setInterval(updateTimer, 250);
    startBtn.onclick = startCalibration;
    inhaleBtn.onclick = () => labelBreath("inhale");
    exhaleBtn.onclick = () => labelBreath("exhale");
    flipBtn.onclick = flipPhase;
    window.addEventListener("keydown", (event) => {
      if (event.key.toLowerCase() === "i") labelBreath("inhale");
      if (event.key.toLowerCase() === "e") labelBreath("exhale");
      if (event.key.toLowerCase() === "f") flipPhase();
    });
  </script>
</body>
</html>
""",
        encoding="utf-8",
    )
    return output_path
