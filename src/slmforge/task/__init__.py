"""Task package initialization."""

from __future__ import annotations

from slmforge.task.detector import LOW_CONFIDENCE_THRESHOLD, Detection, detect
from slmforge.task.templates import render_record, strip_template

__all__ = [
    "detect",
    "Detection",
    "LOW_CONFIDENCE_THRESHOLD",
    "render_record",
    "strip_template",
]
