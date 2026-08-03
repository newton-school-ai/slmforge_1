# Supported Base Models (Model Cards)

This document describes the curated, opinionated set of base models supported by SLMForge.
Any model outside this list requires an explicit addition to `src/slmforge/finetune/registry.py`.

---

## 1. Phi-3-mini

- **HuggingFace ID:** `microsoft/Phi-3-mini-4k-instruct`
- **Short Name:** `phi-3-mini`
- **VRAM Footprint:** ~8.0 GB
- **License:** MIT
- **Default LoRA Recipe:**
  - `r`: 16
  - `alpha`: 32
- **Recommended Task Types:** `classification`, `instruction`, `chat`

---

## 2. Llama 3.1 8B Instruct

- **HuggingFace ID:** `meta-llama/Llama-3.1-8B-Instruct`
- **Short Name:** `llama-3.1-8b`
- **VRAM Footprint:** ~16.0 GB
- **License:** llama-3.1
- **Default LoRA Recipe:**
  - `r`: 16
  - `alpha`: 32
- **Recommended Task Types:** `instruction`, `chat`, `summarisation`

---

## 3. Qwen 2.5 7B Instruct

- **HuggingFace ID:** `Qwen/Qwen2.5-7B-Instruct`
- **Short Name:** `qwen-2.5-7b`
- **VRAM Footprint:** ~16.0 GB
- **License:** Apache-2.0
- **Default LoRA Recipe:**
  - `r`: 16
  - `alpha`: 32
- **Recommended Task Types:** `summarisation`, `qa`, `instruction`

---

## 4. DeepSeek V3 Distill

- **HuggingFace ID:** `deepseek-ai/DeepSeek-V3-distill`
- **Short Name:** `deepseek-v3-distill`
- **VRAM Footprint:** ~8.0 GB
- **License:** MIT
- **Default LoRA Recipe:**
  - `r`: 16
  - `alpha`: 32
- **Recommended Task Types:** `instruction`, `chat`
