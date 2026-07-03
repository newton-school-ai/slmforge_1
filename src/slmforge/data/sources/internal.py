from __future__ import annotations

from typing import Any, Dict, Iterator

from slmforge.data.sources.base import Record, Source


class InternalSource(Source):
    """Internal data source reserved for future development."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize internal source."""
        self.kwargs = kwargs

    def iter_records(self) -> Iterator[Record]:
        """Raise NotImplementedError as internal source is reserved."""
        raise NotImplementedError(
            "The INTERNAL source adapter is reserved for future implementation "
            "and is currently unavailable."
        )

    def metadata(self) -> Dict[str, Any]:
        """Raise NotImplementedError as internal source is reserved."""
        raise NotImplementedError(
            "The INTERNAL source adapter is reserved for future implementation "
            "and is currently unavailable."
        )
