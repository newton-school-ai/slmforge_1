from __future__ import annotations

from typing import Any, Type

from slmforge.data.sources.base import Source
from slmforge.data.sources.internal import InternalSource
from slmforge.data.sources.local import LocalSource
from slmforge.data.sources.public import PublicHFSource
from slmforge.data.sources.synthetic import SyntheticSource

SOURCE_REGISTRY: dict[str, Type[Source]] = {
    "synthetic": SyntheticSource,
    "public": PublicHFSource,
    "local": LocalSource,
    "internal": InternalSource,
}


def get_source(source_type: str, **kwargs: Any) -> Source:
    """Retrieve and instantiate a source adapter based on the source type.

    Args:
        source_type: The type of data source (e.g., 'synthetic', 'public', 'local', 'internal').
        **kwargs: Configuration arguments passed to the source adapter constructor.

    Returns:
        Source: An instance of the source adapter.

    Raises:
        ValueError: If the source_type is unknown or invalid.
    """
    if not source_type:
        raise ValueError("source_type must be a non-empty string.")

    source_class = SOURCE_REGISTRY.get(source_type.lower())
    if source_class is None:
        valid_types = ", ".join(SOURCE_REGISTRY.keys())
        raise ValueError(
            f"Unknown source type '{source_type}'. Valid source types are: {valid_types}."
        )

    return source_class(**kwargs)
