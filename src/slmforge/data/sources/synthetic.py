from __future__ import annotations

from typing import Any, Dict, Iterator

from slmforge.data.sources.base import Record, Source


class SyntheticSource(Source):
    """Source adapter for synthetic/generated datasets."""

    def __init__(
        self,
        generator: str,
        size: int = 10,
        seed: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the synthetic data source.

        Args:
            generator: The name or path of the generator to use.
            size: The number of records to generate.
            seed: The random seed for reproducibility.
            **kwargs: Additional options.
        """
        self.generator = generator
        self.size = size
        self.seed = seed
        self.kwargs = kwargs

    def iter_records(self) -> Iterator[Record]:
        """Yield synthetic records matching the unified record format."""
        for i in range(self.size):
            yield {
                "id": f"synthetic_{self.generator}_{i}",
                "text": f"Synthetic text sample {i} generated using {self.generator}.",
                "metadata": {
                    "generator": self.generator,
                    "index": i,
                    "seed": self.seed,
                },
            }

    def metadata(self) -> Dict[str, Any]:
        """Return metadata for the synthetic source."""
        return {
            "type": "synthetic",
            "generator": self.generator,
            "size": self.size,
            "seed": self.seed,
            **self.kwargs,
        }
