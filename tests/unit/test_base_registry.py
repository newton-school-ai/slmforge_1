"""Tests for the curated base-model registry."""

from __future__ import annotations

import pytest

from slmforge.finetune.registry import (
    _DEFAULT_HF_ID,
    _REGISTRY,
    get_base,
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


def test_get_base_by_short_name_phi3() -> None:
    model = get_base("phi-3-mini")
    assert model.name == "Phi-3-mini"
    assert model.huggingface_id == "microsoft/Phi-3-mini-4k-instruct"
    assert model.vram_gb == 8.0
    assert model.license == "MIT"


def test_get_base_by_hf_id_phi3() -> None:
    model = get_base("microsoft/Phi-3-mini-4k-instruct")
    assert model.name == "Phi-3-mini"


def test_get_base_llama() -> None:
    model = get_base("llama-3.1-8b")
    assert model.name == "Llama 3.1 8B"
    assert model.vram_gb == 16.0
    assert model.license == "llama-3.1"


def test_get_base_qwen() -> None:
    model = get_base("qwen-2.5-7b")
    assert model.name == "Qwen 2.5 7B"


def test_get_base_deepseek() -> None:
    model = get_base("deepseek-v3-distill")
    assert model.name == "DeepSeek V3 distill"


def test_get_base_unknown_raises() -> None:
    with pytest.raises(ValueError, match="not registered; add it deliberately"):
        get_base("nonexistent/model")


def test_get_base_empty_raises() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        get_base("")


def test_is_registered_by_short_name() -> None:
    assert is_registered("phi-3-mini") is True


def test_is_registered_by_hf_id() -> None:
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
    with pytest.raises(ValueError, match="not registered; add it deliberately"):
        resolve("some/unknown-model")


def test_resolve_empty_raises() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        resolve("")


def test_default_is_phi3() -> None:
    assert _DEFAULT_HF_ID == "microsoft/Phi-3-mini-4k-instruct"


def test_registry_keys_are_short_names() -> None:
    for short_name, model in _REGISTRY.items():
        assert model.huggingface_id != short_name
        assert short_name in model.name.lower() or short_name.startswith(
            model.name.split()[0].lower()
        )


def test_all_models_are_frozen() -> None:
    for model in list_models():
        with pytest.raises(AttributeError):
            model.name = "changed"  # type: ignore[misc]


def test_models_have_recommended_tasks() -> None:
    for model in list_models():
        assert len(model.recommended_task_types) > 0, f"{model.name} has no recommended tasks"


def test_phi3_tasks_match_pdf() -> None:
    model = get_base("phi-3-mini")
    assert model.recommended_task_types == ("classification", "instruction", "chat")


def test_llama_tasks_match_pdf() -> None:
    model = get_base("llama-3.1-8b")
    assert model.recommended_task_types == ("instruction", "chat", "summarisation")
