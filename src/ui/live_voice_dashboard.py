"""Live browser voice + breath gate dashboard."""

from __future__ import annotations

from pathlib import Path


def render_live_voice_dashboard(output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_html(), encoding="utf-8")
    return output_path


def _html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Frequency Live Voice + Breath</title>
  <style>
    :root {
      --ink: #151716;
      --muted: #66716c;
      --line: #d8ded9;
      --paper: #f5f6f2;
      --panel: #ffffff;
      --green: #23885f;
      --blue: #236b8e;
      --red: #b64b47;
      --gold: #b98220;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }
    main {
      width: min(1180px, calc(100vw - 32px));
      min-height: calc(100vh - 32px);
      margin: 16px auto;
      display: grid;
      grid-template-rows: auto 1fr;
      gap: 12px;
    }
    header, section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 16px 18px;
    }
    h1 { margin: 0; font-size: 22px; line-height: 1.1; }
    .status { color: var(--muted); font-size: 13px; }
    .grid {
      display: grid;
      grid-template-columns: 0.95fr 1.35fr 0.95fr;
      gap: 12px;
    }
    section { padding: 16px; min-width: 0; }
    .label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 760;
      text-transform: uppercase;
    }
    .value { margin-top: 10px; font-size: 44px; font-weight: 800; line-height: 1; }
    .small { margin-top: 8px; color: var(--muted); font-size: 14px; }
    .gate {
      display: grid;
      place-items: center;
      min-height: 280px;
      color: #fff;
      background: var(--ink);
      text-align: center;
    }
    .gate .value { font-size: clamp(54px, 9vw, 104px); }
    .gate.wait { background: var(--gold); }
    .gate.respond { background: var(--green); }
    .gate.ask { background: var(--blue); }
    .gate.block { background: var(--red); }
    .transcript {
      min-height: 220px;
      line-height: 1.45;
      font-size: 22px;
      overflow-wrap: anywhere;
    }
    .interim { color: var(--muted); }
    canvas {
      display: block;
      width: 100%;
      height: 180px;
      margin-top: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcfa;
    }
    button {
      height: 40px;
      border: 1px solid var(--ink);
      border-radius: 8px;
      padding: 0 14px;
      background: var(--ink);
      color: #fff;
      font-weight: 760;
      cursor: pointer;
    }
    button.secondary { background: #fff; color: var(--ink); }
    .controls { display: flex; gap: 8px; flex-wrap: wrap; }
    @media (max-width: 900px) {
      .grid { grid-template-columns: 1fr; }
      header { align-items: flex-start; flex-direction: column; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Live Voice + Breath Gate</h1>
        <div class="status" id="status">Simulator breath until Vernier JSON appears.</div>
      </div>
      <div class="controls">
        <button id="mic">Start Mic</button>
        <button class="secondary" id="reset">Reset Text</button>
      </div>
    </header>
    <div class="grid">
      <section>
        <div class="label">Breath</div>
        <div class="value" id="phase">hold</div>
        <div class="small" id="breathDetail">force -- N | rate -- bpm</div>
        <canvas id="wave" width="520" height="180"></canvas>
      </section>
      <section>
        <div class="label">Transcript</div>
        <div class="transcript"><span id="final"></span><span class="interim" id="interim"></span></div>
      </section>
      <section class="gate wait" id="gate">
        <div>
          <div class="label">Assistant Gate</div>
          <div class="value" id="action">WAIT</div>
          <div class="small" id="reason">Listening for speech and breath.</div>
        </div>
      </section>
    </div>
  </main>
  <script>
    const state = {
      finalText: "",
      interimText: "",
      speaking: false,
      lastSpeechAt: 0,
      breath: { force_n: 0, breath_rate_bpm: 0, breath_phase: "hold", source: "simulator" },
      samples: []
    };

    const phase = document.querySelector("#phase");
    const breathDetail = document.querySelector("#breathDetail");
    const statusEl = document.querySelector("#status");
    const finalEl = document.querySelector("#final");
    const interimEl = document.querySelector("#interim");
    const gate = document.querySelector("#gate");
    const actionEl = document.querySelector("#action");
    const reasonEl = document.querySelector("#reason");
    const canvas = document.querySelector("#wave");
    const ctx = canvas.getContext("2d");

    document.querySelector("#reset").addEventListener("click", () => {
      state.finalText = "";
      state.interimText = "";
      render();
    });

    document.querySelector("#mic").addEventListener("click", startMic);

    function startMic() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        statusEl.textContent = "SpeechRecognition is not available in this browser. Try Chrome.";
        return;
      }
      const rec = new SpeechRecognition();
      rec.continuous = true;
      rec.interimResults = true;
      rec.lang = "en-US";
      rec.onstart = () => { statusEl.textContent = "Mic on. Speak normally; no audio is saved by this page."; };
      rec.onerror = event => { statusEl.textContent = "Mic error: " + event.error; };
      rec.onend = () => { state.speaking = false; render(); };
      rec.onresult = event => {
        let interim = "";
        for (let i = event.resultIndex; i < event.results.length; i += 1) {
          const text = event.results[i][0].transcript;
          if (event.results[i].isFinal) state.finalText += text + " ";
          else interim += text;
        }
        state.interimText = interim;
        state.speaking = Boolean(interim.trim());
        state.lastSpeechAt = Date.now();
        render();
      };
      rec.start();
    }

    async function pollBreath() {
      try {
        const response = await fetch("vernier-live.json?ts=" + Date.now(), { cache: "no-store" });
        if (!response.ok) throw new Error("no live file");
        const breath = await response.json();
        state.breath = breath;
        statusEl.textContent = "Using " + breath.source + ". Keep Graphical Analysis disconnected if Python needs BLE.";
      } catch {
        const t = Date.now() / 1000;
        const force = 12 + Math.sin(t * 1.8) * 4;
        const slope = Math.cos(t * 1.8);
        state.breath = {
          source: "simulator",
          force_n: force,
          breath_rate_bpm: 10 + Math.sin(t * 0.35) * 1.2,
          breath_phase: slope > 0.16 ? "inhale" : slope < -0.16 ? "exhale" : "hold"
        };
      }
      state.samples.push(state.breath.force_n || 0);
      if (state.samples.length > 120) state.samples.shift();
      render();
    }

    function chooseAction() {
      const silenceMs = Date.now() - state.lastSpeechAt;
      const hasText = (state.finalText + state.interimText).trim().length > 0;
      if (state.speaking) return ["WAIT", "block", "User is speaking."];
      if (state.breath.breath_phase === "inhale" && silenceMs < 1800) return ["WAIT", "wait", "Silent inhale looks like thinking, not done."];
      if (hasText && state.breath.breath_phase === "exhale" && silenceMs > 900) return ["RESPOND", "respond", "Speech paused on exhale."];
      if (hasText && silenceMs > 2500) return ["ASK", "ask", "Long pause; ask a short clarifying question."];
      return ["WAIT", "wait", "Still gathering voice and breath context."];
    }

    function render() {
      phase.textContent = state.breath.breath_phase || "hold";
      breathDetail.textContent = `force ${(state.breath.force_n || 0).toFixed(2)} N | rate ${(state.breath.breath_rate_bpm || 0).toFixed(1)} bpm`;
      finalEl.textContent = state.finalText;
      interimEl.textContent = state.interimText;
      const [action, className, reason] = chooseAction();
      gate.className = "gate " + className;
      actionEl.textContent = action;
      reasonEl.textContent = reason;
      drawWave();
    }

    function drawWave() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const samples = state.samples.length ? state.samples : [0];
      const min = Math.min(...samples);
      const max = Math.max(...samples);
      const span = Math.max(1, max - min);
      ctx.lineWidth = 4;
      ctx.strokeStyle = "#23885f";
      ctx.beginPath();
      samples.forEach((value, index) => {
        const x = (index / Math.max(1, samples.length - 1)) * canvas.width;
        const y = canvas.height - 18 - ((value - min) / span) * (canvas.height - 36);
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
    }

    setInterval(pollBreath, 250);
    setInterval(render, 250);
    pollBreath();
  </script>
</body>
</html>
"""
