"""Film-mode dashboard for the physiology turn-taking demo."""

from __future__ import annotations

import html
import json
from pathlib import Path

from src.sensors.vernier_mock import mock_vernier_frames


def render_film_dashboard(output_path: Path) -> Path:
    frames = mock_vernier_frames()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_html(frames), encoding="utf-8")
    return output_path


def _html(frames: list[dict[str, object]]) -> str:
    data = json.dumps(frames).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Frequency Turn-Taking Film Demo</title>
  <style>
    :root {{
      --ink: #151514;
      --paper: #f5f2ea;
      --lime: #b7f566;
      --teal: #1f8a83;
      --coral: #ff6f61;
      --violet: #7457d8;
      --amber: #f0b83f;
      --muted: #75706a;
      --line: rgba(21, 21, 20, 0.14);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at 12% 12%, rgba(183, 245, 102, 0.34), transparent 24%),
        linear-gradient(135deg, #f7f4eb 0%, #eef1ed 44%, #f8f1ee 100%);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }}
    .stage {{
      width: min(1180px, calc(100vw - 40px));
      min-height: min(720px, calc(100vh - 40px));
      margin: 20px auto;
      display: grid;
      grid-template-rows: auto 1fr auto;
      gap: 18px;
    }}
    header, .main, .timeline {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.68);
      box-shadow: 0 18px 60px rgba(21, 21, 20, 0.08);
      backdrop-filter: blur(18px);
    }}
    header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 18px 20px;
      gap: 18px;
    }}
    h1 {{ margin: 0; font-size: 24px; line-height: 1; }}
    .tag {{
      color: var(--muted);
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      white-space: nowrap;
    }}
    .main {{
      display: grid;
      grid-template-columns: 1fr 1.1fr 1fr;
      gap: 16px;
      padding: 18px;
      min-height: 460px;
    }}
    .panel {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      background: rgba(255, 255, 255, 0.58);
      min-width: 0;
    }}
    .label {{
      margin-bottom: 12px;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }}
    .breath-value {{
      font-size: 46px;
      font-weight: 780;
      line-height: 1;
      margin-bottom: 8px;
    }}
    .wavebox {{
      height: 260px;
      display: grid;
      align-items: center;
    }}
    svg {{ width: 100%; height: 230px; overflow: visible; }}
    .wave-path {{
      fill: none;
      stroke: var(--teal);
      stroke-width: 8;
      stroke-linecap: round;
      filter: drop-shadow(0 8px 16px rgba(31, 138, 131, 0.26));
    }}
    .pulse {{
      fill: var(--lime);
      stroke: var(--ink);
      stroke-width: 3;
    }}
    .agent {{
      display: grid;
      align-content: center;
      text-align: center;
      background: var(--ink);
      color: #fff;
      position: relative;
      overflow: hidden;
    }}
    .agent::after {{
      content: "";
      position: absolute;
      inset: auto -20% -44% -20%;
      height: 180px;
      background: linear-gradient(90deg, var(--lime), var(--teal), var(--violet), var(--coral));
      opacity: 0.9;
      transform: skewY(-5deg);
    }}
    .agent-state {{
      position: relative;
      z-index: 1;
      font-size: 56px;
      font-weight: 820;
      line-height: 0.92;
    }}
    .agent-line {{
      position: relative;
      z-index: 1;
      max-width: 320px;
      margin: 20px auto 0;
      color: rgba(255, 255, 255, 0.78);
      font-size: 18px;
      line-height: 1.3;
    }}
    .decision {{
      display: grid;
      gap: 14px;
      align-content: center;
    }}
    .choice {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      background: rgba(255, 255, 255, 0.78);
    }}
    .choice strong {{
      display: block;
      font-size: 30px;
      line-height: 1;
      margin-top: 8px;
    }}
    .baseline strong {{ color: var(--coral); }}
    .physio strong {{ color: var(--teal); }}
    .meter {{
      height: 10px;
      margin-top: 14px;
      border-radius: 999px;
      background: rgba(21, 21, 20, 0.1);
      overflow: hidden;
    }}
    .fill {{
      height: 100%;
      border-radius: inherit;
      background: currentColor;
      width: 0%;
      transition: width 360ms ease;
    }}
    .timeline {{
      padding: 14px 18px 18px;
    }}
    .beats {{
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      gap: 8px;
    }}
    .beat {{
      height: 10px;
      border-radius: 999px;
      background: rgba(21, 21, 20, 0.14);
    }}
    .beat.active {{ background: var(--lime); box-shadow: 0 0 0 3px rgba(183, 245, 102, 0.3); }}
    .controls {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 14px;
      gap: 14px;
    }}
    button {{
      border: 1px solid var(--ink);
      border-radius: 8px;
      background: var(--ink);
      color: #fff;
      height: 40px;
      padding: 0 16px;
      font-weight: 760;
      cursor: pointer;
    }}
    input[type="range"] {{ width: 100%; accent-color: var(--teal); }}
    .small {{ color: var(--muted); font-size: 13px; min-width: 82px; text-align: right; }}
    @media (max-width: 900px) {{
      .stage {{ width: calc(100vw - 24px); margin: 12px auto; }}
      header {{ align-items: flex-start; flex-direction: column; }}
      .main {{ grid-template-columns: 1fr; }}
      .agent-state {{ font-size: 44px; }}
      .beats {{ grid-template-columns: repeat(4, 1fr); }}
    }}
  </style>
