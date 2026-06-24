from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class SourceType(str, Enum):
    local = "local"
    public = "public"
    synthetic = "synthetic"
    internal = "internal"


class TaskType(str, Enum):
    classification = "classification"
    summarisation = "summarisation"
    qa = "qa"
    instruction = "instruction"
    chat = "chat"
    auto = "auto"


class Source(BaseModel):
    type: SourceType
    path: Optional[str] = None
    id: Optional[str] = None
    generator: Optional[str] = None
    size: Optional[int] = None
    seed: Optional[int] = None

    @model_validator(mode="after")
    def validate_conditional_fields(self) -> Source:
        if self.type == SourceType.local:
            if not self.path:
                raise ValueError("path is required for local sources")
        elif self.type == SourceType.public:
            if not self.id:
                raise ValueError("id is required for public sources")
        elif self.type == SourceType.synthetic:
            if not self.generator:
                raise ValueError("generator is required for synthetic sources")
        return self


class LoRAConfig(BaseModel):
    r: int = Field(..., description="LoRA rank")
    alpha: int = Field(..., description="LoRA alpha scaling factor")
    dropout: float = Field(..., description="LoRA dropout probability")


class TrainingConfig(BaseModel):
    epochs: int = Field(..., description="Number of training epochs")
    batch_size: int = Field(..., description="Training batch size")
    lr: float = Field(..., description="Learning rate")


class EvalConfig(BaseModel):
    llm_judge: bool = Field(..., description="Whether to use LLM as judge for evaluation")


class BuildRequest(BaseModel):
    sources: List[Source] = Field(..., description="List of dataset sources")
    task_type: TaskType = Field(..., description="Type of task to train for")
    base_model: str = Field(..., description="Base model name or 'auto'")
    lora: LoRAConfig = Field(..., description="LoRA configuration parameters")
    training: TrainingConfig = Field(..., description="Training hyperparameters")
    eval: EvalConfig = Field(..., description="Evaluation configuration parameters")


class BuildResponse(BaseModel):
    build_id: str = Field(..., description="Unique ID for the build")
    status: str = Field(..., description="Current status of the build")
