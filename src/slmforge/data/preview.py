from __future__ import annotations

from typing import Iterable

from slmforge.data.ingest import IngestError, Record, open_stream


def first_n(source: str | object, n: int = 5) -> list[Record]:
    """Return the first N normalized records from a data source."""
    if n <= 0:
        return []

    records: list[Record] = []
    try:
        stream = open_stream(source)
        for record in stream:
            records.append(record)
            if len(records) >= n:
                break
    except IngestError as exc:
        raise

    return records