</head>
<body>
  <div class="stage">
    <header>
      <div>
        <div class="tag">SIMULATED VERNIER-SHAPED SIGNAL</div>
        <h1>Frequency Turn Gate</h1>
      </div>
      <div class="tag">breath + cadence → agent timing</div>
    </header>

    <section class="main">
      <div class="panel">
        <div class="label">Respiration Belt</div>
        <div class="breath-value" id="phase">INHALE</div>
        <div id="sample" class="tag">0.00 a.u. · 0 bpm</div>
        <div class="wavebox">
          <svg viewBox="0 0 420 240" aria-label="breath waveform">
            <path id="wave" class="wave-path" d="" />
            <circle id="pulse" class="pulse" cx="0" cy="120" r="11" />
          </svg>
        </div>
      </div>

      <div class="panel agent">
        <div class="label">Agent</div>
        <div id="agentState" class="agent-state">LISTENING</div>
        <div id="agentLine" class="agent-line">User has the floor.</div>
      </div>

      <div class="panel decision">
        <div class="choice baseline">
          <div class="label">Baseline VAD</div>
          <strong id="baselineAction">LISTEN</strong>
          <div class="meter"><div id="baselineFill" class="fill"></div></div>
        </div>
        <div class="choice physio">
          <div class="label">Physiology Gate</div>
          <strong id="physioAction">LISTEN</strong>
          <div class="meter"><div id="physioFill" class="fill"></div></div>
        </div>
      </div>
    </section>

    <section class="timeline">
      <div class="beats" id="beats"></div>
      <div class="controls">
        <button id="play">Play</button>
        <button id="reset">Reset</button>
        <input id="scrub" type="range" min="0" max="6" value="0">
        <div class="small" id="clock">0ms</div>
      </div>
    </section>
  </div>

  <script id="frames" type="application/json">{data}</script>
  <script>
    const frames = JSON.parse(document.getElementById("frames").textContent);
    const els = {{
      phase: document.getElementById("phase"),
      sample: document.getElementById("sample"),
      wave: document.getElementById("wave"),
      pulse: document.getElementById("pulse"),
      agentState: document.getElementById("agentState"),
      agentLine: document.getElementById("agentLine"),
      baselineAction: document.getElementById("baselineAction"),
      baselineFill: document.getElementById("baselineFill"),
      physioAction: document.getElementById("physioAction"),
      physioFill: document.getElementById("physioFill"),
      beats: document.getElementById("beats"),
      play: document.getElementById("play"),
      reset: document.getElementById("reset"),
      scrub: document.getElementById("scrub"),
      clock: document.getElementById("clock"),
    }};
    let index = 0;
    let timer = null;
    els.scrub.max = String(frames.length - 1);
    els.beats.innerHTML = frames.map(() => '<div class="beat"></div>').join("");
    const beats = [...els.beats.querySelectorAll(".beat")];

    function displayAction(action) {{
      return action === "ASK_SHORT_CLARIFYING_QUESTION" ? "ASK" : action;
    }}

    function agentState(frame) {{
      const action = frame.physiology.action;
      if (action === "WAIT") return "WAITING";
      if (action === "RESPOND") return "RESPONDING";
      if (action === "ASK_SHORT_CLARIFYING_QUESTION") return "ASKING";
      return "LISTENING";
    }}

    function wavePath(current) {{
      const values = frames.map((frame, i) => {{
        const base = frame.sample.breath_signal;
        return i === current ? base : base * 0.7;
      }});
      return values.map((value, i) => {{
        const x = 22 + i * (376 / Math.max(1, values.length - 1));
        const y = 120 - value * 86;
        return `${{i === 0 ? "M" : "L"}} ${{x.toFixed(1)}} ${{y.toFixed(1)}}`;
      }}).join(" ");
    }}

    function render(next) {{
      index = Number(next);
      const frame = frames[index];
      const sample = frame.sample;
      els.phase.textContent = String(sample.breath_phase).toUpperCase();
      els.sample.textContent = `${{sample.raw.toFixed(3)}} ${{sample.units}} · ${{sample.breath_rate_bpm.toFixed(1)}} bpm`;
      els.wave.setAttribute("d", wavePath(index));
      const x = 22 + index * (376 / Math.max(1, frames.length - 1));
      const y = 120 - sample.breath_signal * 86;
      els.pulse.setAttribute("cx", x.toFixed(1));
      els.pulse.setAttribute("cy", y.toFixed(1));
      els.agentState.textContent = agentState(frame);
      els.agentLine.textContent = frame.agent_line;
      els.baselineAction.textContent = displayAction(frame.baseline.action);
      els.physioAction.textContent = displayAction(frame.physiology.action);
      els.baselineFill.style.width = `${{Math.round(frame.baseline.end_of_turn_probability * 100)}}%`;
      els.physioFill.style.width = `${{Math.round(frame.physiology.end_of_turn_probability * 100)}}%`;
      els.scrub.value = String(index);
      els.clock.textContent = `${{frame.sample.timestamp_ms}}ms`;
      beats.forEach((beat, i) => beat.classList.toggle("active", i === index));
    }}

    function stop() {{
      clearInterval(timer);
      timer = null;
      els.play.textContent = "Play";
    }}

    els.play.addEventListener("click", () => {{
      if (timer) {{
        stop();
        return;
      }}
      els.play.textContent = "Pause";
      timer = setInterval(() => {{
        if (index >= frames.length - 1) {{
          stop();
          return;
        }}
        render(index + 1);
      }}, 1150);
    }});
    els.reset.addEventListener("click", () => {{
      stop();
      render(0);
    }});
    els.scrub.addEventListener("input", event => {{
      stop();
      render(event.target.value);
    }});
    render(0);
  </script>
</body>
</html>
"""
