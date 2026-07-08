from __future__ import annotations

from slmforge.data.sources.base import Source


def generate_dataset_card(
    sources: list[Source],
    split_sizes: dict[str, int],
    seed: int,
    source_sizes: dict[Source, int] | None = None,
) -> str:
    """Generate a markdown dataset card for the given sources and split sizes.

    Args:
        sources: List of source objects.
        split_sizes: Dictionary containing sizes of 'train', 'val', and 'eval' splits.
        seed: The random seed used for splitting.
        source_sizes: Optional mapping from Source to number of records consumed from it.

    Returns:
        str: Markdown dataset card contents.
    """
    lines = [
        "# Dataset Card",
        "",
        "## Sources",
        "",
        "| Type | ID/Path | Size | License |",
        "|------|---------|------|---------|",
    ]

    for source in sources:
        meta = source.metadata()
        source_type = str(meta.get("type", "unknown"))

        # Extract source ID or path based on typical source fields
        source_id = meta.get("path") or meta.get("dataset_id") or meta.get("generator") or "unknown"
        source_id = str(source_id)

        # Get size
        if source_sizes and source in source_sizes:
            size = source_sizes[source]
        else:
            size = meta.get("size")
        size_str = str(size) if size is not None else "unknown"

        # License
        license_str = str(meta.get("license") or meta.get("license_type") or "unknown")

        lines.append(f"| {source_type} | {source_id} | {size_str} | {license_str} |")

    # Add sorted detail lines for all source metadata
    lines.extend(
        [
            "",
            "### Source Metadata Details",
            "",
        ]
    )

    for i, source in enumerate(sources):
        meta = source.metadata()
        source_id = (
            meta.get("path") or meta.get("dataset_id") or meta.get("generator") or f"source_{i}"
        )
        source_id = str(source_id)
        lines.append(f"#### Source: {source_id}")
        for key in sorted(meta.keys()):
            val = meta[key]
            lines.append(f"- **{key}**: {val}")
        lines.append("")

    # Split Information
    lines.extend(
        [
            "## Split Information",
            "",
            f"Train: {split_sizes.get('train', 0)}",
            f"Validation: {split_sizes.get('val', 0)}",
            f"Evaluation: {split_sizes.get('eval', 0)}",
            "",
            "## Seed",
            "",
            str(seed),
            "",  # trailing newline
        ]
    )

    return "\n".join(lines)
