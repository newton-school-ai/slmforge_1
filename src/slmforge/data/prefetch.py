"""Dataset prefetch utility to cache public HuggingFace datasets locally."""

from __future__ import annotations

import logging

from pathlib import Path

import datasets

logger = logging.getLogger(__name__)

CACHE_DIR = Path("data/cache")
DATASET_ALIASES = {
    "samsum": "knkarthick/samsum",
}


def prefetch(
    dataset_id: str,
    split: str = "train",
    cache_dir: Path = CACHE_DIR,
) -> Path:
    """Download a HuggingFace dataset, cache it locally, and record license/metadata.

    If the dataset is already cached (indicated by a `.done` marker file), this is a no-op.

    Args:
        dataset_id: The HuggingFace dataset identifier (e.g., "samsum", "glue/sst2").
        split: The dataset split to download. Defaults to "train".
        cache_dir: The root directory where datasets are cached. Defaults to CACHE_DIR.

    Returns:
        Path: The absolute or relative path to the cached dataset directory.

    Raises:
        Exception: Propagates any exception raised during dataset loading, saving, or
            writing metadata.
    """
    dataset_name = dataset_id.replace("/", "_")
    resolved_dataset_id = DATASET_ALIASES.get(
        dataset_id,
        dataset_id,
    )
    dest_dir = cache_dir / dataset_name
    done_marker = dest_dir / ".done"
    if done_marker.exists():
        try:
            datasets.load_from_disk(str(dest_dir))
            logger.info("Dataset '%s' already cached at %s", dataset_id, dest_dir)
            return dest_dir
        except Exception:
            logger.warning(
                "Cache for dataset '%s' is invalid. Re-downloading.",
                dataset_id,
            )
            done_marker.unlink(missing_ok=True)

    logger.info("Prefetching dataset '%s' (split: '%s')...", dataset_id, split)
    dest_dir.mkdir(parents=True, exist_ok=True)

    try:
        dataset = datasets.load_dataset(
            resolved_dataset_id,
            split=split,
            cache_dir=str(dest_dir),
        )
    except Exception as e:
        logger.error("Failed to load dataset '%s': %s", dataset_id, e)
        # Clean up directory if empty to avoid leaving stray directories
        if dest_dir.exists() and not any(dest_dir.iterdir()):
            try:
                dest_dir.rmdir()
            except Exception:
                pass
        raise

    try:
        # Save dataset to disk
        dataset.save_to_disk(str(dest_dir))

        # Extract metadata
        license_str = "Unknown"
        if dataset.info and dataset.info.license:
            license_str = dataset.info.license

        size = len(dataset)

        # Write LICENCE_INFO.md
        license_info_path = dest_dir / "LICENCE_INFO.md"
        license_info_content = (
            f"# {dataset_name}\n\n"
            f"- Licence: {license_str}\n"
            f"- Size: {size} records\n"
            f"- Split: {split}\n"
        )
        license_info_path.write_text(license_info_content, encoding="utf-8")

        # Create .done marker file
        done_marker.touch()
        logger.info("Successfully cached dataset '%s' to %s", dataset_id, dest_dir)
    except Exception as e:
        logger.error("Failed to save and document cached dataset '%s': %s", dataset_id, e)
        raise

    return dest_dir
