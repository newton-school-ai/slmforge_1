from __future__ import annotations

import random

import datasets

from slmforge.data.card import generate_dataset_card
from slmforge.data.sources.base import Record, Source


class DatasetBuilder:
    """Builder for constructing seeded splits from registered sources.

    Also automatically generates dataset cards.
    """

    def build(
        self,
        sources: list[Source] | Source,
        seed: int = 42,
    ) -> datasets.DatasetDict:
        """Build and split the dataset from the given sources.

        Args:
            sources: A single Source instance or a list of Source instances.
            seed: Seed used for deterministic splitting. Defaults to 42.

        Returns:
            datasets.DatasetDict: A dictionary mapping splits ('train', 'val', 'eval')
                to datasets.Dataset objects. The returned dictionary will also have a
                `dataset_card` attribute containing the generated markdown dataset card.
        """
        if isinstance(sources, Source):
            source_list = [sources]
        else:
            source_list = list(sources)

        # Retrieve and normalize all records from sources while tracking individual sizes
        records: list[Record] = []
        source_sizes: dict[Source, int] = {}
        for source in source_list:
            count = 0
            for record in source.iter_records():
                records.append(record)
                count += 1
            source_sizes[source] = count

        # Seeded deterministic shuffle
        # We copy to avoid mutating the original source iterators' outputs (if reused)
        shuffled_records = list(records)
        rng = random.Random(seed)
        rng.shuffle(shuffled_records)

        # Splitting logic: 80% train, 10% val, 10% eval
        N = len(shuffled_records)
        train_end = int(round(N * 0.8))
        val_end = train_end + int(round(N * 0.1))

        train_records = shuffled_records[:train_end]
        val_records = shuffled_records[train_end:val_end]
        eval_records = shuffled_records[val_end:]

        split_sizes = {
            "train": len(train_records),
            "val": len(val_records),
            "eval": len(eval_records),
        }

        # Create HF Dataset objects
        train_dataset = datasets.Dataset.from_list(train_records)
        val_dataset = datasets.Dataset.from_list(val_records)
        eval_dataset = datasets.Dataset.from_list(eval_records)

        # Assemble the DatasetDict
        dataset_dict = datasets.DatasetDict(
            {
                "train": train_dataset,
                "val": val_dataset,
                "eval": eval_dataset,
            }
        )

        # Generate dataset card automatically
        card = generate_dataset_card(
            sources=source_list,
            split_sizes=split_sizes,
            seed=seed,
            source_sizes=source_sizes,
        )

        # Store generated card dynamically on the DatasetDict
        dataset_dict.dataset_card = card

        return dataset_dict
