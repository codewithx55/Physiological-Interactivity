"""Vernier Go Direct Respiration Belt adapter placeholder.

The demo is simulator-first. This module defines the boundary for live data
without making the lab depend on a Vernier SDK or BLE stack.
"""

from __future__ import annotations


class VernierRespirationAdapter:
    """Live adapter boundary for Vernier Go Direct respiration data."""

    def connect(self) -> None:
        raise RuntimeError(
            "Vernier live mode is not configured. Run simulator mode now; connect "
            "this adapter to Vernier Go Direct SDK/BLE respiration samples later."
        )
