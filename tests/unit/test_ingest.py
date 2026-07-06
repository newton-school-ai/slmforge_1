from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from slmforge.data.ingest import IngestError, open_stream
from slmforge.data.preview import first_n


def _write_fixture(tmp_path: Path) -> dict[str, Path]:
    jsonl_path = tmp_path / "data.jsonl"
    jsonl_path.write_text(
        "\n".join(
            [json.dumps({"id": "1", "text": "hello", "source": "jsonl"}), json.dumps({"id": "2", "text": "world", "source": "jsonl"})]
        ),
        encoding="utf-8",
    )

    csv_path = tmp_path / "data.csv"
    csv_path.write_text("id,text,source\n1,hello,csv\n2,world,csv\n", encoding="utf-8")

    parquet_path = tmp_path / "data.parquet"
    pd.DataFrame(
        [{"id": "1", "text": "hello", "source": "parquet"}, {"id": "2", "text": "world", "source": "parquet"}]
    ).to_parquet(parquet_path)

    txt_dir = tmp_path / "txt-folder"
    txt_dir.mkdir()
    (txt_dir / "first.txt").write_text("hello from text", encoding="utf-8")
    (txt_dir / "second.txt").write_text("world from text", encoding="utf-8")

    return {
        "jsonl": jsonl_path,
        "csv": csv_path,
        "parquet": parquet_path,
        "txt_folder": txt_dir,
    }


def test_loads_jsonl(tmp_path: Path) -> None:
    paths = _write_fixture(tmp_path)
    records = list(open_stream(paths["jsonl"]))

    assert len(records) == 2
    assert records[0]["text"] == "hello"
    assert records[1]["metadata"]["source"] == "jsonl"


def test_loads_csv(tmp_path: Path) -> None:
    paths = _write_fixture(tmp_path)
    records = list(open_stream(paths["csv"]))

    assert len(records) == 2
    assert records[0]["id"] == "1"
    assert records[0]["metadata"]["source"] == "csv"


def test_loads_parquet(tmp_path: Path) -> None:
    paths = _write_fixture(tmp_path)
    records = list(open_stream(paths["parquet"]))

    assert len(records) == 2
    assert records[1]["text"] == "world"
    assert records[1]["metadata"]["source"] == "parquet"


def test_loads_txt_folder(tmp_path: Path) -> None:
    paths = _write_fixture(tmp_path)
    records = list(open_stream(paths["txt_folder"]))

    assert len(records) == 2
    assert records[0]["id"] == "first"
    assert records[1]["text"] == "world from text"


def test_detects_jsonl_without_extension(tmp_path: Path) -> None:
    paths = _write_fixture(tmp_path)
    renamed = tmp_path / "data"
    paths["jsonl"].rename(renamed)

    records = list(open_stream(renamed))
    assert len(records) == 2
    assert records[0]["metadata"]["source"] == "jsonl"


def test_preview_returns_first_five_records(tmp_path: Path) -> None:
    jsonl_path = tmp_path / "data.jsonl"
    jsonl_path.write_text(
        "\n".join([json.dumps({"id": str(i), "text": f"item {i}"}) for i in range(10)]),
        encoding="utf-8",
    )

    records = first_n(jsonl_path, n=5)
    assert len(records) == 5
    assert records[0]["text"] == "item 0"
    assert records[-1]["text"] == "item 4"
