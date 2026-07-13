from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from slmforge.data.prefetch import prefetch


def test_prefetch_writes_cache_and_card(tmp_path: Path) -> None:
    dataset_id = "samsum"
    dataset = MagicMock()
    dataset.info.license = "apache-2.0"
    dataset.__len__.return_value = 10

    with patch("slmforge.data.prefetch.load_dataset", return_value=dataset) as load_dataset:
        cache_path = prefetch(
            dataset_id,
            split="train",
            cache_dir=tmp_path / "cache",
            card_path=tmp_path / "dataset_card.md",
        )

    assert cache_path.exists()
    assert (cache_path / ".done").exists()
    assert (tmp_path / "dataset_card.md").exists()
    assert "apache-2.0" in (tmp_path / "dataset_card.md").read_text()
    load_dataset.assert_called_once_with(dataset_id, split="train", cache_dir=str(cache_path))


def test_prefetch_is_no_op_when_cached(tmp_path: Path) -> None:
    dataset_id = "samsum"
    cache_dir = tmp_path / "cache" / dataset_id
    cache_dir.mkdir(parents=True)
    (cache_dir / ".done").write_text("")

    with patch("slmforge.data.prefetch.load_dataset") as load_dataset:
        returned = prefetch(
            dataset_id,
            split="train",
            cache_dir=tmp_path / "cache",
            card_path=tmp_path / "dataset_card.md",
        )

    assert returned == cache_dir
    load_dataset.assert_not_called()
