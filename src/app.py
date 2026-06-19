"""Run the physiology-aware turn-taking demo."""

from __future__ import annotations

import argparse
import http.server
import socketserver
from pathlib import Path

from src.ui.dashboard import render_dashboard


ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build"
DASHBOARD = BUILD_DIR / "dashboard.html"


class ReusableTcpServer(socketserver.TCPServer):
    allow_reuse_address = True


def run_server(port: int) -> None:
    render_dashboard(DASHBOARD)
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(  # noqa: E731
        *args,
        directory=str(BUILD_DIR),
        **kwargs,
    )
    with ReusableTcpServer(("127.0.0.1", port), handler) as httpd:
        print(f"Dashboard: http://127.0.0.1:{port}/dashboard.html")
        print("Synthetic data only. No raw audio, Tinker call, Slack post, or live sensor connection.")
        httpd.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description="Physiology-aware turn-taking demo runner.")
    parser.add_argument("--mode", choices=["simulator", "vernier"], default="simulator")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--once", action="store_true", help="Render dashboard and exit.")
    args = parser.parse_args()

    if args.mode == "vernier":
        print("Vernier live mode is stubbed. Use --mode simulator for the current demo.")
        return 2

    path = render_dashboard(DASHBOARD)
    print(f"Rendered dashboard: {path}")
    if args.once:
        return 0

    run_server(args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
