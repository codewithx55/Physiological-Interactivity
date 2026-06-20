"""Render a force-only Vernier-style inhale/exhale dashboard."""

from __future__ import annotations

from pathlib import Path


def render_vernier_breath_dashboard(output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_html(), encoding="utf-8")
    return output_path


def _html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Vernier Force Breath Phase</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #252627;
      --chrome: #3a3a40;
      --panel: #282929;
      --grid: #414344;
      --axis: #f3f3f3;
      --text: #f4f4f4;
      --force: #ffd514;
      --inhale: #1ca777;
      --exhale: #cb4164;
      --hold: #6f767f;
      --line: #44484b;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      overflow: hidden;
      background: #1e2732;
      color: var(--text);
      font-family: Arial, Helvetica, sans-serif;
      letter-spacing: 0;
    }
    .window {
      width: 100vw;
      height: 100vh;
      min-height: 780px;
      display: grid;
      grid-template-rows: 40px 70px 1fr 66px;
      background: var(--bg);
      border: 1px solid #161616;
    }
    .titlebar {
      position: relative;
      display: grid;
      place-items: center;
      background: var(--chrome);
      border-bottom: 1px solid #202124;
      color: #d8d8db;
      font-size: 18px;
      font-weight: 760;
    }
    .traffic {
      position: absolute;
      left: 18px;
      top: 50%;
      display: flex;
      gap: 12px;
      transform: translateY(-50%);
    }
    .dot { width: 18px; height: 18px; border-radius: 50%; }
    .dot.red { background: #ff5f57; }
    .dot.gray { background: #73757b; }
    .dot.green { background: #28c840; }
    .toolbar {
      display: grid;
      grid-template-columns: 1fr auto 1fr;
      align-items: center;
      padding: 0 24px;
      border-bottom: 1px solid var(--line);
      background: #262727;
    }
    .document {
      display: flex;
      align-items: center;
      gap: 14px;
      font-size: 18px;
      font-weight: 760;
    }
    .file-icon {
      width: 30px;
      height: 36px;
      border: 4px solid #e8e8e8;
    }
    .stop {
      width: 136px;
      height: 52px;
      display: grid;
      place-items: center;
      border: 2px solid #666a70;
      border-radius: 6px;
      background: #2b2c30;
      font-size: 22px;
      font-weight: 900;
    }
    .tools {
      justify-self: end;
      display: flex;
      align-items: center;
      gap: 20px;
      color: #dddddd;
      font-size: 28px;
      font-weight: 800;
    }
    .tool-button {
      width: 34px;
      height: 38px;
      display: grid;
      place-items: center;
      border: 0;
      background: transparent;
      color: inherit;
      font: inherit;
    }
    .workspace {
      position: relative;
      padding: 68px 0 86px 184px;
      min-height: 0;
    }
    .plot-row {
      position: relative;
      width: 100%;
      height: 100%;
      min-height: 520px;
    }
    .plot-wrap {
      position: relative;
      width: 100%;
      height: 100%;
    }
    canvas {
      display: block;
      width: 100%;
      height: 100%;
      background: var(--panel);
    }
    .axis-label {
      position: absolute;
      left: -174px;
      top: 50%;
      width: 72px;
      height: 170px;
      display: grid;
      place-items: center;
      border: 2px solid #777c81;
      border-radius: 7px;
      background: #2c2e30;
      color: #f6f6f6;
      font-size: 21px;
      font-weight: 900;
      writing-mode: vertical-rl;
      transform: translateY(-50%) rotate(180deg);
    }
    .axis-label::before {
      content: "";
      position: absolute;
      left: 17px;
      top: 32px;
      bottom: 32px;
      width: 4px;
      border-radius: 4px;
      background: var(--force);
    }
    .small-tool {
      position: absolute;
      left: -174px;
      bottom: -68px;
      display: flex;
      gap: 16px;
    }
    .small-tool span {
      width: 68px;
      height: 68px;
      display: grid;
      place-items: center;
      border: 2px solid #777c81;
      border-radius: 7px;
      background: #2c2e30;
      color: #f6f6f6;
      font-size: 31px;
      font-weight: 900;
    }
    .x-label {
      position: absolute;
      left: 50%;
      bottom: -62px;
      min-width: 108px;
      height: 50px;
      display: grid;
      place-items: center;
      transform: translateX(-50%);
      border: 2px solid #777c81;
      border-radius: 7px;
      background: #2c2e30;
      font-weight: 900;
    }
    .footer {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 18px;
      align-items: center;
      padding: 0 24px;
      border-top: 1px solid var(--line);
      background: #262727;
      color: #e5e5e5;
      font-size: 17px;
      font-weight: 760;
    }
    .footer-left, .footer-right {
      display: flex;
      gap: 24px;
      align-items: center;
      min-width: 0;
    }
    .footer-right {
      justify-content: end;
      flex-wrap: wrap;
    }
    .phase-pill {
      min-width: 184px;
      height: 42px;
      display: grid;
      grid-template-columns: 48px 1fr;
      align-items: center;
      border: 2px solid rgba(255,255,255,0.55);
      border-radius: 7px;
      overflow: hidden;
      background: var(--hold);
      font-weight: 900;
    }
    .phase-pill.inhale { background: var(--inhale); }
    .phase-pill.exhale { background: var(--exhale); }
    .phase-pill.hold { background: var(--hold); }
    .phase-arrow {
      height: 100%;
      display: grid;
      place-items: center;
      border-right: 2px solid rgba(255,255,255,0.4);
      font-size: 15px;
    }
    .phase-word {
      padding: 0 12px;
      font-size: 22px;
    }
    .readout strong { color: #ffffff; }
    .flip {
      height: 38px;
      border: 2px solid #777c81;
      border-radius: 7px;
      padding: 0 12px;
      background: #303237;
      color: #f4f4f4;
      font: inherit;
      font-size: 14px;
      font-weight: 900;
      cursor: pointer;
    }
    .flip.active {
      border-color: var(--force);
      color: var(--force);
    }
    @media (max-width: 900px) {
      body { overflow: auto; }
      .window {
        height: auto;
        min-height: 100vh;
        grid-template-rows: 40px 64px 720px auto;
      }
      .toolbar { padding: 0 12px; }
      .document { font-size: 16px; }
      .stop { width: 104px; height: 44px; font-size: 18px; }
      .tools { gap: 6px; font-size: 20px; }
      .workspace { padding: 44px 0 90px 90px; }
      .plot-row { min-height: 520px; }
      .axis-label {
        left: -80px;
        width: 70px;
        height: 170px;
        font-size: 19px;
      }
      .small-tool { left: -80px; }
      .small-tool span { width: 68px; height: 68px; }
      .footer {
        grid-template-columns: 1fr;
        padding: 12px 14px;
        font-size: 15px;
      }
      .footer-left, .footer-right { gap: 12px; flex-wrap: wrap; justify-content: start; }
    }
  </style>
</head>
<body>
  <main class="window">
    <div class="titlebar">
      <div class="traffic">
        <span class="dot red"></span>
        <span class="dot gray"></span>
        <span class="dot green"></span>
      </div>
      Vernier Graphical Analysis&reg;
    </div>
    <div class="toolbar">
      <div class="document"><span class="file-icon"></span><span>Untitled</span></div>
      <div class="stop">STOP</div>
      <div class="tools" aria-label="Graph tools">
        <button class="tool-button" title="Help">?</button>
        <button class="tool-button" title="Wireless">((o))</button>
        <button class="tool-button" title="Reset">R</button>
        <button class="tool-button" title="Layout">[]</button>
        <button class="tool-button" title="More">...</button>
      </div>
    </div>
    <section class="workspace" aria-label="Live Vernier force graph">
      <div class="plot-row">
        <div class="axis-label">Force (N)</div>
        <div class="plot-wrap">
          <canvas id="forceCanvas" width="1450" height="640"></canvas>
          <div class="x-label">Time (s)</div>
        </div>
        <div class="small-tool"><span title="Graph options">/</span><span title="Zoom">Q</span></div>
      </div>
    </section>
    <footer class="footer">
      <div class="footer-left">
        <span>Mode: Time Based</span>
        <span>Rate: 10 samples/s</span>
        <span id="source">Source: simulator force trace</span>
      </div>
      <div class="footer-right">
        <div class="phase-pill hold" id="phasePill">
          <span class="phase-arrow" id="phaseArrow">-</span>
          <span class="phase-word" id="phaseWord">HOLD</span>
        </div>
        <span class="readout">Force: <strong id="forceReadout">-- N</strong></span>
        <button class="flip" id="flipBtn">Flip direction</button>
      </div>
    </footer>
  </main>
  <script>
    const forceCanvas = document.getElementById("forceCanvas");
    const phasePill = document.getElementById("phasePill");
    const phaseArrow = document.getElementById("phaseArrow");
    const phaseWord = document.getElementById("phaseWord");
    const sourceEl = document.getElementById("source");
    const forceReadout = document.getElementById("forceReadout");
    const flipBtn = document.getElementById("flipBtn");

    const state = {
      samples: [],
      phase: "hold",
      lastPhaseChangeMs: 0,
      lastLiveUpdate: 0,
      startedAt: Date.now() / 1000,
      inverted: window.localStorage.getItem("vernier_phase_inverted") === "true",
      usingLive: false
    };

    const MAX_SECONDS = 130;
    const SAMPLE_MS = 100;
    const FORCE_MIN = -10;
    const FORCE_MAX = 80;

    const demoTrace = [
      [0.0, 20.0], [0.8, 22.0], [1.6, 25.0], [2.2, 32.0], [3.0, 43.0],
      [3.8, 50.0], [4.3, 54.0], [5.2, 33.0], [5.9, 22.0], [6.6, 19.0],
      [7.5, 25.0], [8.4, 24.0], [9.2, 15.0], [10.0, 4.8], [10.8, 2.2],
      [12.5, 1.8], [14.0, 2.1], [16.0, 1.8], [18.0, 2.0], [19.5, 2.5],
      [20.4, 22.0], [21.0, 23.0], [21.7, 38.0], [22.3, 52.0], [22.8, 65.0],
      [23.3, 72.0], [23.8, 66.0], [24.4, 12.0], [25.0, 5.0], [25.8, 3.8],
      [26.8, 5.8], [27.6, 4.8], [28.6, 6.0], [30.0, 5.5], [31.8, 5.0],
      [34.0, 4.8], [36.2, 6.8], [38.0, 7.2]
    ];

    flipBtn.addEventListener("click", () => {
      state.inverted = !state.inverted;
      window.localStorage.setItem("vernier_phase_inverted", state.inverted ? "true" : "false");
      flipBtn.classList.toggle("active", state.inverted);
      state.phase = "hold";
    });
    flipBtn.classList.toggle("active", state.inverted);

    function nowSeconds() {
      return Date.now() / 1000;
    }

    async function pollSample() {
      let payload = null;
      try {
        const response = await fetch("vernier-live.json?ts=" + Date.now(), { cache: "no-store" });
        if (response.ok) {
          const live = await response.json();
          if (Number.isFinite(Number(live.force_n))) {
            state.lastLiveUpdate = Date.now();
            state.usingLive = true;
            if (Array.isArray(live.recent_samples) && live.recent_samples.length) {
              loadLiveHistory(live);
              render();
              return;
            }
            payload = normalizeLive(live);
          }
        }
      } catch (error) {}

      if (!payload || Date.now() - state.lastLiveUpdate > 2200) {
        state.usingLive = false;
        payload = simulatorPayload();
      }

      addSample(payload);
      render();
    }

    function normalizeLive(payload) {
      return {
        source: payload.source || "vernier_live",
        force_n: Number(payload.force_n),
        breath_phase: payload.breath_phase || "hold",
        updated_at: Number(payload.updated_at || nowSeconds()),
        t: Number.isFinite(Number(payload.at_ms)) ? Number(payload.at_ms) / 1000 : nowSeconds() - state.startedAt
      };
    }

    function loadLiveHistory(payload) {
      const samples = payload.recent_samples
        .map(sample => ({
          t: Number(sample.at_ms || 0) / 1000,
          source: payload.source || "vernier_live",
          force: Number(sample.force_n),
          rawPhase: payload.breath_phase || "hold"
        }))
        .filter(sample => Number.isFinite(sample.t) && Number.isFinite(sample.force));
      if (samples.length) {
        state.samples = samples.slice(-1300);
        if (["inhale", "exhale", "hold"].includes(payload.breath_phase)) {
          setPhase(payload.breath_phase);
        } else {
          classifyPhase();
        }
      }
    }

    function simulatorPayload() {
      const elapsed = Math.min(38, nowSeconds() - state.startedAt);
      return {
        source: "simulator force trace",
        force_n: interpolateDemo(elapsed),
        breath_phase: "hold",
        updated_at: nowSeconds(),
        t: elapsed
      };
    }

    function interpolateDemo(t) {
      for (let i = 1; i < demoTrace.length; i += 1) {
        const prev = demoTrace[i - 1];
        const next = demoTrace[i];
        if (t <= next[0]) {
          const pct = (t - prev[0]) / Math.max(0.001, next[0] - prev[0]);
          const wiggle = Math.sin(t * 7.1) * 0.35 + Math.sin(t * 2.3) * 0.22;
          return prev[1] + (next[1] - prev[1]) * pct + wiggle;
        }
      }
      const last = demoTrace[demoTrace.length - 1][1];
      return last + Math.sin(t * 1.1) * 0.35 + Math.sin(t * 4.2) * 0.12;
    }

    function addSample(payload) {
      const sample = {
        t: payload.t,
        source: payload.source,
        force: Number(payload.force_n),
        rawPhase: payload.breath_phase || "hold"
      };
      state.samples.push(sample);
      while (state.samples.length > 2 && state.samples[0].t < sample.t - MAX_SECONDS) state.samples.shift();
      classifyPhase();
    }

    function classifyPhase() {
      if (state.samples.length < 5) {
        setPhase("hold");
        return;
      }
      const recent = state.samples.slice(-10);
      const head = average(recent.slice(0, 3).map(s => s.force));
      const tail = average(recent.slice(-3).map(s => s.force));
      const polarity = state.inverted ? -1 : 1;
      const delta = (tail - head) * polarity;
      if (delta > 0.25) setPhase("inhale");
      else if (delta < -0.25) setPhase("exhale");
      else if (Date.now() - state.lastPhaseChangeMs > 1200) setPhase("hold");
    }

    function setPhase(next) {
      if (state.phase !== next) {
        state.phase = next;
        state.lastPhaseChangeMs = Date.now();
      }
    }

    function average(values) {
      if (!values.length) return 0;
      return values.reduce((sum, value) => sum + value, 0) / values.length;
    }

    function render() {
      const latest = state.samples[state.samples.length - 1] || { force: 0, source: "simulator force trace" };
      phasePill.className = "phase-pill " + state.phase;
      phaseWord.textContent = state.phase.toUpperCase();
      phaseArrow.textContent = state.phase === "inhale" ? "UP" : state.phase === "exhale" ? "DN" : "-";
      sourceEl.textContent = "Source: " + latest.source;
      forceReadout.textContent = latest.force.toFixed(2) + " N";
      drawForceGraph(forceCanvas, state.samples.map(s => ({ t: s.t, v: s.force })));
    }

    function drawForceGraph(canvas, samples) {
      const ctx = canvas.getContext("2d");
      const width = canvas.width;
      const height = canvas.height;
      ctx.clearRect(0, 0, width, height);
      ctx.fillStyle = "#282929";
      ctx.fillRect(0, 0, width, height);

      const plotLeft = 0;
      const plotTop = 0;
      const plotRight = width;
      const plotBottom = height - 54;
      const spanY = FORCE_MAX - FORCE_MIN;

      ctx.strokeStyle = "#414344";
      ctx.lineWidth = 1.2;
      ctx.font = "25px Arial, Helvetica, sans-serif";
      ctx.fillStyle = "#f0f0f0";
      ctx.textAlign = "right";
      ctx.textBaseline = "middle";

      for (const tick of [-10, 0, 10, 20, 30, 40, 50, 60, 70]) {
        const y = yFor(tick);
        ctx.beginPath();
        ctx.moveTo(plotLeft, y);
        ctx.lineTo(plotRight, y);
        ctx.stroke();
        if (tick === 70 || tick === 0 || tick === -10) labelBox(ctx, String(tick), -16, y);
        else ctx.fillText(String(tick), -28, y);
      }

      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      for (const tick of [0, 50, 100]) {
        const x = xFor(tick);
        ctx.beginPath();
        ctx.moveTo(x, plotTop);
        ctx.lineTo(x, plotBottom);
        ctx.stroke();
        labelBox(ctx, String(tick), x, plotBottom + 42, true);
      }

      ctx.strokeStyle = "#f1f1f1";
      ctx.lineWidth = 3.4;
      ctx.beginPath();
      ctx.moveTo(plotLeft, yFor(0));
      ctx.lineTo(plotRight, yFor(0));
      ctx.moveTo(plotLeft, plotTop);
      ctx.lineTo(plotLeft, plotBottom);
      ctx.stroke();

      ctx.strokeStyle = "#ffd514";
      ctx.lineWidth = 4.8;
      ctx.lineJoin = "round";
      ctx.lineCap = "round";
      ctx.beginPath();
      let hasPoint = false;
      for (const sample of samples) {
        if (sample.t < 0 || sample.t > MAX_SECONDS) continue;
        const x = xFor(sample.t);
        const y = yFor(sample.v);
        if (!hasPoint) {
          ctx.moveTo(x, y);
          hasPoint = true;
        } else {
          ctx.lineTo(x, y);
        }
      }
      if (hasPoint) ctx.stroke();

      function xFor(t) {
        return plotLeft + (t / MAX_SECONDS) * (plotRight - plotLeft);
      }
      function yFor(value) {
        const clamped = Math.max(FORCE_MIN, Math.min(FORCE_MAX, value));
        return plotBottom - ((clamped - FORCE_MIN) / spanY) * (plotBottom - plotTop);
      }
    }

    function labelBox(ctx, text, x, y, centered = false) {
      const metrics = ctx.measureText(text);
      const width = metrics.width + 14;
      const height = 34;
      const left = centered ? x - width / 2 : x - width;
      const top = y - height / 2;
      ctx.save();
      ctx.strokeStyle = "#f1f1f1";
      ctx.lineWidth = 2;
      ctx.fillStyle = "#303235";
      roundRect(ctx, left, top, width, height, 5);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = "#f4f4f4";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(text, left + width / 2, top + height / 2 + 1);
      ctx.restore();
    }

    function roundRect(ctx, x, y, width, height, radius) {
      ctx.beginPath();
      ctx.moveTo(x + radius, y);
      ctx.lineTo(x + width - radius, y);
      ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
      ctx.lineTo(x + width, y + height - radius);
      ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
      ctx.lineTo(x + radius, y + height);
      ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
      ctx.lineTo(x, y + radius);
      ctx.quadraticCurveTo(x, y, x + radius, y);
      ctx.closePath();
    }

    setInterval(pollSample, SAMPLE_MS);
    pollSample();
  </script>
</body>
</html>
"""
