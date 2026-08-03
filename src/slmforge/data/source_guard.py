from __future__ import annotations

from slmforge.data.sources.registry import list_source_types

BLOCKED_PATHS = ["_internal/", "internal/", "nst_data/"]


def validate(source_type: str, path: str | None = None) -> bool:
    """Validate a data source before use.

    Args:
        source_type: The source type to validate.
        path: Optional local path for the source.

    Returns:
        True if the source_type and path are allowed.

    Raises:
        ValueError: If the source type is unknown or the path contains blocked patterns.
    """
    if not source_type or not source_type.strip():
        raise ValueError("source_type must be a non-empty string.")

    known = list_source_types()
    if source_type.lower() not in known:
        raise ValueError(f"Unregistered source type: {source_type}. Known types: {known}")

    if path:
        normalized_path = str(path)
        for blocked in BLOCKED_PATHS:
            if blocked in normalized_path:
                raise ValueError(
                    f"Blocked path detected: {path} contains '{blocked}'. "
                    "Internal data must not enter the public repo."
                )

    return True
