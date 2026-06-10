# Engine API Contract (v0)

This file is the contract between the CLI, the Web UI, and the engine. All three consume the same shape. Changes go through the maintainer.

## Build request

```json
{
  "sources": [
    {"type": "local",     "path": "/data/train.jsonl"},
    {"type": "public",    "id": "cnn_dailymail"},
    {"type": "synthetic", "generator": "feedback_summariser", "size": 20000, "seed": 42}
  ],
  "task_type": "summarisation",
  "base_model": "auto",
  "lora": {"r": 16, "alpha": 32, "dropout": 0.05},
  "training": {"epochs": 2, "batch_size": 16, "lr": 2e-4},
  "eval": {"llm_judge": false}
}
```

### `sources[].type`
- `local` -- a path on the host filesystem
- `public` -- a permissively licensed dataset id (e.g., a Hugging Face dataset id)
- `synthetic` -- a named generator in `src/slmforge/data/sources/synthetic.py` or a recipe folder
- `internal` -- stubbed in the public build; internal team enables it later

### `task_type`
One of: `classification`, `summarisation`, `qa`, `instruction`, `chat`, `auto`.

### `base_model`
- `auto` -- engine picks based on task_type + size constraint
- explicit Hugging Face id -- e.g., `microsoft/Phi-3-mini-4k-instruct`

## Build response (streamed via WebSocket)

```jsonl
{"event": "discover_sources", "files": [...]}
{"event": "detect_task",      "task_type": "summarisation"}
{"event": "plan",             "vram_gb": 18, "est_minutes": 24}
{"event": "epoch",            "epoch": 1, "train_loss": 1.23, "val_loss": 1.05}
{"event": "checkpoint",       "path": "builds/build_.../checkpoint-epoch-1"}
{"event": "eval",             "metrics": {"rouge_l": 0.62, "accuracy": 0.91}}
{"event": "complete",         "build_id": "build_2026_06_10_142231", "usage_url": "builds/build_.../USAGE.md"}
```

## On-disk build layout

```
builds/<build_id>/
  adapter/             LoRA weights
  dataset_card.md      Sources, splits, licence
  model_card.md        Base, hyperparameters, eval scores
  eval_report.md       Metrics + Pareto plot
  USAGE.md             curl + Python + integration notes
  serve.sh             One-liner: brings this endpoint back up
```

## Versioning

The contract is versioned. Breaking changes bump `v0` -> `v1`. The CLI and UI both declare the contract version they target.
