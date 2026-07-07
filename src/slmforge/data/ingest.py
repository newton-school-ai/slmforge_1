from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any
from typing import Generator

import pandas as pd

try:
    import magic
except ImportError:  # pragma: no cover
    magic = None

from slmforge.data.sources.base import Record


class IngestError(Exception):
    """Raised when ingestion cannot detect or load a supported format."""


def detect_format(path: Path) -> str:
    """Detect file type using python-magic and fall back to extension."""
    if not path.exists():
        raise IngestError(f"Path does not exist: {path}")

    mime = None
    if magic is not None:
        try:
            mime = magic.from_file(str(path), mime=True)
        except Exception:
            mime = None

    if mime:
        if "json" in mime:
            return "jsonl"
        if "csv" in mime or "text/plain" in mime:
            return "csv"
        if "parquet" in mime:
            return "parquet"

    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        return "jsonl"
    if suffix == ".csv":
        return "csv"
    if suffix == ".parquet":
        return "parquet"
    if path.is_dir() or suffix == ".txt":
        return "txt-folder"

    if path.is_file():
        try:
            with path.open("r", encoding="utf-8") as file:
                first_line = ""
                for line in file:
                    if line.strip():
                        first_line = line.strip()
                        break
                if first_line:
                    try:
                        json.loads(first_line)
                        return "jsonl"
                    except json.JSONDecodeError:
                        pass
                    if "," in first_line:
                        return "csv"
        except Exception:
            pass

    raise IngestError(
        f"Could not detect ingest format for path: {path} (mime={mime})"
    )


def normalize_record(raw: dict[str, Any], source_id: str | None = None) -> Record:
    """Normalize raw row data into the standard SLMForge Record format."""
    text = raw.get("text") or raw.get("body") or raw.get("content")
    if text is None:
        text = json.dumps(raw, ensure_ascii=False)

    record_id = raw.get("id")
    if record_id is None or str(record_id).strip() == "":
        record_id = source_id or ""

    return {
        "id": str(record_id),
        "text": str(text),
        "metadata": {k: v for k, v in raw.items() if k != "text" and k != "id"},
    }


def read_jsonl(path: Path) -> Generator[Record, None, None]:
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                raw = json.loads(line)
                yield normalize_record(raw, source_id=path.name)


def read_csv(path: Path) -> Generator[Record, None, None]:
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            yield normalize_record(row, source_id=path.name)


def read_parquet(path: Path) -> Generator[Record, None, None]:
    df = pd.read_parquet(path)
    for _, row in df.iterrows():
        yield normalize_record(row.to_dict(), source_id=path.name)


def read_txt_folder(path: Path) -> Generator[Record, None, None]:
    if path.is_file():
        raise IngestError("txt-folder expects a directory of text files.")

    for child in sorted(path.iterdir()):
        if child.is_file() and child.suffix.lower() == ".txt":
            with child.open("r", encoding="utf-8") as file:
                text = file.read().strip()
            yield {
                "id": child.stem,
                "text": text,
                "metadata": {"source_file": str(child.name)},
            }


def open_stream(source: str | Path) -> Generator[Record, None, None]:
    """Open a source path and return normalized records from the detected format."""
    path = Path(source)
    if not path.exists():
        raise IngestError(f"Source not found: {source}")

    fmt = detect_format(path)
    if fmt == "jsonl":
        return read_jsonl(path)
    if fmt == "csv":
        return read_csv(path)
    if fmt == "parquet":
        return read_parquet(path)
    if fmt == "txt-folder":
        return read_txt_folder(path)

    raise IngestError(f"Unsupported ingest format: {fmt}")
