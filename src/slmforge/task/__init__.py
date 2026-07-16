"""Task package initialization."""

from __future__ import annotations

from slmforge.task.detector import LOW_CONFIDENCE_THRESHOLD, Detection, detect

__all__ = [
    "detect",
    "Detection",
    "LOW_CONFIDENCE_THRESHOLD",
]
