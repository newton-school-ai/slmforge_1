from __future__ import annotations

from typing import Any, Dict, Iterator

from slmforge.data.sources.base import Record, Source


class PublicHFSource(Source):
    """Source adapter for public Hugging Face datasets."""

    def __init__(
        self,
        id: str | None = None,
        hf_id: str | None = None,
        split: str = "train",
        **kwargs: Any,
    ) -> None:
        """Initialize the public Hugging Face data source.

        Args:
            id: The Hugging Face dataset ID (e.g. 'cnn_dailymail').
            hf_id: Alternative parameter for Hugging Face dataset ID.
            split: The dataset split to load (e.g., 'train', 'validation').
            **kwargs: Additional parameters.
        """
        self.dataset_id = id or hf_id
        if not self.dataset_id:
            raise ValueError("A dataset ID (id or hf_id) must be provided for PublicHFSource.")
        self.split = split
        self.kwargs = kwargs

    def iter_records(self) -> Iterator[Record]:
        """Yield placeholder records for the public HF dataset.

        In the future, this can be expanded to use the `datasets` library:
            from datasets import load_dataset
            dataset = load_dataset(self.dataset_id, split=self.split)
            for i, row in enumerate(dataset):
                yield {
                    "id": f"public_{self.dataset_id}_{i}",
                    "text": row.get("text") or row.get("document") or "",
                    "metadata": {"row_index": i}
                }
        """
        yield {
            "id": f"public_{self.dataset_id}_0",
            "text": (
                f"Placeholder text for public HF dataset '{self.dataset_id}' (split: {self.split})."
            ),
            "metadata": {
                "dataset_id": self.dataset_id,
                "split": self.split,
                **self.kwargs,
            },
        }

    def metadata(self) -> Dict[str, Any]:
        """Return metadata for the public HF source."""
        return {
            "type": "public",
            "dataset_id": self.dataset_id,
            "split": self.split,
            **self.kwargs,
        }
