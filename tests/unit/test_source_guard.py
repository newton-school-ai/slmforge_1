from __future__ import annotations

import pytest

from slmforge.data.source_guard import validate


def test_accepts_valid_local_source():
    validate(
        {
            "type": "local",
            "path": "datasets/train.jsonl",
        }
    )


def test_accepts_valid_public_source():
    validate(
        {
            "type": "public",
            "id": "ag_news",
        }
    )


def test_accepts_valid_synthetic_source():
    validate(
        {
            "type": "synthetic",
            "generator": "demo",
            "size": 10,
        }
    )


def test_rejects_unknown_source_type():
    with pytest.raises(ValueError, match="Unknown source type"):
        validate(
            {
                "type": "unknown",
            }
        )


def test_rejects_missing_source_type():
    with pytest.raises(ValueError, match="type"):
        validate(
            {
                "path": "data/train.jsonl",
            }
        )


def test_rejects_internal_path():
    with pytest.raises(ValueError, match="internal path"):
        validate(
            {
                "type": "local",
                "path": "_internal/private.jsonl",
            }
        )


def test_accepts_uppercase_source_type():
    validate(
        {
            "type": "LOCAL",
            "path": "datasets/train.jsonl",
        }
    )


def test_rejects_nested_internal_path():
    with pytest.raises(ValueError, match="protected internal path"):
        validate(
            {
                "type": "local",
                "path": "datasets/_internal/train.jsonl",
            }
        )


def test_rejects_internal_root():
    with pytest.raises(ValueError, match="protected internal path"):
        validate(
            {
                "type": "local",
                "root": "_internal",
            }
        )


def test_rejects_internal_directory():
    with pytest.raises(ValueError, match="protected internal path"):
        validate(
            {
                "type": "local",
                "directory": "_internal/cache",
            }
        )


def test_rejects_empty_source_type():
    with pytest.raises(ValueError, match="non-empty"):
        validate(
            {
                "type": "",
            }
        )


def test_rejects_none_source_type():
    with pytest.raises(ValueError, match="non-empty"):
        validate(
            {
                "type": None,
            }
        )
