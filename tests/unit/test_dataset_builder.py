from __future__ import annotations

from typing import Any
from typing import Iterator

from datasets import DatasetDict

from slmforge.data.builder import DatasetBuilder
from slmforge.data.card import render_dataset_card
from slmforge.data.sources.base import Record
from slmforge.data.sources.base import Source


class DummySource(Source):
    def __init__(self, source_id: str, size: int, license: str | None = None) -> None:
        self.source_id = source_id
        self.size = size
        self.license = license

    def iter_records(self) -> Iterator[Record]:
        for i in range(self.size):
            yield {
                "id": f"{self.source_id}_{i}",
                "text": f"text-{i}",
                "metadata": {"source_id": self.source_id},
            }

    def metadata(self) -> dict[str, Any]:
        return {
            "type": "dummy",
            "identifier": self.source_id,
            "size": self.size,
            "license": self.license or "MIT",
        }


def test_same_seed_produces_same_splits() -> None:
    source = DummySource("source_a", size=20)
    first = DatasetBuilder.build([source], seed=42)
    second = DatasetBuilder.build([source], seed=42)

    assert list(first["train"]["id"]) == list(second["train"]["id"])
    assert list(first["val"]["id"]) == list(second["val"]["id"])
    assert list(first["eval"]["id"]) == list(second["eval"]["id"])


def test_splits_are_disjoint() -> None:
    source = DummySource("source_a", size=20)
    dataset = DatasetBuilder.build([source], seed=42)

    train_ids = set(dataset["train"]["id"])
    val_ids = set(dataset["val"]["id"])
    eval_ids = set(dataset["eval"]["id"])

    assert train_ids.isdisjoint(val_ids)
    assert train_ids.isdisjoint(eval_ids)
    assert val_ids.isdisjoint(eval_ids)


def test_split_ratios_are_approximate() -> None:
    source = DummySource("source_a", size=20)
    dataset = DatasetBuilder.build([source], seed=42)

    assert len(dataset["train"]) == 16
    assert len(dataset["val"]) == 2
    assert len(dataset["eval"]) == 2


def test_dataset_card_includes_all_sources() -> None:
    sources = [
        {"type": "dummy", "identifier": "source_a", "size": 20, "license": "MIT"},
        {"type": "dummy", "identifier": "source_b", "size": 10, "license": "Apache-2.0"},
    ]
    dataset = DatasetBuilder.build([DummySource("source_a", 20), DummySource("source_b", 10)], seed=42)
    card = render_dataset_card("build123", sources, dataset, schema='{"input": "...", "target": "..."}')

    assert "source_a" in card
    assert "source_b" in card
    assert "MIT" in card
    assert "Apache-2.0" in card
    assert "Train: 80%" in card
    assert "Held-out eval: 10% (seeded, frozen)" in card


def test_rendered_schema_in_card() -> None:
    sources = [{"type": "dummy", "identifier": "source_a", "size": 20, "license": "MIT"}]
    dataset = DatasetBuilder.build([DummySource("source_a", 20)], seed=42)
    card = render_dataset_card("build123", sources, dataset, schema='{"input": "...", "target": "..."}')

    assert "\"input\": \"...\"" in card
    assert "\"target\": \"...\"" in card
