#!/usr/bin/env python3
"""Build a local click-to-watch HTML wrapper for the generated demo video."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
VIDEO = BUILD / "frequency-turn-gate-demo.mp4"
VIEWER = BUILD / "demo-viewer.html"


def main() -> int:
    if not VIDEO.exists():
        print(f"Missing video: {VIDEO}")
        print("Generate it from the film UI before using the viewer.")
        return 2

    VIEWER.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Frequency Turn Gate Demo Video</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: #151514;
      color: #f7f4eb;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      width: min(1120px, calc(100vw - 32px));
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: 24px;
      letter-spacing: 0;
    }}
    p {{
      color: rgba(247, 244, 235, 0.72);
      margin: 0 0 18px;
    }}
    video {{
      width: 100%;
      border-radius: 8px;
      border: 1px solid rgba(247, 244, 235, 0.18);
      box-shadow: 0 24px 80px rgba(0, 0, 0, 0.45);
      background: #000;
    }}
  </style>
</head>
<body>
  <main>
    <h1>Frequency Turn Gate Demo</h1>
    <p>Synthetic Vernier-shaped signal. No real voice, breath, HR, or EMG data recorded.</p>
    <video controls autoplay muted loop playsinline src="{VIDEO.name}"></video>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )
    print(f"Viewer: {VIEWER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
