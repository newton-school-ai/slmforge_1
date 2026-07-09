from __future__ import annotations

import random

from typing import TypedDict

from datasets import Dataset, DatasetDict

from slmforge.data.sources.base import Record
from slmforge.data.sources.registry import get_source


class SourceConfig(TypedDict, total=False):
    """Configuration for a dataset source."""

    type: str
    path: str
    id: str
    generator: str
    size: int
    seed: int


class DatasetBuilder:
    """Build deterministic train/validation/evaluation datasets."""

    DEFAULT_SEED = 42

    TRAIN_RATIO = 0.8
    VAL_RATIO = 0.1
    EVAL_RATIO = 0.1

    def build(
        self,
        sources: list[SourceConfig],
        seed: int = DEFAULT_SEED,
    ) -> DatasetDict:
        """Build a DatasetDict from the provided sources.

        Args:
            sources: Source configurations.
            seed: Random seed used for deterministic splitting.

        Returns:
            DatasetDict containing train, val and eval splits.

        Raises:
            ValueError: If no sources are provided or records are invalid.
        """
        if not sources:
            raise ValueError("At least one source must be provided.")

        records = self._collect_records(sources)
        self._validate_records(records)

        return self._split_records(records, seed)

    def _collect_records(
        self,
        sources: list[SourceConfig],
    ) -> list[Record]:
        """Collect normalized records from every configured source."""

        records: list[Record] = []

        for source in sources:
            source_type = source.get("type")

            if not source_type:
                raise ValueError("Every source must define a 'type'.")

            config = {
                key: value
                for key, value in source.items()
                if key != "type"
            }

            adapter = get_source(source_type, **config)

            records.extend(adapter.iter_records())

        return records

    def _validate_records(
        self,
        records: list[Record],
    ) -> None:
        """Validate collected records before dataset creation."""

        if not records:
            raise ValueError("No records were collected from the provided sources.")

        required_fields = {"id", "text", "metadata"}

        for index, record in enumerate(records):
            missing = required_fields - record.keys()

            if missing:
                raise ValueError(
                    f"Record at index {index} is missing required fields: {sorted(missing)}"
                )

            if not isinstance(record["id"], str):
                raise ValueError(
                    f"Record at index {index} has a non-string 'id'."
                )

            if not isinstance(record["text"], str):
                raise ValueError(
                    f"Record at index {index} has a non-string 'text'."
                )

            if not isinstance(record["metadata"], dict):
                raise ValueError(
                    f"Record at index {index} has invalid metadata."
                )

            if not record["text"].strip():
                raise ValueError(
                    f"Record at index {index} contains empty text."
                )

    def _split_records(
        self,
        records: list[Record],
        seed: int,
    ) -> DatasetDict:
        """Split records into deterministic train/val/eval datasets."""

        shuffled = list(records)
        random.Random(seed).shuffle(shuffled)

        total = len(shuffled)

        train_size = int(total * self.TRAIN_RATIO)
        val_size = int(total * self.VAL_RATIO)
        eval_size = total - train_size - val_size

        assert train_size + val_size + eval_size == total

        train_records = shuffled[:train_size]
        val_records = shuffled[
            train_size : train_size + val_size
        ]
        eval_records = shuffled[
            train_size + val_size :
        ]

        return DatasetDict(
            {
                "train": Dataset.from_list(train_records),
                "val": Dataset.from_list(val_records),
                "eval": Dataset.from_list(eval_records),
            }
        )
