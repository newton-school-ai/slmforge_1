from __future__ import annotations

import pytest

from datasets import DatasetDict

from slmforge.data.builder import DatasetBuilder
from slmforge.data.card import render_dataset_card


def sample_sources():
    return [
        {
            "type": "synthetic",
            "generator": "feedback_summariser",
            "size": 10,
            "seed": 42,
        }
    ]


def test_build_returns_dataset_dict():
    builder = DatasetBuilder()

    dataset = builder.build(sample_sources())

    assert isinstance(dataset, DatasetDict)
    assert set(dataset.keys()) == {"train", "val", "eval"}


def test_same_seed_produces_same_split():
    builder = DatasetBuilder()

    first = builder.build(sample_sources(), seed=42)
    second = builder.build(sample_sources(), seed=42)

    assert list(first["train"]["id"]) == list(second["train"]["id"])
    assert list(first["val"]["id"]) == list(second["val"]["id"])
    assert list(first["eval"]["id"]) == list(second["eval"]["id"])


def test_different_seed_changes_order():
    builder = DatasetBuilder()

    first = builder.build(sample_sources(), seed=42)
    second = builder.build(sample_sources(), seed=7)

    assert list(first["train"]["id"]) != list(second["train"]["id"])


def test_empty_sources_raise_value_error():
    builder = DatasetBuilder()

    with pytest.raises(ValueError):
        builder.build([])


def test_no_overlap_between_train_and_eval():
    builder = DatasetBuilder()

    dataset = builder.build(sample_sources())

    train_ids = set(dataset["train"]["id"])
    eval_ids = set(dataset["eval"]["id"])

    assert train_ids.isdisjoint(eval_ids)


def test_split_sizes():
    builder = DatasetBuilder()

    dataset = builder.build(sample_sources())

    assert len(dataset["train"]) == 8
    assert len(dataset["val"]) == 1
    assert len(dataset["eval"]) == 1


def test_dataset_card_contains_summary():
    builder = DatasetBuilder()

    dataset = builder.build(sample_sources())

    card = render_dataset_card(sample_sources(), dataset, seed=42)

    assert "# Dataset Card" in card
    assert "## Summary" in card
    assert "Seed: 42" in card
    assert "Total Records: 10" in card


def test_dataset_card_contains_sources():
    builder = DatasetBuilder()

    dataset = builder.build(sample_sources())

    card = render_dataset_card(sample_sources(), dataset, seed=42)

    assert "feedback_summariser" in card
    assert "synthetic" in card


def test_dataset_card_contains_notes():
    builder = DatasetBuilder()

    dataset = builder.build(sample_sources())

    card = render_dataset_card(sample_sources(), dataset, seed=42)

    assert "deterministic" in card.lower()
    assert "reproducibility" in card.lower()
