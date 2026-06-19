"""Static HTML dashboard for synthetic turn-taking traces."""

from __future__ import annotations

import html
import json
from pathlib import Path

from src.sensors.simulator import load_scenarios
from src.turn_taking.evaluator import evaluate, EvaluatedEvent, PolicyMetrics


def _action_class(action: str) -> str:
    return action.lower().replace("_", "-")


def _rows_for_scenario(rows: list[EvaluatedEvent], scenario_id: str) -> list[EvaluatedEvent]:
    return [row for row in rows if row.scenario_id == scenario_id]


def render_dashboard(output_path: Path) -> Path:
    rows, metrics = evaluate()
    scenarios = load_scenarios()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Physiology-Aware Turn-Taking Demo</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #17201a;
      --muted: #66736b;
      --line: #d7ded6;
      --bg: #f6f7f3;
      --panel: #ffffff;
      --speech: #2f6f73;
      --breath: #8d5a2b;
      --baseline: #b84444;
      --physio: #2f7d4f;
      --clarify: #8060a8;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
      letter-spacing: 0;
    }}
    header {{
      padding: 28px 32px 18px;
      border-bottom: 1px solid var(--line);
      background: #eef3ed;
    }}
    h1 {{ margin: 0 0 8px; font-size: 30px; line-height: 1.1; }}
    h2 {{ margin: 0 0 12px; font-size: 18px; }}
    h3 {{ margin: 0 0 6px; font-size: 15px; }}
    p {{ margin: 0; color: var(--muted); max-width: 920px; }}
    main {{ padding: 20px 32px 40px; }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin-bottom: 20px;
    }}
    .metric {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }}
    .metric strong {{ display: block; font-size: 26px; margin-top: 6px; }}
    .scenario {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      margin: 0 0 18px;
      padding: 16px;
    }}
    .timeline {{
      display: grid;
      gap: 8px;
      margin-top: 14px;
    }}
    .event {{
      display: grid;
      grid-template-columns: 78px minmax(130px, 1.4fr) minmax(170px, 1fr) minmax(160px, 1fr) minmax(170px, 1fr);
      gap: 10px;
      align-items: stretch;
      min-height: 58px;
    }}
    .cell {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px;
      background: #fbfcfa;
      overflow-wrap: anywhere;
    }}
    .time {{ font-variant-numeric: tabular-nums; color: var(--muted); white-space: nowrap; }}
    .token.active {{ border-left: 5px solid var(--speech); }}
    .token.silent {{ border-left: 5px solid #aeb8b0; }}
    .wave {{
      height: 8px;
      margin-top: 8px;
      border-radius: 999px;
      background: linear-gradient(90deg, #d4c1a1, var(--breath));
      transform-origin: left center;
    }}
    .pill {{
      display: inline-flex;
      align-items: center;
      min-height: 26px;
      padding: 4px 8px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      color: #fff;
      background: var(--muted);
    }}
    .respond {{ background: var(--physio); }}
    .wait {{ background: #6f7c75; }}
    .listen {{ background: var(--speech); }}
    .ask-short-clarifying-question {{ background: var(--clarify); }}
    .baseline .respond {{ background: var(--baseline); }}
    .prob {{ margin-top: 6px; color: var(--muted); font-size: 12px; }}
    .truth {{ font-size: 12px; color: var(--muted); margin-top: 6px; }}
    @media (max-width: 900px) {{
      header, main {{ padding-left: 16px; padding-right: 16px; }}
      .event {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Physiology-Aware Turn-Taking for Real-Time Voice AI</h1>
    <p>Synthetic research demo: audio/prosody + respiration + optional HR/EMG signals estimate when an assistant should listen, wait, respond, or ask a short clarifying question.</p>
  </header>
  <main>
    <section class="metrics">
      {_render_metrics(metrics)}
    </section>
    {_render_scenarios(scenarios, rows)}
  </main>
  <script type="application/json" id="demo-data">{html.escape(json.dumps(_json_payload(metrics), indent=2))}</script>
</body>
</html>
"""
    output_path.write_text(html_text, encoding="utf-8")
    return output_path


def _render_metrics(metrics: list[PolicyMetrics]) -> str:
    blocks: list[str] = []
    for metric in metrics:
        blocks.append(
            f"""<article class="metric">
  <h2>{html.escape(metric.policy.title())}</h2>
  <p>False interruptions: {metric.false_interruptions} | Latency: {metric.true_end_latency_ms}ms | Unneeded wait: {metric.unnecessary_wait_ms}ms</p>
  <strong>{metric.score}</strong>
  <p>score</p>
</article>"""
        )
    return "\n".join(blocks)


def _render_scenarios(scenarios, rows: list[EvaluatedEvent]) -> str:
    blocks: list[str] = []
    for scenario in scenarios:
        event_rows = _rows_for_scenario(rows, scenario.id)
        events_html = "\n".join(_render_event(row) for row in event_rows)
        blocks.append(
            f"""<section class="scenario">
  <h2>{html.escape(scenario.title)}</h2>
  <p>{html.escape(scenario.description)}</p>
  <div class="timeline">
    {events_html}
  </div>
</section>"""
        )
    return "\n".join(blocks)


def _render_event(row: EvaluatedEvent) -> str:
    event = row.event
    token_class = "active" if event.speech_active else "silent"
    token = html.escape(event.token if event.token else "silence")
    wave_scale = max(0.12, min(1.0, abs(event.breath_signal)))
    return f"""<div class="event">
  <div class="cell time">{event.at_ms}ms</div>
  <div class="cell token {token_class}"><h3>{token}</h3><div class="truth">truth: {event.ground_truth}; silence: {event.silence_ms}ms</div></div>
  <div class="cell"><h3>Breath: {event.breath_phase}</h3><div>{event.breath_rate_bpm:.1f} bpm | HR {event.heart_rate_bpm or "n/a"} | EMG {event.emg_tension if event.emg_tension is not None else "n/a"}</div><div class="wave" style="transform: scaleX({wave_scale:.2f});"></div></div>
  <div class="cell baseline"><span class="pill {_action_class(row.baseline.action)}">{_display_action(row.baseline.action)}</span><div class="prob">p={row.baseline.end_of_turn_probability:.2f}<br>{html.escape(row.baseline.reason)}</div></div>
  <div class="cell"><span class="pill {_action_class(row.physiology.action)}">{_display_action(row.physiology.action)}</span><div class="prob">p={row.physiology.end_of_turn_probability:.2f}<br>{html.escape(row.physiology.reason)}</div></div>
</div>"""


def _display_action(action: str) -> str:
    if action == "ASK_SHORT_CLARIFYING_QUESTION":
        return "ASK CLARIFY"
    return action


def _json_payload(metrics: list[PolicyMetrics]) -> dict[str, object]:
    return {"metrics": [metric.__dict__ for metric in metrics]}
