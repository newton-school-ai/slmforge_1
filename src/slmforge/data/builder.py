from __future__ import annotations

import random

from typing import Any, Iterable

from datasets import Dataset, DatasetDict

from slmforge.data.sources.base import Record, Source


class DatasetBuilder:
    """Build deterministic dataset splits from one or more sources."""

    DEFAULT_SEED = 42

    @classmethod
    def build(cls, sources: Iterable[Source], seed: int = DEFAULT_SEED) -> DatasetDict:
        """Build train/val/eval datasets from the provided sources.

        Args:
            sources: Iterable of source adapters implementing Source.
            seed: Seed used to shuffle records before splitting.

        Returns:
            DatasetDict: A dataset dict with `train`, `val`, and `eval` splits.
        """
        records = []
        for source in sources:
            source_metadata = cls._normalize_source_metadata(source.metadata())
            for record in source.iter_records():
                records.append(cls._normalize_record(record, source_metadata))

        base_dataset = Dataset.from_list(records)
        return cls._split_dataset(base_dataset, seed)

    @staticmethod
    def _normalize_source_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": metadata.get("type", "unknown"),
            "identifier": metadata.get("id")
            or metadata.get("dataset_id")
            or metadata.get("path")
            or metadata.get("generator")
            or "unknown",
            "size": metadata.get("size"),
            "license": metadata.get("license") or metadata.get("licence") or "unknown",
            **metadata,
        }

    @staticmethod
    def _normalize_record(record: Record, source_metadata: dict[str, Any]) -> dict[str, Any]:
        normalized_metadata = dict(record.get("metadata", {}))
        normalized_metadata["source"] = source_metadata

        return {
            "id": str(record["id"]),
            "text": str(record["text"]),
            "metadata": normalized_metadata,
        }

    @classmethod
    def _split_dataset(cls, dataset: Dataset, seed: int) -> DatasetDict:
        total = len(dataset)
        indices = list(range(total))
        random.Random(seed).shuffle(indices)

        eval_size = total // 10
        val_size = total // 10
        train_size = total - val_size - eval_size

        train_indices = indices[:train_size]
        val_indices = indices[train_size : train_size + val_size]
        eval_indices = indices[train_size + val_size :]

        return DatasetDict(
            {
                "train": dataset.select(train_indices),
                "val": dataset.select(val_indices),
                "eval": dataset.select(eval_indices),
            }
        )
