"""Final Vernier Graphical Analysis + voice capture demo page."""

from __future__ import annotations

from pathlib import Path


def render_final_demo_dashboard(output_path: Path, session_id: str) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_html(session_id), encoding="utf-8")
    return output_path


def _html(session_id: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Final Vernier + Voice Demo</title>
  <style>
    :root {{
      --bg: #f5f7f4;
      --panel: #ffffff;
      --ink: #151817;
      --muted: #66716c;
      --line: #d7ded8;
      --green: #227a58;
      --blue: #246a91;
      --red: #a9423f;
      --gold: #a7741f;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }}
    main {{
      width: min(1220px, calc(100vw - 28px));
      min-height: calc(100vh - 28px);
      margin: 14px auto;
      display: grid;
      grid-template-rows: auto 1fr;
      gap: 12px;
    }}
    header, section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    header {{
      display: grid;
      grid-template-columns: minmax(240px, 1fr) auto;
      gap: 12px;
      align-items: center;
      padding: 16px;
    }}
    h1 {{ margin: 0; font-size: 24px; line-height: 1.1; }}
    .sub {{ margin-top: 6px; color: var(--muted); font-size: 13px; }}
    .controls {{ display: flex; gap: 8px; flex-wrap: wrap; justify-content: end; }}
    button {{
      height: 40px;
      border: 1px solid var(--ink);
      border-radius: 8px;
      padding: 0 13px;
      background: var(--ink);
      color: #fff;
      font-weight: 760;
      cursor: pointer;
      white-space: nowrap;
    }}
    button.secondary {{ background: #fff; color: var(--ink); }}
    button.green {{ border-color: var(--green); background: var(--green); }}
    button.gold {{ border-color: var(--gold); background: var(--gold); }}
    button.red {{ border-color: var(--red); background: var(--red); }}
    button:disabled {{ opacity: 0.45; cursor: not-allowed; }}
    .grid {{
      display: grid;
      grid-template-columns: 0.82fr 1.18fr;
      gap: 12px;
      min-height: 0;
    }}
    section {{ padding: 16px; min-width: 0; }}
    .stack {{ display: grid; gap: 12px; align-content: start; }}
    .label {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 820;
      text-transform: uppercase;
    }}
    .clock {{
      margin-top: 8px;
      font-variant-numeric: tabular-nums;
      font-size: clamp(48px, 8vw, 88px);
      font-weight: 860;
      line-height: 1;
    }}
    .status-line {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.35;
    }}
    .paths {{
      display: grid;
      gap: 6px;
      margin-top: 12px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 12px;
      color: #34403b;
      overflow-wrap: anywhere;
    }}
    .transcript {{
      min-height: 430px;
      max-height: calc(100vh - 230px);
      overflow: auto;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcfa;
      font-size: 22px;
      line-height: 1.45;
    }}
    .interim {{ color: var(--muted); }}
    .event-log {{
      display: grid;
      gap: 8px;
      max-height: 260px;
      overflow: auto;
      margin-top: 12px;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcfa;
      font-size: 13px;
    }}
    .event-row {{
      display: grid;
      grid-template-columns: 92px 1fr;
      gap: 8px;
      align-items: baseline;
    }}
    .event-row time {{
      color: var(--muted);
      font-variant-numeric: tabular-nums;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }}
    textarea {{
      width: 100%;
      min-height: 74px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      font: inherit;
    }}
    @media (max-width: 900px) {{
      header {{ grid-template-columns: 1fr; }}
      .controls {{ justify-content: start; }}
      .grid {{ grid-template-columns: 1fr; }}
      .transcript {{ min-height: 300px; max-height: none; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Final Vernier + Voice Demo</h1>
        <div class="sub">Session <strong id="sessionId">{session_id}</strong> | Graphical Analysis records belt; this page records audio + transcript markers.</div>
      </div>
      <div class="controls">
        <button class="green" id="startBtn">Start Session</button>
        <button class="gold" id="vernierStartBtn" disabled>Mark Vernier Start</button>
        <button class="secondary" id="vernierStopBtn" disabled>Mark Vernier Stop</button>
        <button class="red" id="stopBtn" disabled>Stop Session</button>
      </div>
    </header>
    <div class="grid">
      <div class="stack">
        <section>
          <div class="label">Session Clock</div>
          <div class="clock" id="clock">00:00.0</div>
          <div class="status-line" id="status">Ready. Start this page, then start Vernier Graphical Analysis and mark its start.</div>
          <div class="paths" id="paths"></div>
        </section>
        <section>
          <div class="label">Session Notes</div>
          <textarea id="notes" placeholder="Mic, belt placement, Graphical Analysis file name, anything Kenny should know."></textarea>
        </section>
        <section>
          <div class="label">Markers</div>
          <div class="event-log" id="eventLog"></div>
        </section>
      </div>
      <section>
        <div class="label">Live Speech-To-Text</div>
        <div class="transcript"><span id="finalText"></span><span class="interim" id="interimText"></span></div>
      </section>
    </div>
  </main>
  <script>
    const SESSION_ID = "{session_id}";
    const state = {{
      startedAtMs: 0,
      stopped: false,
      recognition: null,
      finalText: "",
      interimText: "",
      events: []
    }};

    const startBtn = document.querySelector("#startBtn");
    const stopBtn = document.querySelector("#stopBtn");
    const vernierStartBtn = document.querySelector("#vernierStartBtn");
    const vernierStopBtn = document.querySelector("#vernierStopBtn");
    const clock = document.querySelector("#clock");
    const statusEl = document.querySelector("#status");
    const pathsEl = document.querySelector("#paths");
    const finalTextEl = document.querySelector("#finalText");
    const interimTextEl = document.querySelector("#interimText");
    const eventLog = document.querySelector("#eventLog");
    const notesEl = document.querySelector("#notes");

    startBtn.addEventListener("click", startSession);
    stopBtn.addEventListener("click", stopSession);
    vernierStartBtn.addEventListener("click", () => postMarker("vernier_start"));
    vernierStopBtn.addEventListener("click", () => postMarker("vernier_stop"));

    async function startSession() {{
      const payload = await postJson("/session/start", {{
        session_id: SESSION_ID,
        notes: notesEl.value
      }});
      state.startedAtMs = payload.marker.timestamp_ms;
      setPaths(payload.paths || {{}});
      addEvent(payload.marker);
      startBtn.disabled = true;
      stopBtn.disabled = false;
      vernierStartBtn.disabled = false;
      vernierStopBtn.disabled = false;
      notesEl.disabled = true;
      statusEl.textContent = "Session running. Start Vernier Graphical Analysis recording, then click Mark Vernier Start.";
      startSpeechRecognition();
    }}

    async function stopSession() {{
      state.stopped = true;
      if (state.recognition) state.recognition.stop();
      const payload = await postJson("/session/stop", {{
        session_id: SESSION_ID,
        notes: notesEl.value
      }});
      addEvent(payload.marker);
      stopBtn.disabled = true;
      vernierStartBtn.disabled = true;
      vernierStopBtn.disabled = true;
      statusEl.textContent = "Session stopped. Export .gambl from Graphical Analysis, then run the import and bundle commands.";
    }}

    async function postMarker(label) {{
      const payload = await postJson("/session/marker", {{
        session_id: SESSION_ID,
        label,
        notes: notesEl.value
      }});
      addEvent(payload.marker);
      if (label === "vernier_start") statusEl.textContent = "Vernier start marked. Record the belt and speak normally.";
      if (label === "vernier_stop") statusEl.textContent = "Vernier stop marked. Stop the page when the voice capture is done.";
    }}

    function startSpeechRecognition() {{
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {{
        statusEl.textContent = "SpeechRecognition is not available in this browser. Use Chrome for live transcript; WAV still records.";
        return;
      }}
      const rec = new SpeechRecognition();
      rec.continuous = true;
      rec.interimResults = true;
      rec.lang = "en-US";
      rec.onstart = () => {{
        statusEl.textContent = "Mic transcript active. Audio WAV is recorded by the local Python helper.";
      }};
      rec.onerror = event => {{
        statusEl.textContent = "Speech recognition error: " + event.error;
      }};
      rec.onend = () => {{
        if (!state.stopped && state.startedAtMs) {{
          try {{ rec.start(); }} catch (error) {{}}
        }}
      }};
      rec.onresult = event => {{
        let interim = "";
        for (let i = event.resultIndex; i < event.results.length; i += 1) {{
          const result = event.results[i];
          const text = result[0].transcript.trim();
          if (!text) continue;
          if (result.isFinal) {{
            state.finalText += text + " ";
            postTranscript(text, true, result[0].confidence);
          }} else {{
            interim = text;
          }}
        }}
        state.interimText = interim;
        renderTranscript();
      }};
      state.recognition = rec;
      rec.start();
    }}

    async function postTranscript(text, isFinal, confidence) {{
      const payload = await postJson("/transcript", {{
        session_id: SESSION_ID,
        speaker: "daley",
        text,
        is_final: isFinal,
        confidence
      }});
      addEvent({{ label: "transcript", timestamp_ms: payload.event.timestamp_ms, text }});
    }}

    async function postJson(path, payload) {{
      const response = await fetch(path, {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify(payload)
      }});
      if (!response.ok) {{
        const text = await response.text();
        throw new Error(path + " failed: " + text);
      }}
      return response.json();
    }}

    function setPaths(paths) {{
      pathsEl.innerHTML = "";
      for (const [label, path] of Object.entries(paths)) {{
        const row = document.createElement("div");
        row.textContent = label + ": " + path;
        pathsEl.appendChild(row);
      }}
    }}

    function addEvent(event) {{
      state.events.unshift(event);
      state.events = state.events.slice(0, 18);
      renderEvents();
    }}

    function renderTranscript() {{
      finalTextEl.textContent = state.finalText;
      interimTextEl.textContent = state.interimText ? " " + state.interimText : "";
    }}

    function renderEvents() {{
      eventLog.innerHTML = "";
      for (const event of state.events) {{
        const row = document.createElement("div");
        row.className = "event-row";
        const t = document.createElement("time");
        t.textContent = formatWall(event.timestamp_ms);
        const body = document.createElement("div");
        body.textContent = event.label + (event.text ? ": " + event.text : "");
        row.append(t, body);
        eventLog.appendChild(row);
      }}
    }}

    function renderClock() {{
      if (!state.startedAtMs) return;
      const elapsed = Math.max(0, Date.now() - state.startedAtMs);
      const minutes = Math.floor(elapsed / 60000);
      const seconds = Math.floor((elapsed % 60000) / 1000);
      const tenths = Math.floor((elapsed % 1000) / 100);
      clock.textContent = String(minutes).padStart(2, "0") + ":" + String(seconds).padStart(2, "0") + "." + tenths;
    }}

    function formatWall(ms) {{
      if (!ms) return "--:--:--";
      return new Date(ms).toLocaleTimeString([], {{ hour12: false }});
    }}

    setInterval(renderClock, 100);
  </script>
</body>
</html>
"""
