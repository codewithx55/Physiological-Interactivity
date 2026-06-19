"""Transcript token helpers."""

from __future__ import annotations

from src.sensors.simulator import TimelineEvent


def visible_token(event: TimelineEvent) -> str:
    return event.token if event.token else "(silence)"
