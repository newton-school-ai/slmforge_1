"""Curated base-model registry.

The registry holds an opinionated set of supported models.  Any model outside
this list requires an explicit addition to the registry -- it is never accepted
by accident.

Registered models
------------------
<<<<<<< HEAD
| Name                | HF ID                                      | VRAM   | License       |
|---------------------|--------------------------------------------|--------|---------------|
| Phi-3-mini          | microsoft/Phi-3-mini-4k-instruct            | ~6 GB  | MIT           |
| Llama 3.1 8B        | meta-llama/Llama-3.1-8B-Instruct            | ~16 GB | llama3.1      |
| Qwen 2.5 7B         | Qwen/Qwen2.5-7B-Instruct                   | ~16 GB | Apache-2.0    |
| DeepSeek V3 distill | deepseek-ai/DeepSeek-V3-distill             | ~8 GB  | MIT           |

Usage
------
    from slmforge.finetune.registry import list_models, get_model, resolve
=======
| Name                | HF ID                                      | VRAM   | License    |
|---------------------|--------------------------------------------|--------|------------|
| Phi-3-mini          | microsoft/Phi-3-mini-4k-instruct            | ~8 GB  | MIT        |
| Llama 3.1 8B        | meta-llama/Llama-3.1-8B-Instruct            | ~16 GB | llama-3.1  |
| Qwen 2.5 7B         | Qwen/Qwen2.5-7B-Instruct                   | ~16 GB | Apache-2.0 |
| DeepSeek V3 distill | deepseek-ai/DeepSeek-V3-distill             | ~8 GB  | MIT        |

Usage
------
    from slmforge.finetune.registry import list_models, get_base, resolve
>>>>>>> c353c23 (Enhance base model validation and registry integration)

    for model in list_models():
        print(model.name, model.vram_gb)

<<<<<<< HEAD
    cfg = get_model("microsoft/Phi-3-mini-4k-instruct")
=======
    cfg = get_base("phi-3-mini")
>>>>>>> c353c23 (Enhance base model validation and registry integration)
    hf_id = resolve("auto")          # -> default model HF ID
"""

from __future__ import annotations

from dataclasses import dataclass

_DEFAULT_HF_ID = "microsoft/Phi-3-mini-4k-instruct"


@dataclass(frozen=True)
<<<<<<< HEAD
class BaseModel:
=======
class Base:
>>>>>>> c353c23 (Enhance base model validation and registry integration)
    """Metadata for a supported base model.

    Attributes:
        huggingface_id: HuggingFace model identifier.
        name: Human-readable short name.
        default_lora_r: Default LoRA rank.
        default_lora_alpha: Default LoRA alpha.
        vram_gb: Approximate VRAM required in GB.
        license: Model license identifier.
        recommended_task_types: Task types this model is well-suited for.
    """

    huggingface_id: str
    name: str
    default_lora_r: int = 16
    default_lora_alpha: int = 32
    vram_gb: float = 0.0
    license: str = ""
    recommended_task_types: tuple[str, ...] = ()


<<<<<<< HEAD
_REGISTRY: dict[str, BaseModel] = {
    "microsoft/Phi-3-mini-4k-instruct": BaseModel(
        huggingface_id="microsoft/Phi-3-mini-4k-instruct",
        name="Phi-3-mini",
        vram_gb=6.0,
        license="MIT",
        recommended_task_types=("classification", "qa", "instruction"),
    ),
    "meta-llama/Llama-3.1-8B-Instruct": BaseModel(
        huggingface_id="meta-llama/Llama-3.1-8B-Instruct",
        name="Llama 3.1 8B",
        vram_gb=16.0,
        license="llama3.1",
        recommended_task_types=("summarisation", "instruction", "chat"),
    ),
    "Qwen/Qwen2.5-7B-Instruct": BaseModel(
=======
_REGISTRY: dict[str, Base] = {
    "phi-3-mini": Base(
        huggingface_id="microsoft/Phi-3-mini-4k-instruct",
        name="Phi-3-mini",
        vram_gb=8.0,
        license="MIT",
        recommended_task_types=("classification", "instruction", "chat"),
    ),
    "llama-3.1-8b": Base(
        huggingface_id="meta-llama/Llama-3.1-8B-Instruct",
        name="Llama 3.1 8B",
        vram_gb=16.0,
        license="llama-3.1",
        recommended_task_types=("instruction", "chat", "summarisation"),
    ),
    "qwen-2.5-7b": Base(
>>>>>>> c353c23 (Enhance base model validation and registry integration)
        huggingface_id="Qwen/Qwen2.5-7B-Instruct",
        name="Qwen 2.5 7B",
        vram_gb=16.0,
        license="Apache-2.0",
        recommended_task_types=("summarisation", "qa", "instruction"),
    ),
<<<<<<< HEAD
    "deepseek-ai/DeepSeek-V3-distill": BaseModel(
=======
    "deepseek-v3-distill": Base(
>>>>>>> c353c23 (Enhance base model validation and registry integration)
        huggingface_id="deepseek-ai/DeepSeek-V3-distill",
        name="DeepSeek V3 distill",
        vram_gb=8.0,
        license="MIT",
        recommended_task_types=("instruction", "chat"),
    ),
}


<<<<<<< HEAD
def list_models() -> list[BaseModel]:
=======
def list_models() -> list[Base]:
>>>>>>> c353c23 (Enhance base model validation and registry integration)
    """Return all registered base models."""
    return list(_REGISTRY.values())


<<<<<<< HEAD
def get_model(hf_id: str) -> BaseModel:
    """Look up a base model by its HuggingFace ID.

    Raises:
        ValueError: If *hf_id* is not registered.
    """
    if not hf_id:
        raise ValueError("Model ID must be a non-empty string.")
    model = _REGISTRY.get(hf_id)
    if model is None:
        valid = ", ".join(_REGISTRY.keys())
        raise ValueError(f"Unknown model '{hf_id}'. Must be one of: {valid}")
    return model


def is_registered(hf_id: str | None) -> bool:
    """Return True if *hf_id* is in the registry."""
    return hf_id in _REGISTRY if hf_id else False
=======
def get_base(name: str) -> Base:
    """Look up a base model by short name or HuggingFace ID.

    Raises:
        ValueError: If the name is empty or not registered.
    """
    if not name:
        raise ValueError("Model name must be a non-empty string.")
    if name in _REGISTRY:
        return _REGISTRY[name]
    for base in _REGISTRY.values():
        if base.huggingface_id == name:
            return base
    raise ValueError(f"'{name}' not registered; add it deliberately")


def is_registered(name: str | None) -> bool:
    """Return True if *name* is in the registry (by short name or HF ID)."""
    if not name:
        return False
    if name in _REGISTRY:
        return True
    return any(base.huggingface_id == name for base in _REGISTRY.values())
>>>>>>> c353c23 (Enhance base model validation and registry integration)


def resolve(model: str) -> str:
    """Resolve a model string to a HuggingFace ID.

    ``"auto"`` (case-insensitive) returns the default model ID.
    Otherwise validates against the registry.

    Raises:
        ValueError: If the model string is empty or not recognised.
    """
    if not model:
        raise ValueError("Model name must be a non-empty string.")
    if model.lower() == "auto":
        return _DEFAULT_HF_ID
<<<<<<< HEAD
    return get_model(model).huggingface_id
=======
    return get_base(model).huggingface_id
>>>>>>> c353c23 (Enhance base model validation and registry integration)
