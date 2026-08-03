"""SLMForge data ingestion helpers and package namespace."""

from __future__ import annotations

from slmforge.data.builder import DatasetBuilder
from slmforge.data.card import generate_card
from slmforge.data.prefetch import CACHE_DIR, prefetch

__all__ = ["DatasetBuilder", "generate_card", "prefetch", "CACHE_DIR"]
