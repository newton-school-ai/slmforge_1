from __future__ import annotations

from typing import Iterator

import datasets

from slmforge.data.builder import DatasetBuilder
from slmforge.data.sources.base import Record, Source
from slmforge.data.sources.synthetic import SyntheticSource


class MockSource(Source):
    """A simple MockSource for testing."""

    def __init__(self, records: list[Record], metadata_dict: dict | None = None) -> None:
        self.records = records
        self._metadata = metadata_dict or {"type": "mock", "path": "mock_path"}

    def iter_records(self) -> Iterator[Record]:
        yield from self.records

    def metadata(self) -> dict:
        return self._metadata


def test_dataset_builder_default_seed() -> None:
    # 10. Default seed equals 42
    builder = DatasetBuilder()
    source = SyntheticSource(generator="gen_a", size=10)

    ds_default = builder.build(source)
    ds_42 = builder.build(source, seed=42)

    assert list(ds_default["train"]["id"]) == list(ds_42["train"]["id"])
    assert "Seed\n\n42" in ds_default.dataset_card


def test_dataset_builder_same_seed_identical_splits() -> None:
    # 1. Same seed -> identical splits
    builder = DatasetBuilder()
    source = SyntheticSource(generator="gen_a", size=50)

    ds_1 = builder.build(source, seed=123)
    ds_2 = builder.build(source, seed=123)

    for split in ["train", "val", "eval"]:
        assert list(ds_1[split]["id"]) == list(ds_2[split]["id"])
        assert list(ds_1[split]["text"]) == list(ds_2[split]["text"])


def test_dataset_builder_different_seed_different_splits() -> None:
    # 2. Different seed -> different splits
    builder = DatasetBuilder()
    source = SyntheticSource(generator="gen_a", size=100)

    ds_1 = builder.build(source, seed=42)
    ds_2 = builder.build(source, seed=999)

    any_different = False
    for split in ["train", "val", "eval"]:
        if list(ds_1[split]["id"]) != list(ds_2[split]["id"]):
            any_different = True
            break
    assert any_different, "Different seeds should produce different splits"


def test_dataset_builder_ratios_80_10_10() -> None:
    # 3. Train/val/eval ratios approximately follow 80/10/10
    builder = DatasetBuilder()

    # Test N=100 (exact splits 80, 10, 10)
    source_100 = SyntheticSource(generator="gen_a", size=100)
    ds_100 = builder.build(source_100, seed=42)
    assert len(ds_100["train"]) == 80
    assert len(ds_100["val"]) == 10
    assert len(ds_100["eval"]) == 10

    # Test N=10 (exact splits 8, 1, 1)
    source_10 = SyntheticSource(generator="gen_a", size=10)
    ds_10 = builder.build(source_10, seed=42)
    assert len(ds_10["train"]) == 8
    assert len(ds_10["val"]) == 1
    assert len(ds_10["eval"]) == 1


def test_dataset_builder_no_overlap() -> None:
    # 4, 5, 6. No overlap between splits
    builder = DatasetBuilder()
    source = SyntheticSource(generator="gen_a", size=100)
    ds = builder.build(source, seed=42)

    train_ids = set(ds["train"]["id"])
    val_ids = set(ds["val"]["id"])
    eval_ids = set(ds["eval"]["id"])

    assert train_ids.isdisjoint(val_ids), "Overlap between train and val!"
    assert train_ids.isdisjoint(eval_ids), "Overlap between train and eval!"
    assert val_ids.isdisjoint(eval_ids), "Overlap between val and eval!"
    assert len(train_ids) + len(val_ids) + len(eval_ids) == 100


def test_dataset_builder_empty_source() -> None:
    # 7. Empty source handling
    builder = DatasetBuilder()
    empty_source = MockSource(records=[])
    ds = builder.build(empty_source)

    assert isinstance(ds, datasets.DatasetDict)
    assert len(ds["train"]) == 0
    assert len(ds["val"]) == 0
    assert len(ds["eval"]) == 0


def test_dataset_builder_contains_exactly_splits() -> None:
    # 8. DatasetDict contains exactly: train, val, eval
    builder = DatasetBuilder()
    source = SyntheticSource(generator="gen_a", size=5)
    ds = builder.build(source)

    assert list(ds.keys()) == ["train", "val", "eval"]


def test_dataset_builder_dataset_card_contents() -> None:
    # 9. Dataset card contains: source type, source path/id, size, license
    builder = DatasetBuilder()

    records: list[Record] = [
        {"id": "1", "text": "hello", "metadata": {}},
        {"id": "2", "text": "world", "metadata": {}},
    ]
    source = MockSource(
        records=records,
        metadata_dict={
            "type": "custom_type",
            "path": "custom_path/dataset.csv",
            "license": "Apache-2.0",
        },
    )

    ds = builder.build(source, seed=123)
    card = ds.dataset_card

    assert "# Dataset Card" in card
    assert "custom_type" in card
    assert "custom_path/dataset.csv" in card
    assert "Apache-2.0" in card
    assert "2" in card  # size
    assert "Seed" in card
    assert "123" in card
    assert "Train: 2" in card
    assert "Validation: 0" in card
    assert "Evaluation: 0" in card


def test_dataset_builder_custom_split_ratio() -> None:
    source = SyntheticSource(generator="gen_a", size=10)
    # custom split 70% / 20% / 10%
    ds = DatasetBuilder.build(source, split_ratio=(0.7, 0.2, 0.1), seed=42)
    assert len(ds["train"]) == 7
    assert len(ds["val"]) == 2
    assert len(ds["eval"]) == 1


def test_generate_card_writes_to_file(tmp_path) -> None:
    from slmforge.data.card import generate_card

    source = SyntheticSource(generator="gen_a", size=10)
    output_file = tmp_path / "custom_card.md"

    card_str = generate_card(
        sources=[source],
        split_sizes={"train": 8, "val": 1, "eval": 1},
        seed=42,
        output_path=str(output_file),
    )

    assert output_file.exists()
    file_content = output_file.read_text(encoding="utf-8")
    assert file_content == card_str
    assert "Seed\n\n42" in file_content
