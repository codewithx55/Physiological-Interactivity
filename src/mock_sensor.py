"""Synthetic breath and heart-like stream for Kenny-facing integration tests."""

from __future__ import annotations

import asyncio
import math
import random
import time
from collections.abc import AsyncIterator

from src.events import BiometricEvent, now_ms


class MockSensor:
    def __init__(self, session_id: str, rate_hz: float) -> None:
        self.session_id = session_id
        self.rate_hz = rate_hz
        self.started = time.monotonic()

    async def events(self) -> AsyncIterator[BiometricEvent]:
        interval = 1.0 / self.rate_hz
        sample = 0
        while True:
            elapsed = time.monotonic() - self.started
            breath_rate = 11.5 + 2.0 * math.sin(elapsed / 18.0)
            breath_phase = (elapsed * breath_rate / 60.0) * math.tau
            respiration = math.sin(breath_phase)
            heart_rate = 78 + 7 * math.sin(elapsed / 25.0) + random.uniform(-1.5, 1.5)
            quality = random.uniform(0.88, 1.0)

            yield BiometricEvent(
                session_id=self.session_id,
                device="mock",
                timestamp_ms=now_ms(),
                signal="respiration_force",
                value=round(respiration, 4),
                unit="arbitrary",
                quality=round(quality, 3),
            )
            if sample % max(1, int(self.rate_hz)) == 0:
                yield BiometricEvent(
                    session_id=self.session_id,
                    device="mock",
                    timestamp_ms=now_ms(),
                    signal="respiration_rate",
                    value=round(breath_rate, 2),
                    unit="bpm",
                    quality=round(quality, 3),
                )
                yield BiometricEvent(
                    session_id=self.session_id,
                    device="mock",
                    timestamp_ms=now_ms(),
                    signal="heart_rate",
                    value=round(heart_rate, 2),
                    unit="bpm",
                    quality=round(quality, 3),
                )
            sample += 1
            await asyncio.sleep(interval)
