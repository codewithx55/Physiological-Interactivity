"""BLE heart-rate adapter placeholder."""

from __future__ import annotations


class HeartRateBleAdapter:
    """Live adapter boundary for optional BLE Heart Rate Profile devices."""

    def connect(self) -> None:
        raise RuntimeError(
            "BLE heart-rate live mode is not configured. The simulator provides "
            "optional synthetic heart-rate samples."
        )
