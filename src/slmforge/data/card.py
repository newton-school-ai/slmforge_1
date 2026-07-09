from __future__ import annotations

from typing import Any
from typing import Iterable

from datasets import DatasetDict


def render_dataset_card(
    build_id: str,
    sources: Iterable[dict[str, Any]],
    dataset: DatasetDict,
    schema: str | None = None,
    extra_sections: str | None = None,
) -> str:
    """Render a Markdown dataset card for a build."""
    rows = []
    for source in sources:
        source_type = source.get("type", "unknown")
        identifier = source.get("identifier") or source.get("dataset_id") or source.get("path") or source.get("generator") or "unknown"
        size = source.get("size", "unknown")
        licence = source.get("license") or source.get("licence") or "unknown"
        rows.append(f"| {source_type} | {identifier} | {size} | {licence} |")

    source_table = "\n".join(rows) if rows else "| unknown | unknown | unknown | unknown |"

    if schema:
        schema_section = """```
{schema}
```""".format(schema=schema)
    else:
        schema_section = """```
{"input": "...", "target": "..."}
```"""

    extra = f"\n{extra_sections}\n" if extra_sections else ""

    return """# Dataset Card -- {build_id}

## Sources
| Type | Identifier | Size | Licence |
|------|-----------|------|---------|
{source_table}

## Splits
- Train: 80%
- Val: 10%
- Held-out eval: 10% (seeded, frozen)

## Schema
{schema_section}

## dePII
- Method:
- Manual spot-check sample size:
- Leaks found:

## Known limitations

## Citations
{extra}""".format(
        build_id=build_id,
        source_table=source_table,
        schema_section=schema_section,
        extra=extra,
    )
