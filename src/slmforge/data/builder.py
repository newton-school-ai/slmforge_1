from __future__ import annotations

import datasets

from slmforge.data.card import generate_card
from slmforge.data.sources.base import Record, Source


class DatasetBuilder:
    """Builder for constructing seeded splits from registered sources.

    Also automatically generates dataset cards.
    """

    DEFAULT_SEED = 42
    DEFAULT_SPLIT = (0.8, 0.1, 0.1)

    @staticmethod
    def build(
        sources: list[Source] | Source,
        split_ratio: tuple = DEFAULT_SPLIT,
        seed: int = DEFAULT_SEED,
    ) -> datasets.DatasetDict:
        """Build and split the dataset from the given sources.

        Args:
            sources: A single Source instance or a list of Source instances.
            split_ratio: A tuple of (train, val, eval) ratio. Defaults to (0.8, 0.1, 0.1).
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

        # Convert to Hugging Face Dataset
        ds = datasets.Dataset.from_list(records)

        # Seeded deterministic shuffle
        ds_shuffled = ds.shuffle(seed=seed)

        # Splitting logic based on split_ratio
        N = len(ds_shuffled)
        train_ratio, val_ratio, eval_ratio = split_ratio

        train_end = int(round(N * train_ratio))
        val_end = train_end + int(round(N * val_ratio))

        train_dataset = ds_shuffled.select(list(range(0, train_end)))
        val_dataset = ds_shuffled.select(list(range(train_end, val_end)))
        eval_dataset = ds_shuffled.select(list(range(val_end, N)))

        split_sizes = {
            "train": len(train_dataset),
            "val": len(val_dataset),
            "eval": len(eval_dataset),
        }

        # Assemble the DatasetDict
        dataset_dict = datasets.DatasetDict(
            {
                "train": train_dataset,
                "val": val_dataset,
                "eval": eval_dataset,
            }
        )

        # Generate dataset card automatically
        card = generate_card(
            sources=source_list,
            split_sizes=split_sizes,
            seed=seed,
            source_sizes=source_sizes,
        )

        # Store generated card dynamically on the DatasetDict
        dataset_dict.dataset_card = card

        return dataset_dict
