from __future__ import annotations

from pathlib import Path

from datasets import load_dataset

CACHE_DIR = Path("data/cache")


def _normalize_dataset_id(dataset_id: str) -> str:
    return dataset_id.replace("/", "_")


def prefetch(
    dataset_id: str,
    split: str = "train",
    cache_dir: Path = CACHE_DIR,
    card_path: Path = Path("data/dataset_card.md"),
) -> Path:
    """Download and cache a HuggingFace dataset, returning the cache path.

    Args:
        dataset_id: HuggingFace dataset identifier.
        split: Dataset split to cache.
        cache_dir: Base cache directory.
        card_path: Path to write dataset card metadata.

    Returns:
        Path: The dataset cache directory.
    """
    cache_dir = Path(cache_dir)
    target_dir = cache_dir / _normalize_dataset_id(dataset_id)
    target_dir.mkdir(parents=True, exist_ok=True)

    marker = target_dir / ".done"
    if marker.exists():
        return target_dir

    ds = load_dataset(dataset_id, split=split, cache_dir=str(target_dir))
    license_info = getattr(ds.info, "license", None) or "unknown"
    size = len(ds)

    card_dir = card_path.parent
    card_dir.mkdir(parents=True, exist_ok=True)
    with card_path.open("w", encoding="utf-8") as card_file:
        card_file.write("# Dataset Card\n\n")
        card_file.write("## Prefetched Dataset\n\n")
        card_file.write(f"- dataset_id: {dataset_id}\n")
        card_file.write(f"- split: {split}\n")
        card_file.write(f"- cache_path: {target_dir}\n")
        card_file.write(f"- licence: {license_info}\n")
        card_file.write(f"- size: {size}\n")

    marker.touch()
    return target_dir
