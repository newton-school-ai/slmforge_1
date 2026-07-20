"""Task package initialization."""

from __future__ import annotations

from slmforge.task.detector import LOW_CONFIDENCE_THRESHOLD, Detection, detect
from slmforge.task.metrics import Metric, get_metric, get_metrics, register_metric
from slmforge.task.templates import apply_chat_template, render_record, strip_template

__all__ = [
    "detect",
    "Detection",
    "LOW_CONFIDENCE_THRESHOLD",
    "apply_chat_template",
    "render_record",
    "strip_template",
    "get_metric",
    "get_metrics",
    "Metric",
    "register_metric",
]
