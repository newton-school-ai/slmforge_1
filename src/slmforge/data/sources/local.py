from __future__ import annotations

import pathlib

from typing import Any, Dict, Iterator

from slmforge.data.sources.base import Record, Source


class LocalSource(Source):
    """Source adapter for local datasets (CSV, JSONL, Parquet, etc.)."""

    def __init__(self, path: str, **kwargs: Any) -> None:
        """Initialize the local data source.

        Args:
            path: Path to the local dataset file.
            **kwargs: Additional options.
        """
        self.path = pathlib.Path(path)
        self.kwargs = kwargs

    def iter_records(self) -> Iterator[Record]:
        """Iterate over records based on the file type extension."""
        suffix = self.path.suffix.lower()
        if suffix == ".jsonl":
            yield from self._iter_jsonl()
        elif suffix == ".csv":
            yield from self._iter_csv()
        elif suffix == ".parquet":
            yield from self._iter_parquet()
        else:
            yield from self._iter_generic()

    def _iter_jsonl(self) -> Iterator[Record]:
        """Parse local JSONL file."""
        yield {
            "id": f"local_{self.path.name}_0",
            "text": f"Placeholder content for local JSONL file at {self.path}.",
            "metadata": {"path": str(self.path), "format": "jsonl", **self.kwargs},
        }

    def _iter_csv(self) -> Iterator[Record]:
        """Parse local CSV file."""
        yield {
            "id": f"local_{self.path.name}_0",
            "text": f"Placeholder content for local CSV file at {self.path}.",
            "metadata": {"path": str(self.path), "format": "csv", **self.kwargs},
        }

    def _iter_parquet(self) -> Iterator[Record]:
        """Parse local Parquet file."""
        yield {
            "id": f"local_{self.path.name}_0",
            "text": f"Placeholder content for local Parquet file at {self.path}.",
            "metadata": {"path": str(self.path), "format": "parquet", **self.kwargs},
        }

    def _iter_generic(self) -> Iterator[Record]:
        """Generic/fallback parser."""
        yield {
            "id": f"local_{self.path.name}_0",
            "text": f"Placeholder content for local file at {self.path}.",
            "metadata": {"path": str(self.path), "format": "generic", **self.kwargs},
        }

    def metadata(self) -> Dict[str, Any]:
        """Return metadata for the local source."""
        return {
            "type": "local",
            "path": str(self.path),
            "suffix": self.path.suffix,
            **self.kwargs,
        }
