from __future__ import annotations

from datasets import DatasetDict


def render_dataset_card(
    sources: list[dict],
    dataset: DatasetDict,
    seed: int,
) -> str:
    """Render a Markdown dataset card."""

    train_count = len(dataset["train"])
    val_count = len(dataset["val"])
    eval_count = len(dataset["eval"])
    total_records = train_count + val_count + eval_count

    lines: list[str] = []

    lines.append("# Dataset Card")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Seed: {seed}")
    lines.append(f"- Total Records: {total_records}")
    lines.append(f"- Train Records: {train_count}")
    lines.append(f"- Validation Records: {val_count}")
    lines.append(f"- Evaluation Records: {eval_count}")
    lines.append("")

    lines.append("## Sources")
    lines.append("")
    lines.append("| Type | Identifier | Size | Licence |")
    lines.append("|------|------------|------|----------|")

    for source in sources:
        source_type = source.get("type", "-")

        identifier = (
            source.get("id")
            or source.get("path")
            or source.get("generator")
            or "-"
        )

        size = source.get("size", "-")
        licence = source.get("licence", "-")

        lines.append(
            f"| {source_type} | {identifier} | {size} | {licence} |"
        )

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Dataset splits are deterministic for a given seed.")
    lines.append("- Train, validation, and evaluation splits are mutually exclusive.")
    lines.append("- Source metadata is recorded for reproducibility.")

    return "\n".join(lines)
