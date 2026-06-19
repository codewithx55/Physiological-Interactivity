"""Callibri EMG adapter placeholder for future live muscle-tension cues."""

from __future__ import annotations


class CallibriEmgAdapter:
    """Live adapter boundary for optional Callibri/Calibri EMG data."""

    def connect(self) -> None:
        raise RuntimeError(
            "Callibri EMG live mode is not configured. The current demo uses "
            "synthetic EMG tension values only."
        )
