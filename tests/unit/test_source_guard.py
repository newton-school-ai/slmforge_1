import pytest

from slmforge.data.source_guard import validate


def test_validate_known_source_type() -> None:
    assert validate("synthetic") is True


def test_validate_unknown_source_type_raises() -> None:
    with pytest.raises(ValueError, match="Unregistered source type"):
        validate("magic")


def test_validate_blocked_internal_path_raises() -> None:
    blocked_path = "_internal/data.csv"
    with pytest.raises(ValueError, match="Blocked path detected"):
        validate("local", blocked_path)


def test_validate_blocked_nst_data_path_raises() -> None:
    blocked_path = "data/nst_data/sample.csv"
    with pytest.raises(ValueError, match="Blocked path detected"):
        validate("local", blocked_path)


def test_validate_allowed_path_passes() -> None:
    assert validate("local", "data/sample.csv") is True
