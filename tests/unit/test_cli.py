"""Tests for CLI --task, --base, --template flags."""

from __future__ import annotations

from unittest.mock import patch

from typer.testing import CliRunner

from slmforge.cli.main import (
    _VALID_TASK_TYPES,
    _VALID_TEMPLATES,
    _validate_base_model,
    _validate_override,
    app,
)

runner = CliRunner()


# ---------------------------------------------------------------------------
# Unit tests for validation helpers
# ---------------------------------------------------------------------------


def test_validate_override_valid() -> None:
    _validate_override("classification", _VALID_TASK_TYPES, "task", "task type")
    _validate_override("phi3", _VALID_TEMPLATES, "template", "template format")
    _validate_override(None, _VALID_TASK_TYPES, "task", "task type")


def test_validate_override_invalid() -> None:
    result = runner.invoke(
        app,
        ["build", "--task", "invalid_type", "--auto"],
    )
    assert result.exit_code != 0
    assert "invalid_type" in result.stderr


def test_validate_base_model_valid() -> None:
    _validate_base_model(None)
    _validate_base_model("auto")
    _validate_base_model("microsoft/Phi-3-mini-4k-instruct")


def test_validate_base_model_invalid() -> None:
    result = runner.invoke(
        app,
        ["build", "--base", "not-a-valid-model-id", "--auto"],
    )
    assert result.exit_code != 0
    assert "not-a-valid-model-id" in result.stderr


# ---------------------------------------------------------------------------
# Integration tests via CliRunner (with _post_build mocked)
# ---------------------------------------------------------------------------


@patch("slmforge.cli.main._post_build")
def test_build_defaults(mock_post_build) -> None:
    mock_post_build.return_value = {
        "build_id": "build_test_001",
        "status": "queued",
        "task_type": "auto",
        "base_model": "auto",
        "template": "phi3",
    }
    result = runner.invoke(app, ["build", "--auto"])
    assert result.exit_code == 0
    assert "build_test_001" in result.stdout


@patch("slmforge.cli.main._post_build")
def test_build_task_override(mock_post_build) -> None:
    mock_post_build.return_value = {
        "build_id": "build_test_001",
        "status": "queued",
        "task_type": "classification",
        "base_model": "auto",
        "template": "phi3",
    }
    result = runner.invoke(app, ["build", "--task", "classification", "--auto"])
    assert result.exit_code == 0
    assert "classification" in result.stdout


@patch("slmforge.cli.main._post_build")
def test_build_template_override(mock_post_build) -> None:
    mock_post_build.return_value = {
        "build_id": "build_test_001",
        "status": "queued",
        "task_type": "auto",
        "base_model": "auto",
        "template": "llama3.1",
    }
    result = runner.invoke(app, ["build", "--template", "llama3.1", "--auto"])
    assert result.exit_code == 0
    assert "llama3.1" in result.stdout


@patch("slmforge.cli.main._post_build")
def test_build_base_override(mock_post_build) -> None:
    mock_post_build.return_value = {
        "build_id": "build_test_001",
        "status": "queued",
        "task_type": "auto",
        "base_model": "microsoft/Phi-3-mini-4k-instruct",
        "template": "phi3",
    }
    result = runner.invoke(
        app,
        ["build", "--base", "microsoft/Phi-3-mini-4k-instruct", "--auto"],
    )
    assert result.exit_code == 0
    assert "Phi-3-mini-4k-instruct" in result.stdout


@patch("slmforge.cli.main._post_build")
def test_build_all_overrides(mock_post_build) -> None:
    mock_post_build.return_value = {
        "build_id": "build_test_001",
        "status": "queued",
        "task_type": "qa",
        "base_model": "meta-llama/Llama-3.1-8B-Instruct",
        "template": "llama3.1",
    }
    result = runner.invoke(
        app,
        [
            "build",
            "--task",
            "qa",
            "--base",
            "meta-llama/Llama-3.1-8B-Instruct",
            "--template",
            "llama3.1",
            "--auto",
        ],
    )
    assert result.exit_code == 0
    assert "qa" in result.stdout
    assert "llama3.1" in result.stdout
    assert "Llama-3.1-8B-Instruct" in result.stdout


def test_build_invalid_task() -> None:
    result = runner.invoke(app, ["build", "--task", "bogus", "--auto"])
    assert result.exit_code != 0
    assert "bogus" in result.stderr
    assert "classification" in result.stderr


def test_build_invalid_template() -> None:
    result = runner.invoke(app, ["build", "--template", "bogus", "--auto"])
    assert result.exit_code != 0
    assert "bogus" in result.stderr
    assert "phi3" in result.stderr


def test_build_invalid_base() -> None:
    result = runner.invoke(app, ["build", "--base", "no-slash", "--auto"])
    assert result.exit_code != 0
    assert "no-slash" in result.stderr
    assert "HuggingFace" in result.stderr
