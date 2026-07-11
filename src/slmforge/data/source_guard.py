"""Runtime validation for source configurations.

This module implements the first layer of defence against invalid or
restricted data source configurations before source adapters are created.
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from slmforge.data.sources.registry import SOURCE_REGISTRY


class SourceConfig(TypedDict, total=False):
    """Configuration for validating a source before adapter creation."""

    type: str
    path: str
    root: str
    directory: str


FORBIDDEN_PATH_COMPONENTS: frozenset[str] = frozenset({"_internal"})

PATH_FIELDS: tuple[str, ...] = (
    "path",
    "root",
    "directory",
)


def _validate_source_type(source_type: str | None) -> None:
    """Validate that the source type is registered."""

    if not source_type:
        raise ValueError("Source configuration must include a non-empty 'type' field.")

    normalized = source_type.lower()

    if normalized not in SOURCE_REGISTRY:
        valid = ", ".join(sorted(SOURCE_REGISTRY))
        raise ValueError(
            f"Unknown source type '{source_type}'. " f"Registered source types: {valid}."
        )


def _validate_paths(config: SourceConfig) -> None:
    """Reject references to protected internal paths."""

    for field in PATH_FIELDS:
        value = config.get(field)

        if not isinstance(value, str):
            continue

        parts = Path(value).parts

        if FORBIDDEN_PATH_COMPONENTS.intersection(parts):
            raise ValueError(
                f"Source field '{field}' references protected internal path '{value}'."
            )


def validate(config: SourceConfig) -> None:
    """Validate a source configuration before creating a source adapter."""

    _validate_source_type(config.get("type"))
    _validate_paths(config)
