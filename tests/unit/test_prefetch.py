from __future__ import annotations

import logging

from unittest.mock import MagicMock, patch

import pytest

from typer.testing import CliRunner

from slmforge.cli.main import app
from slmforge.data.prefetch import prefetch


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Fixture to patch CACHE_DIR to a temporary path during tests."""
    with patch("slmforge.data.prefetch.CACHE_DIR", tmp_path):
        yield tmp_path


def test_prefetch_fresh_download(temp_cache_dir) -> None:
    # Arrange
    dataset_id = "samsum"
    split = "train"

    mock_dataset = MagicMock()
    mock_dataset.info = MagicMock()
    mock_dataset.info.license = "Apache-2.0"
    mock_dataset.__len__.return_value = 14732
    mock_dataset.save_to_disk = MagicMock()

    with patch("datasets.load_dataset", return_value=mock_dataset) as mock_load:
        # Act
        dest_dir = prefetch(dataset_id, split=split, cache_dir=temp_cache_dir)

        # Assert
        expected_dir = temp_cache_dir / "samsum"
        assert dest_dir == expected_dir
        assert expected_dir.exists()

        mock_load.assert_called_once_with(
            "knkarthick/samsum",
            split=split,
            cache_dir=str(expected_dir),
        )
        mock_dataset.save_to_disk.assert_called_once_with(str(expected_dir))

        # Check marker file
        assert (expected_dir / ".done").exists()

        # Check LICENCE_INFO.md contents
        licence_file = expected_dir / "LICENCE_INFO.md"
        assert licence_file.exists()
        content = licence_file.read_text(encoding="utf-8")
        assert "# samsum" in content
        assert "- Licence: Apache-2.0" in content
        assert "- Size: 14732 records" in content
        assert "- Split: train" in content


def test_prefetch_already_cached(temp_cache_dir, caplog) -> None:
    # Arrange
    dataset_id = "samsum"
    dest_dir = temp_cache_dir / "samsum"
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / ".done").touch()

    # Act
    with patch("datasets.load_from_disk") as mock_load_from_disk:
        caplog.set_level(logging.INFO)

        result_dir = prefetch(dataset_id, cache_dir=temp_cache_dir)

        assert result_dir == dest_dir
        mock_load_from_disk.assert_called_once()
        assert "already cached" in caplog.text


def test_prefetch_uses_samsum_alias(temp_cache_dir) -> None:
    mock_dataset = MagicMock()
    mock_dataset.info = MagicMock()
    mock_dataset.info.license = "Apache-2.0"
    mock_dataset.__len__.return_value = 14731
    mock_dataset.save_to_disk = MagicMock()

    with patch("datasets.load_dataset", return_value=mock_dataset) as mock_load:
        prefetch("samsum", cache_dir=temp_cache_dir)

        mock_load.assert_called_once_with(
            "knkarthick/samsum",
            split="train",
            cache_dir=str(temp_cache_dir / "samsum"),
        )


def test_prefetch_dataset_id_slash_replacement(temp_cache_dir) -> None:
    # Arrange
    dataset_id = "glue/sst2"
    split = "validation"

    mock_dataset = MagicMock()
    mock_dataset.info = MagicMock()
    mock_dataset.info.license = None  # None should default to Unknown
    mock_dataset.__len__.return_value = 872
    mock_dataset.save_to_disk = MagicMock()

    with patch("datasets.load_dataset", return_value=mock_dataset) as mock_load:
        # Act
        dest_dir = prefetch(dataset_id, split=split, cache_dir=temp_cache_dir)

        # Assert
        expected_dir = temp_cache_dir / "glue_sst2"
        assert dest_dir == expected_dir
        assert expected_dir.exists()

        mock_load.assert_called_once_with(
            dataset_id,
            split=split,
            cache_dir=str(expected_dir),
        )
        assert (expected_dir / ".done").exists()

        licence_file = expected_dir / "LICENCE_INFO.md"
        assert licence_file.exists()
        content = licence_file.read_text(encoding="utf-8")
        assert "# glue_sst2" in content
        assert "- Licence: Unknown" in content
        assert "- Size: 872 records" in content
        assert "- Split: validation" in content


def test_prefetch_download_failure_cleanup(temp_cache_dir) -> None:
    # Arrange
    dataset_id = "nonexistent/dataset"

    with patch("datasets.load_dataset", side_effect=ValueError("Dataset not found")):
        # Act & Assert
        with pytest.raises(ValueError, match="Dataset not found"):
            prefetch(dataset_id, cache_dir=temp_cache_dir)

        expected_dir = temp_cache_dir / "nonexistent_dataset"
        # Directory should have been cleaned up if empty
        assert not expected_dir.exists()


def test_cli_prefetch_success(temp_cache_dir) -> None:
    # Arrange
    runner = CliRunner()
    dataset_id = "samsum"

    mock_dataset = MagicMock()
    mock_dataset.info = MagicMock()
    mock_dataset.info.license = "Apache-2.0"
    mock_dataset.__len__.return_value = 100
    mock_dataset.save_to_disk = MagicMock()

    with patch("datasets.load_dataset", return_value=mock_dataset):
        # Act
        result = runner.invoke(app, ["data", "prefetch", dataset_id])

        # Assert
        assert result.exit_code == 0
        assert f"Cached at: {temp_cache_dir}/{dataset_id}" in result.stdout.strip()


def test_cli_prefetch_already_cached(temp_cache_dir, caplog) -> None:
    # Arrange
    runner = CliRunner()
    dataset_id = "samsum"
    dest_dir = temp_cache_dir / "samsum"
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / ".done").touch()

    with (
        patch("datasets.load_from_disk") as mock_load_from_disk,
        patch("datasets.load_dataset") as mock_load_dataset,
    ):
        caplog.set_level(logging.INFO)

        # Act
        result = runner.invoke(app, ["data", "prefetch", dataset_id])

        # Assert
        assert result.exit_code == 0
        mock_load_from_disk.assert_called_once_with(str(dest_dir))
        mock_load_dataset.assert_not_called()
        assert "already cached" in caplog.text
        assert f"Cached at: {temp_cache_dir}/{dataset_id}" in result.stdout


def test_cli_prefetch_failure(temp_cache_dir) -> None:
    # Arrange
    runner = CliRunner()
    dataset_id = "invalid"

    with patch("datasets.load_dataset", side_effect=Exception("Failed to download")):
        # Act
        result = runner.invoke(app, ["data", "prefetch", dataset_id])

        # Assert
        assert result.exit_code == 1
        assert "Error:" in result.stderr or "Error:" in result.stdout
