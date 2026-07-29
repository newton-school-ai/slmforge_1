"""Tests for the curated base-model registry."""

from __future__ import annotations

import pytest

from slmforge.finetune.registry import (
    _DEFAULT_HF_ID,
    _REGISTRY,
    get_model,
    is_registered,
    list_models,
    resolve,
)


def test_four_models_registered() -> None:
    assert len(list_models()) == 4


def test_all_have_hf_id() -> None:
    for model in list_models():
        assert model.huggingface_id, f"{model.name} missing huggingface_id"


def test_all_have_positive_vram() -> None:
    for model in list_models():
        assert model.vram_gb > 0, f"{model.name} has vram_gb <= 0"


def test_all_have_name() -> None:
    for model in list_models():
        assert model.name, f"{model.huggingface_id} missing name"


def test_get_model_phi3() -> None:
    model = get_model("microsoft/Phi-3-mini-4k-instruct")
    assert model.name == "Phi-3-mini"
    assert model.vram_gb == 6.0
    assert model.license == "MIT"


def test_get_model_llama() -> None:
    model = get_model("meta-llama/Llama-3.1-8B-Instruct")
    assert model.name == "Llama 3.1 8B"
    assert model.vram_gb == 16.0


def test_get_model_qwen() -> None:
    model = get_model("Qwen/Qwen2.5-7B-Instruct")
    assert model.name == "Qwen 2.5 7B"


def test_get_model_deepseek() -> None:
    model = get_model("deepseek-ai/DeepSeek-V3-distill")
    assert model.name == "DeepSeek V3 distill"


def test_get_model_unknown_raises() -> None:
    with pytest.raises(ValueError, match="Unknown model"):
        get_model("nonexistent/model")


def test_get_model_empty_raises() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        get_model("")


def test_is_registered_true() -> None:
    assert is_registered("microsoft/Phi-3-mini-4k-instruct") is True


def test_is_registered_false() -> None:
    assert is_registered("unknown/model") is False


def test_is_registered_none() -> None:
    assert is_registered(None) is False


def test_resolve_auto() -> None:
    assert resolve("auto") == _DEFAULT_HF_ID


def test_resolve_auto_case_insensitive() -> None:
    assert resolve("AUTO") == _DEFAULT_HF_ID


def test_resolve_registered_model() -> None:
    hf_id = "meta-llama/Llama-3.1-8B-Instruct"
    assert resolve(hf_id) == hf_id


def test_resolve_unknown_raises() -> None:
    with pytest.raises(ValueError, match="Unknown model"):
        resolve("some/unknown-model")


def test_resolve_empty_raises() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        resolve("")


def test_default_is_phi3() -> None:
    assert _DEFAULT_HF_ID == "microsoft/Phi-3-mini-4k-instruct"


def test_registry_keys_match_hf_ids() -> None:
    for hf_id, model in _REGISTRY.items():
        assert model.huggingface_id == hf_id


def test_all_models_are_frozen() -> None:
    for model in list_models():
        with pytest.raises(AttributeError):
            model.name = "changed"  # type: ignore[misc]


def test_models_have_recommended_tasks() -> None:
    for model in list_models():
        assert len(model.recommended_task_types) > 0, f"{model.name} has no recommended tasks"
