"""Callibri/BrainBit adapter boundary.

This repo intentionally does not fake a vendor SDK import. Install the actual
Callibri/BrainBit Python SDK, then wire discovery, BLE connection, signal
subscription, and event conversion in this file.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from src.events import BiometricEvent


KNOWN_SDK_IMPORTS = ("neurosdk", "brainbit", "callibri")


class CallibriSensor:
    def __init__(self, session_id: str, rate_hz: float) -> None:
        self.session_id = session_id
        self.rate_hz = rate_hz

    async def events(self) -> AsyncIterator[BiometricEvent]:
        sdk_name = self._find_sdk()
        if sdk_name is None:
            raise RuntimeError(
                "Callibri SDK is not installed in this Python environment. "
                "Install the vendor SDK, then implement discovery/subscription in "
                "src/sensors/callibri_sensor.py. For Kenny right now, run "
                "--device mock to validate the stream format."
            )
        raise RuntimeError(
            f"Found possible Callibri SDK import '{sdk_name}', but the real adapter "
            "still needs vendor-specific discovery, BLE connection, signal "
            "subscription, and conversion to BiometricEvent."
        )
        if False:
            yield BiometricEvent(
                session_id=self.session_id,
                device="callibri",
                timestamp_ms=0,
                signal="respiration_force",
                value=0.0,
                unit="arbitrary",
                quality=0.0,
            )

    @staticmethod
    def _find_sdk() -> str | None:
        import importlib.util

        for name in KNOWN_SDK_IMPORTS:
            if importlib.util.find_spec(name):
                return name
        return None
