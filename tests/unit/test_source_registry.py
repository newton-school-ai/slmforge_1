import pytest
from slmforge.data.sources.base import Source
from slmforge.data.sources.internal import InternalSource
from slmforge.data.sources.local import LocalSource
from slmforge.data.sources.public import PublicHFSource
from slmforge.data.sources.registry import get_source
from slmforge.data.sources.synthetic import SyntheticSource


def test_registry_resolves_sources() -> None:
    # Test resolving each known source type
    synthetic = get_source("synthetic", generator="test_gen", size=5, seed=42)
    assert isinstance(synthetic, SyntheticSource)
    assert synthetic.generator == "test_gen"
    assert synthetic.size == 5
    assert synthetic.seed == 42

    public_hf = get_source("public", id="cnn_dailymail", split="train")
    assert isinstance(public_hf, PublicHFSource)
    assert public_hf.dataset_id == "cnn_dailymail"
    assert public_hf.split == "train"

    local = get_source("local", path="/tmp/data.jsonl")
    assert isinstance(local, LocalSource)
    assert str(local.path) == "/tmp/data.jsonl"

    internal = get_source("internal")
    assert isinstance(internal, InternalSource)


def test_registry_rejects_unknown_sources() -> None:
    # Test that unknown source type raises ValueError
    with pytest.raises(ValueError) as exc_info:
        get_source("nonexistent_source")
    assert "Unknown source type" in str(exc_info.value)

    # Test empty source type
    with pytest.raises(ValueError) as exc_info:
        get_source("")
    assert "source_type must be a non-empty string" in str(exc_info.value)


def test_internal_source_raises_not_implemented() -> None:
    internal = InternalSource()
    with pytest.raises(NotImplementedError) as exc_info:
        list(internal.iter_records())
    assert "reserved for future implementation" in str(exc_info.value)

    with pytest.raises(NotImplementedError) as exc_info:
        internal.metadata()
    assert "reserved for future implementation" in str(exc_info.value)


def test_adapter_record_shape_and_interface() -> None:
    # Instantiate all valid sources
    sources = [
        get_source("synthetic", generator="test_gen", size=2),
        get_source("public", id="cnn_dailymail"),
        get_source("local", path="data.jsonl"),
    ]

    for source in sources:
        # Check interface and inheritance
        assert isinstance(source, Source)

        # Check metadata interface
        meta = source.metadata()
        assert isinstance(meta, dict)
        assert "type" in meta

        # Check records interface and shape
        records = list(source.iter_records())
        assert len(records) > 0
        for record in records:
            assert isinstance(record, dict)
            assert sorted(record.keys()) == ["id", "metadata", "text"]
            assert isinstance(record["id"], str)
            assert isinstance(record["text"], str)
            assert isinstance(record["metadata"], dict)


def test_local_source_file_extensions() -> None:
    # LocalSource should run without error for different file formats
    csv_source = get_source("local", path="data.csv")
    csv_records = list(csv_source.iter_records())
    assert len(csv_records) == 1
    assert csv_records[0]["metadata"]["format"] == "csv"

    parquet_source = get_source("local", path="data.parquet")
    parquet_records = list(parquet_source.iter_records())
    assert len(parquet_records) == 1
    assert parquet_records[0]["metadata"]["format"] == "parquet"

    generic_source = get_source("local", path="data.txt")
    generic_records = list(generic_source.iter_records())
    assert len(generic_records) == 1
    assert generic_records[0]["metadata"]["format"] == "generic"
