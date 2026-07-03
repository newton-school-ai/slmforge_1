from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, TypedDict


class Record(TypedDict):
    """Unified record format returned by all source adapters."""
    id: str
    text: str
    metadata: Dict[str, Any]


class Source(ABC):
    """Abstract base class for all data sources in SLMForge."""

    @abstractmethod
    def iter_records(self) -> Iterator[Record]:
        """Iterate over the records from this data source.

        Yields:
            Record: A dictionary containing 'id', 'text', and 'metadata'.
        """
        pass

    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """Retrieve metadata associated with this data source.

        Returns:
            Dict[str, Any]: Metadata dictionary.
        """
        pass
