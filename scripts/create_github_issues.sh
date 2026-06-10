#!/usr/bin/env bash
# SLMForge - create all 42 GitHub issues
# Requires: gh CLI authenticated (gh auth login)
# Pre-req: labels + milestones already exist (see PROJECT_CONTEXT.md "GitHub Automation Scripts")
# Usage:   bash scripts/create_github_issues.sh

set -euo pipefail

REPO="${REPO:-newton-school-ai/slmforge}"

create_issue() {
  local num=$1; local title=$2; local milestone=$3; local labels=$4; local body=$5
  echo "Creating: Issue $num - $title"
  gh issue create --repo "$REPO" \
    --title "Issue $num - $title" \
    --milestone "$milestone" \
    --label "$labels" \
    --body "$body"
  sleep 1
}

# --- M1: Scaffold + Engine API Contract ---

create_issue 1 "Initialize repo scaffold, CI workflow, Docker setup, pre-commit hooks" \
  "M1: Scaffold + Engine API Contract" "m1,infra" \
  "## Why
SLMForge needs a working dev environment from day one. CI + pre-commit hygiene prevent style drift, non-ASCII leaks, and internal-data path mistakes.

## What to build
- pyproject.toml, requirements.txt, .gitignore, .env.example
- Dockerfile and docker-compose.yml (api + redis)
- .github/workflows/ci.yml (ASCII guard + internal-data guard + ruff + black + pytest)
- .pre-commit-config.yaml

## Files to create
- pyproject.toml, requirements.txt, .gitignore, .env.example
- Dockerfile, docker-compose.yml
- .github/workflows/ci.yml
- .pre-commit-config.yaml

## How to test locally
\`\`\`bash
pre-commit install && pre-commit run --all-files
docker compose build && docker compose up -d
curl http://localhost:8000/health
\`\`\`

## Acceptance Criteria
- [ ] pre-commit run --all-files passes
- [ ] docker compose up -d brings the API up on port 8000
- [ ] /health returns {\"status\":\"ok\"}
- [ ] CI green on a no-op PR
- [ ] Pre-commit blocks a deliberate _internal/<other-file> path

## Branch: feature/issue-1-scaffold
## Dependencies: None"

create_issue 2 "Design SQLite schema for builds, runs, sources, datasets, evals, serves" \
  "M1: Scaffold + Engine API Contract" "m1,infra,engine" \
  "## Why
SLMForge tracks every build, dataset, eval, serve session. SQLite by default; Postgres-ready for shared deploys.

## What to build
- SQLAlchemy models: Build, Run, Source, Dataset, Eval, Serve
- Alembic migration setup with initial migration
- Default SLMFORGE_DB_URL=sqlite:///./slmforge.db

## Files to create
- src/slmforge/engine/state.py
- alembic.ini, alembic/env.py, alembic/versions/001_initial.py
- src/slmforge/api/db.py

## How to test locally
\`\`\`bash
alembic upgrade head
pytest tests/unit/test_models.py
\`\`\`

## Acceptance Criteria
- [ ] All six tables exist after alembic upgrade head
- [ ] Models import with no circular deps
- [ ] One unit test per model exercises create + read

## Branch: feature/issue-2-db-schema
## Dependencies: Issue 1"

create_issue 3 "FastAPI skeleton with health + build + run endpoints (contract only)" \
  "M1: Scaffold + Engine API Contract" "m1,engine" \
  "## Why
The API surface is the contract for the CLI + Web UI. Locking endpoint shapes early prevents weeks of churn.

## What to build
- FastAPI app under slmforge.api.main:app
- Endpoints (skeletons): /health, POST /builds, GET /builds, GET /builds/{id}, WS /builds/{id}/stream
- Pydantic schemas mirroring docs/ENGINE_API.md

## Files to create
- src/slmforge/api/main.py
- src/slmforge/api/routes/builds.py
- src/slmforge/api/schemas.py

## How to test locally
\`\`\`bash
uvicorn slmforge.api.main:app --reload
curl http://localhost:8000/health
\`\`\`

## Acceptance Criteria
- [ ] /health returns 200
- [ ] POST /builds validates payload against ENGINE_API.md
- [ ] OpenAPI docs render at /docs
- [ ] Pytest covers happy + invalid payload

## Branch: feature/issue-3-fastapi-skeleton
## Dependencies: Issue 2"

create_issue 4 "Commit docs/ENGINE_API.md (contract between CLI / UI and engine)" \
  "M1: Scaffold + Engine API Contract" "m1,engine" \
  "## Why
Both surfaces consume the same engine. Without a locked contract the two will diverge.

## What to build
- docs/ENGINE_API.md v0: build request schema, streamed events, on-disk build layout, versioning policy
- Future contract changes update this file in the same PR

## Files to create
- docs/ENGINE_API.md

## How to test locally
\`\`\`bash
grep -n v0 docs/ENGINE_API.md
\`\`\`

## Acceptance Criteria
- [ ] Contract covers request, response, streamed events, on-disk layout, versioning
- [ ] CONTRIBUTING.md links to it
- [ ] Maintainer signs off

## Branch: docs/issue-4-engine-api
## Dependencies: Issue 3"

# --- M2: Data Layer + Source Adapters ---

create_issue 5 "Source adapter base class + registry" \
  "M2: Data Layer + Source Adapters" "m2,data" \
  "## Why
SLMForge supports multiple data sources (synthetic, public, local, future internal) behind one interface.

## What to build
- Source ABC with iter_records() + metadata()
- Concrete adapters: SyntheticSource, PublicHFSource, LocalSource
- INTERNAL stub raising NotImplementedError
- Registry mapping type -> adapter class

## Files to create
- src/slmforge/data/sources/{base,synthetic,public,local,internal,registry}.py

## How to test locally
\`\`\`bash
pytest tests/unit/test_source_registry.py
\`\`\`

## Acceptance Criteria
- [ ] Registry rejects unknown source types
- [ ] INTERNAL raises NotImplementedError with clear message
- [ ] All adapters yield records with the same shape

## Branch: feature/issue-5-source-adapters
## Dependencies: Issue 1"

create_issue 6 "Multi-format ingestion (jsonl, csv, parquet, txt-folder)" \
  "M2: Data Layer + Source Adapters" "m2,data" \
  "## Why
Users will throw any of these at SLMForge. Detect-and-load should just work.

## What to build
- Per-format readers returning a normalised record stream
- python-magic based detection with extension fallback
- Sample-preview helper (first N records)

## Files to create
- src/slmforge/data/ingest.py
- src/slmforge/data/preview.py

## How to test locally
\`\`\`bash
pytest tests/unit/test_ingest.py
\`\`\`

## Acceptance Criteria
- [ ] jsonl, csv, parquet, txt-folder all load correctly
- [ ] Format detection works when extension is missing
- [ ] Sample preview returns first 5 records

## Branch: feature/issue-6-multi-format
## Dependencies: Issue 5"

create_issue 7 "Dataset Builder with seeded 80/10/10 split + dataset card" \
  "M2: Data Layer + Source Adapters" "m2,data" \
  "## Why
Reproducibility starts with deterministic splits. Eval split must be frozen across runs.

## What to build
- DatasetBuilder.build(sources, seed) -> datasets.DatasetDict (train/val/eval)
- Dataset card markdown auto-generation
- Default seed 42

## Files to create
- src/slmforge/data/builder.py
- src/slmforge/data/card.py

## How to test locally
\`\`\`bash
pytest tests/unit/test_dataset_builder.py
\`\`\`

## Acceptance Criteria
- [ ] Same seed produces same splits
- [ ] Card lists every source with type, id/path, size, licence
- [ ] No eval leak into train

## Branch: feature/issue-7-dataset-builder
## Dependencies: Issue 6"

create_issue 8 "Source guard + CI regex scan" \
  "M2: Data Layer + Source Adapters" "m2,data,infra" \
  "## Why
Internal NST data must never enter the public repo. Two-layer defence.

## What to build
- source_guard.validate() raising on unregistered types and _internal/ paths
- CI step greps tracked files for known NST identifier patterns
- Pre-commit hook variant

## Files to create
- src/slmforge/data/source_guard.py
- Extend .github/workflows/ci.yml and .pre-commit-config.yaml

## How to test locally
\`\`\`bash
pytest tests/unit/test_source_guard.py
\`\`\`

## Acceptance Criteria
- [ ] Guard rejects unregistered + internal-path sources
- [ ] CI fails on a deliberate violation
- [ ] Pre-commit fails on a deliberate violation

## Branch: feature/issue-8-source-guard
## Dependencies: Issue 5"

create_issue 9 "Public dataset prefetch helper" \
  "M2: Data Layer + Source Adapters" "m2,data" \
  "## Why
Recipes need their public datasets cached locally before training.

## What to build
- prefetch(dataset_id) downloads + caches via datasets.load_dataset
- License-attribution writeback into the dataset card
- CLI: slmforge data prefetch <id>

## Files to create
- src/slmforge/data/prefetch.py
- Extend src/slmforge/cli/main.py

## How to test locally
\`\`\`bash
slmforge data prefetch samsum
ls data/cache/samsum
\`\`\`

## Acceptance Criteria
- [ ] Subsequent prefetches are no-ops
- [ ] License recorded in dataset card
- [ ] CLI prints cache path on success

## Branch: feature/issue-9-prefetch
## Dependencies: Issue 5"

# --- M3: Task Type System ---

create_issue 10 "Task detector v1 (heuristic + small classifier)" \
  "M3: Task Type System" "m3,task" \
  "## Why
The whole 'just point at data' UX rests on the detector picking the right task type.

## What to build
- Heuristics on schema-shape + content features
- Supports: classification, summarisation, qa, instruction, chat
- Confidence score + fallback prompt for low-confidence

## Files to create
- src/slmforge/task/detector.py

## How to test locally
\`\`\`bash
pytest tests/unit/test_task_detector.py
\`\`\`

## Acceptance Criteria
- [ ] >= 85% accuracy on regression suite (Issue 14)
- [ ] Returns confidence + alternatives
- [ ] Heuristics documented in module docstring

## Branch: feature/issue-10-task-detector
## Dependencies: Issue 7"

create_issue 11 "Per-task chat template + instruction format" \
  "M3: Task Type System" "m3,task" \
  "## Why
Each task type needs a canonical prompt shape so one engine trains + serves all of them.

## What to build
- Template per task (classification, summarisation, qa, instruction, chat)
- Renderer turning records into prompt + target

## Files to create
- src/slmforge/task/templates.py

## How to test locally
\`\`\`bash
pytest tests/unit/test_task_templates.py
\`\`\`

## Acceptance Criteria
- [ ] One canonical template per task type
- [ ] Roundtrip render-then-strip equals original
- [ ] Templates align with Phi-3 + Llama 3.1 chat formats

## Branch: feature/issue-11-task-templates
## Dependencies: Issue 10"

create_issue 12 "Per-task metric selector" \
  "M3: Task Type System" "m3,task,eval" \
  "## Why
Eval has to just work; users do not pick metrics manually.

## What to build
- Selector mapping task type to metric suite
- Plug-in interface for new metrics

## Files to create
- src/slmforge/task/metrics.py

## How to test locally
\`\`\`bash
pytest tests/unit/test_task_metrics.py
\`\`\`

## Acceptance Criteria
- [ ] Each task type returns a non-empty suite
- [ ] Uniform metric(preds, refs) call shape
- [ ] Mapping documented in module docstring

## Branch: feature/issue-12-task-metrics
## Dependencies: Issue 11"

create_issue 13 "User-override path in CLI + UI" \
  "M3: Task Type System" "m3,task,cli,ui" \
  "## Why
Detector will be wrong sometimes. Users must override task, base, template without editing code.

## What to build
- CLI flags: --task, --base, --template
- UI dropdowns with detector suggestion as default
- Server-side validation

## Files to create
- Extend src/slmforge/cli/main.py
- Extend src/slmforge/api/schemas.py

## How to test locally
\`\`\`bash
slmforge build --task classification --auto --recipe sanity
\`\`\`

## Acceptance Criteria
- [ ] Overrides reach the engine
- [ ] Invalid values rejected with helpful message
- [ ] UI uses the same API surface

## Branch: feature/issue-13-overrides
## Dependencies: Issue 10"

create_issue 14 "Task-detector regression suite" \
  "M3: Task Type System" "m3,task" \
  "## Why
Detector must not silently regress as task coverage grows.

## What to build
- tests/fixtures/task_detection/ with 5-10 labelled samples per task type
- Pytest asserts the right label
- CI gate on this test

## Files to create
- tests/integration/test_task_detector_regression.py
- tests/fixtures/task_detection/...

## How to test locally
\`\`\`bash
pytest tests/integration/test_task_detector_regression.py
\`\`\`

## Acceptance Criteria
- [ ] >= 30 labelled samples
- [ ] Overall accuracy >= 85%
- [ ] CI fails if accuracy drops below threshold

## Branch: feature/issue-14-detector-regression
## Dependencies: Issue 10"

# --- M4: Fine-Tune Engine ---

create_issue 15 "Base model registry" \
  "M4: Fine-Tune Engine" "m4,finetune" \
  "## Why
Small, opinionated list of bases. Outside the registry needs a deliberate add.

## What to build
- Entries for Phi-3-mini, Llama 3.1 8B Instruct, Qwen 2.5 7B Instruct, DeepSeek V3 distill
- Per-entry: HF id, default LoRA recipe, VRAM footprint, licence, recommended task types

## Files to create
- src/slmforge/finetune/registry.py
- docs/model_card.md per base

## How to test locally
\`\`\`bash
pytest tests/unit/test_base_registry.py
\`\`\`

## Acceptance Criteria
- [ ] Four bases registered with full metadata
- [ ] Registry rejects unregistered HF ids
- [ ] Each base has a unit test loading config

## Branch: feature/issue-15-base-registry
## Dependencies: Issue 7"

create_issue 16 "LoRA training harness" \
  "M4: Fine-Tune Engine" "m4,finetune" \
  "## Why
Core engine: dataset + base + config -> trained adapter.

## What to build
- train_lora(dataset, base, lora_cfg, training_cfg) -> adapter_path
- HF Trainer + peft; checkpoints per epoch; adapter only
- Deterministic with seed

## Files to create
- src/slmforge/finetune/lora.py
- src/slmforge/finetune/train.py

## How to test locally
\`\`\`bash
pytest tests/integration/test_lora_smoke.py -m gpu
\`\`\`

## Acceptance Criteria
- [ ] Trains tiny adapter on a 50-record dataset
- [ ] Adapter loads + generates a token
- [ ] Same seed -> same final eval within tolerance

## Branch: feature/issue-16-lora-harness
## Dependencies: Issue 15, Issue 7"

create_issue 17 "QLoRA (4-bit) path for 8B-class models" \
  "M4: Fine-Tune Engine" "m4,finetune" \
  "## Why
Llama 3.1 8B and Qwen 2.5 7B do not fit on shared GPU in fp16.

## What to build
- 4-bit NF4 quantisation via bitsandbytes
- Auto-selected for 8B-class registered bases
- Smoke test on Llama 3.1 8B

## Files to create
- src/slmforge/finetune/qlora.py

## How to test locally
\`\`\`bash
pytest tests/integration/test_qlora_smoke.py -m gpu
\`\`\`

## Acceptance Criteria
- [ ] QLoRA auto-selected for 8B-class
- [ ] Memory < 16GB for Llama 3.1 8B
- [ ] Smoke test passes

## Branch: feature/issue-17-qlora
## Dependencies: Issue 16"

create_issue 18 "Run planner with VRAM + walltime estimator" \
  "M4: Fine-Tune Engine" "m4,engine,finetune" \
  "## Why
Planner saves shared GPU from oversubscription and gives realistic ETA.

## What to build
- Estimator: dataset_size + base + LoRA cfg + epochs -> VRAM_gb, est_minutes
- Warning when over shared budget
- Plan emitted in streamed build response

## Files to create
- src/slmforge/engine/planner.py

## How to test locally
\`\`\`bash
pytest tests/unit/test_planner.py
\`\`\`

## Acceptance Criteria
- [ ] Estimates within +-30% of actual on smoke run
- [ ] Warning fires over budget
- [ ] Plan event emitted before training

## Branch: feature/issue-18-run-planner
## Dependencies: Issue 15"

create_issue 19 "Checkpoint + resume; deterministic by seed" \
  "M4: Fine-Tune Engine" "m4,finetune" \
  "## Why
Shared-GPU runs get pre-empted. Resume must work without losing progress.

## What to build
- Checkpoint per epoch
- slmforge build --resume <build_id>
- Seed propagation across resume

## Files to create
- src/slmforge/finetune/checkpoint.py
- Extend src/slmforge/cli/main.py

## How to test locally
\`\`\`bash
slmforge build --recipe sanity --auto --kill-after-epoch 1
slmforge build --resume <id>
\`\`\`

## Acceptance Criteria
- [ ] Resumed run identical final eval to uninterrupted
- [ ] Checkpoint path in DB
- [ ] No double-counted epochs

## Branch: feature/issue-19-checkpoint-resume
## Dependencies: Issue 16"

create_issue 20 "Log + progress streaming over WebSocket" \
  "M4: Fine-Tune Engine" "m4,engine,cli,ui" \
  "## Why
CLI and UI both need live progress; one stream serves both.

## What to build
- WS endpoint WS /builds/{id}/stream
- Events: discover_sources, detect_task, plan, epoch, checkpoint, eval, complete
- CLI client renders via rich

## Files to create
- Extend src/slmforge/api/routes/builds.py
- src/slmforge/cli/tty.py

## How to test locally
\`\`\`bash
slmforge build --recipe sanity --auto
\`\`\`

## Acceptance Criteria
- [ ] All event types emit in order
- [ ] CLI shows live loss + GPU util
- [ ] Reconnect resumes the stream

## Branch: feature/issue-20-stream
## Dependencies: Issue 3, Issue 16"

# --- M5: Eval Engine ---

create_issue 21 "Per-task metric suite end-to-end" \
  "M5: Eval Engine" "m5,eval" \
  "## Why
Auto-pick metrics based on detected task type.

## What to build
- eval_run(adapter, eval_dataset, task_type) -> metrics dict
- Wires per-task selector into a runnable pipeline

## Files to create
- src/slmforge/eval/run.py

## How to test locally
\`\`\`bash
pytest tests/integration/test_eval_run.py
\`\`\`

## Acceptance Criteria
- [ ] Right metric set per task type
- [ ] Values land in build's DB row
- [ ] Reproducible with fixed seed

## Branch: feature/issue-21-eval-run
## Dependencies: Issue 16, Issue 12"

create_issue 22 "Optional LLM-as-judge harness" \
  "M5: Eval Engine" "m5,eval" \
  "## Why
Generative tasks need a quality signal beyond ROUGE. LLM-as-judge gives a blinded win-rate.

## What to build
- Blinded A/B between SLM and reference; configurable judge model
- Win-rate + per-category breakdown

## Files to create
- src/slmforge/eval/judge.py

## How to test locally
\`\`\`bash
SLMFORGE_JUDGE_MODEL=... pytest tests/integration/test_judge.py
\`\`\`

## Acceptance Criteria
- [ ] Judge runs blinded (no position bias)
- [ ] Win-rate in [0, 1]
- [ ] Sample annotations persisted

## Branch: feature/issue-22-judge
## Dependencies: Issue 21"

create_issue 23 "Ship-gate calculator + Pareto plot" \
  "M5: Eval Engine" "m5,eval" \
  "## Why
A build must be told ship / iterate / kill, not just given numbers.

## What to build
- Ship gate: quality >= 0.95*baseline, cost <= 0.10*baseline, latency p95 <= 1.5x
- Pareto plot: quality vs cost across runs
- Verdict string

## Files to create
- src/slmforge/eval/ship_gate.py
- src/slmforge/eval/pareto.py

## How to test locally
\`\`\`bash
pytest tests/unit/test_ship_gate.py
\`\`\`

## Acceptance Criteria
- [ ] PASS / FAIL per dimension
- [ ] Pareto plot saved to build dir
- [ ] Verdict text in eval report

## Branch: feature/issue-23-ship-gate
## Dependencies: Issue 21"

create_issue 24 "Eval report markdown generator" \
  "M5: Eval Engine" "m5,eval" \
  "## Why
Every build needs a human-readable eval report.

## What to build
- generate_eval_report(build_id) -> eval_report.md
- Metric cards, ship-gate verdict, sample outputs, Pareto ref

## Files to create
- src/slmforge/eval/report.py

## How to test locally
\`\`\`bash
slmforge eval <build_id>
cat builds/<build_id>/eval_report.md
\`\`\`

## Acceptance Criteria
- [ ] Report exists in build dir
- [ ] All ship-gate dimensions present
- [ ] >= 3 side-by-side samples vs reference

## Branch: feature/issue-24-eval-report
## Dependencies: Issue 23"

# --- M6: Serving Engine ---

create_issue 25 "vLLM single-LoRA serve, OpenAI-compatible /v1/chat/completions" \
  "M6: Serving Engine" "m6,serve" \
  "## Why
Drop the new SLM into existing code by changing one line.

## What to build
- vLLM wrapper exposing /v1/chat/completions
- Adapter loaded by build_id
- Health + model-list endpoints

## Files to create
- src/slmforge/serve/vllm_app.py

## How to test locally
\`\`\`bash
slmforge serve <build_id>
curl http://localhost:8000/v1/chat/completions -H 'Content-Type: application/json' -d '{\"model\":\"<build_id>\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}]}'
\`\`\`

## Acceptance Criteria
- [ ] Server boots in < 60s on shared GPU
- [ ] Valid OpenAI-shape response
- [ ] OpenAI Python client works with base_url override

## Branch: feature/issue-25-vllm-serve
## Dependencies: Issue 16"

create_issue 26 "Multi-LoRA hot-swap" \
  "M6: Serving Engine" "m6,serve" \
  "## Why
One base loaded, many adapters registered. Adapter picked via the model field.

## What to build
- Adapter registry that vLLM swaps per request
- slmforge serve --adapters a,b,c

## Files to create
- src/slmforge/serve/adapter_registry.py
- Extend src/slmforge/serve/vllm_app.py

## How to test locally
\`\`\`bash
slmforge serve --adapters build_a,build_b
\`\`\`

## Acceptance Criteria
- [ ] Two adapters registered at once
- [ ] Per-request swap with no base reload
- [ ] p95 within 1.2x of single-adapter serve

## Branch: feature/issue-26-multi-lora
## Dependencies: Issue 25"

create_issue 27 "USAGE.md auto-generator (curl + Python + JS)" \
  "M6: Serving Engine" "m6,serve" \
  "## Why
From 'build done' to 'using it in code' must be one screen.

## What to build
- Generate USAGE.md per build: serve command, curl, Python (openai client), JS (fetch)
- 'Change one line in your existing OpenAI client' snippet

## Files to create
- src/slmforge/serve/usage_doc.py

## How to test locally
\`\`\`bash
slmforge usage <build_id>
\`\`\`

## Acceptance Criteria
- [ ] USAGE.md generated alongside adapter
- [ ] curl example works copy-paste
- [ ] Python + JS snippets work copy-paste

## Branch: feature/issue-27-usage-doc
## Dependencies: Issue 25"

create_issue 28 "Auth modes (off by default, optional bearer-token)" \
  "M6: Serving Engine" "m6,serve" \
  "## Why
Localhost has no auth; shared deployments need a token.

## What to build
- Feature-flagged bearer-token middleware
- Token in .env
- 401 with helpful message

## Files to create
- src/slmforge/serve/auth.py
- Extend src/slmforge/api/main.py

## How to test locally
\`\`\`bash
SLMFORGE_AUTH_TOKEN=secret uvicorn slmforge.api.main:app
curl -H 'Authorization: Bearer secret' http://localhost:8000/builds
\`\`\`

## Acceptance Criteria
- [ ] Off by default
- [ ] 401 when token mismatches
- [ ] Timing-safe token check

## Branch: feature/issue-28-auth
## Dependencies: Issue 3"

# --- M7: CLI ---

create_issue 29 "Typer entrypoint with subcommands" \
  "M7: CLI" "m7,cli" \
  "## Why
The CLI is one of two primary surfaces.

## What to build
- slmforge init / build / eval / serve / list / usage / ui via Typer
- Each subcommand delegates to the engine via ENGINE_API contract

## Files to create
- Extend src/slmforge/cli/main.py

## How to test locally
\`\`\`bash
slmforge --help
slmforge build --help
\`\`\`

## Acceptance Criteria
- [ ] All seven subcommands present
- [ ] Each shows useful --help
- [ ] slmforge --version works

## Branch: feature/issue-29-cli-entrypoint
## Dependencies: Issue 3"

create_issue 30 "Interactive prompts + --auto flag" \
  "M7: CLI" "m7,cli" \
  "## Why
Default walks the user through task / base / config; --auto skips for scripts.

## What to build
- Interactive Q&A for task type, base, LoRA defaults
- --auto accepts all defaults
- Validation of all answers

## Files to create
- src/slmforge/cli/prompts.py

## How to test locally
\`\`\`bash
slmforge build
slmforge build --auto
\`\`\`

## Acceptance Criteria
- [ ] Interactive covers task / base / LoRA / epochs / batch
- [ ] --auto matches manual defaults
- [ ] Invalid answers re-prompt with reason

## Branch: feature/issue-30-interactive
## Dependencies: Issue 29"

create_issue 31 "Pretty terminal output (rich-based)" \
  "M7: CLI" "m7,cli" \
  "## Why
Live progress, GPU util, end-of-build summary -- CLI should feel polished.

## What to build
- rich.Live progress + multi-row stats
- End-of-build summary panel

## Files to create
- Extend src/slmforge/cli/tty.py

## How to test locally
\`\`\`bash
slmforge build --recipe sanity --auto
\`\`\`

## Acceptance Criteria
- [ ] Progress per epoch
- [ ] GPU util live
- [ ] Summary matches USAGE.md preamble

## Branch: feature/issue-31-tty-polish
## Dependencies: Issue 20"

create_issue 32 "slmforge ui launches the localhost UI" \
  "M7: CLI" "m7,cli,ui" \
  "## Why
Single command to start backend + frontend + open the browser.

## What to build
- Start FastAPI (uvicorn) + frontend dev server
- Open http://localhost:3000 automatically
- Clean Ctrl-C tears both down

## Files to create
- Extend src/slmforge/cli/main.py (ui subcommand)
- scripts/dev_ui.sh

## How to test locally
\`\`\`bash
slmforge ui
\`\`\`

## Acceptance Criteria
- [ ] Backend on 8000, frontend on 3000
- [ ] Browser opens automatically
- [ ] Ctrl-C cleans up both

## Branch: feature/issue-32-cli-ui
## Dependencies: Issue 29"

# --- M8: Web UI ---

create_issue 33 "React + Vite scaffold and routing" \
  "M8: Web UI" "m8,ui" \
  "## Why
Locks the frontend stack and pages early.

## What to build
- Vite + React + TypeScript scaffold under frontend/
- Routes: Home / NewBuild / Run / EvalReport / Serve / Library
- Page stubs

## Files to create
- frontend/package.json, frontend/vite.config.ts
- frontend/src/pages/{Home,NewBuild,Run,EvalReport,Serve,Library}.tsx
- frontend/src/App.tsx

## How to test locally
\`\`\`bash
cd frontend && npm install && npm run dev
\`\`\`

## Acceptance Criteria
- [ ] All six routes render
- [ ] npm run build passes
- [ ] No console errors on initial load

## Branch: feature/issue-33-ui-scaffold
## Dependencies: Issue 32"

create_issue 34 "New Build screen with + source rows" \
  "M8: Web UI" "m8,ui" \
  "## Why
Headline UX: paste a path, hit +, paste another, click Build.

## What to build
- Source row component with file picker + remove button
- + Add source button below the last row
- Task-type dropdown (defaults to detector suggestion)
- Advanced disclosure (base / LoRA / training params)
- Estimated VRAM + walltime line
- Big Build button

## Files to create
- frontend/src/pages/NewBuild.tsx
- frontend/src/components/SourceRow.tsx
- frontend/src/components/AdvancedDisclosure.tsx

## How to test locally
\`\`\`bash
npm run dev   # open /new-build
\`\`\`

## Acceptance Criteria
- [ ] Add / remove sources works
- [ ] Advanced disclosure toggles
- [ ] Build POSTs to /builds with right payload
- [ ] VRAM estimate updates live

## Branch: feature/issue-34-new-build-ui
## Dependencies: Issue 33, Issue 18"

create_issue 35 "Live Run screen (WebSocket-driven)" \
  "M8: Web UI" "m8,ui" \
  "## Why
The user waits here while training runs.

## What to build
- Connect to WS /builds/{id}/stream
- Progress bar, train + val loss chart, GPU util, log stream
- Cancel button

## Files to create
- frontend/src/pages/Run.tsx
- frontend/src/components/{LiveChart,LogStream}.tsx

## How to test locally
\`\`\`bash
# Start a build, open /run/<id>
\`\`\`

## Acceptance Criteria
- [ ] Live chart per epoch
- [ ] Cancel kills the run cleanly
- [ ] Reconnect on temporary disconnect

## Branch: feature/issue-35-run-ui
## Dependencies: Issue 34, Issue 20"

create_issue 36 "Eval Report screen" \
  "M8: Web UI" "m8,ui,eval" \
  "## Why
Verdict at a glance + side-by-side samples.

## What to build
- Metric cards (one per ship-gate dimension)
- Pareto plot embed
- Side-by-side SLM vs reference, paginated

## Files to create
- frontend/src/pages/EvalReport.tsx
- frontend/src/components/MetricCard.tsx

## How to test locally
\`\`\`bash
# Open /eval/<build_id>
\`\`\`

## Acceptance Criteria
- [ ] Three metric cards render
- [ ] PASS / FAIL visually obvious
- [ ] >= 5 side-by-side samples

## Branch: feature/issue-36-eval-ui
## Dependencies: Issue 24"

create_issue 37 "Serve screen + Library list" \
  "M8: Web UI" "m8,ui,serve" \
  "## Why
One-click serve; library shows everything ever built.

## What to build
- Serve: Start / Stop, curl / Python / JS tabs, QR for mobile
- Library: filter / sort / search; click row to open Serve

## Files to create
- frontend/src/pages/{Serve,Library}.tsx

## How to test locally
\`\`\`bash
# Open /serve/<id> then /library
\`\`\`

## Acceptance Criteria
- [ ] Start spins up endpoint
- [ ] All three snippet tabs work
- [ ] Library filters by task + date

## Branch: feature/issue-37-serve-library
## Dependencies: Issue 27, Issue 26"

# --- M9: Bundled Recipes ---

create_issue 38 "Recipe: Interview Coach" \
  "M9: Four Bundled Recipes" "m9,recipes,finetune" \
  "## Why
First recipe ships a multi-turn chat SLM using only public + synthetic data.

## What to build
- Synthetic multi-turn transcript generator grounded in a public LeetCode-style HF dataset
- recipe.yaml, synth_gen.py, USAGE_NOTES.md
- End-to-end smoke target

## Files to create
- src/recipes/interview_coach/{recipe.yaml,synth_gen.py,USAGE_NOTES.md}
- tests/integration/test_recipe_interview_coach.py

## How to test locally
\`\`\`bash
slmforge build --recipe interview_coach --auto
\`\`\`

## Acceptance Criteria
- [ ] Builds end-to-end in < 30 min on shared GPU
- [ ] Holds a coherent multi-turn interview on eval split
- [ ] Smoke test green in CI

## Branch: feature/issue-38-recipe-interview-coach
## Dependencies: Issue 16, Issue 24"

create_issue 39 "Recipe: Feedback Summariser" \
  "M9: Four Bundled Recipes" "m9,recipes,finetune" \
  "## Why
Easiest first proof point: narrow surface, easy eval, well-structured input.

## What to build
- Pipeline: public doc corpora (cnn_dailymail / samsum / xsum) + synthetic comment templates
- Faithfulness check: no invented asks

## Files to create
- src/recipes/feedback_summariser/{recipe.yaml,synth_gen.py,USAGE_NOTES.md}
- tests/integration/test_recipe_feedback_summariser.py

## How to test locally
\`\`\`bash
slmforge build --recipe feedback_summariser --auto
\`\`\`

## Acceptance Criteria
- [ ] Builds in < 20 min on shared GPU
- [ ] ROUGE-L >= 0.55 on eval
- [ ] Faithfulness: 0 invented asks on 100-sample review

## Branch: feature/issue-39-recipe-feedback
## Dependencies: Issue 16, Issue 24"

create_issue 40 "Recipe: Question Assistant" \
  "M9: Four Bundled Recipes" "m9,recipes,finetune" \
  "## Why
Closest to the 'give me a binary search question' use case; exercises retrieval + ranking + clarification.

## What to build
- Synthetic queries + histories over a public question bank
- FAISS semantic + Meilisearch keyword retrieval, re-rank, not-solved filter

## Files to create
- src/recipes/question_assistant/{recipe.yaml,synth_gen.py,USAGE_NOTES.md}
- tests/integration/test_recipe_question_assistant.py

## How to test locally
\`\`\`bash
slmforge build --recipe question_assistant --auto
\`\`\`

## Acceptance Criteria
- [ ] Builds in < 30 min on shared GPU
- [ ] MRR@10 >= 0.6 on eval
- [ ] Never invents questions outside the public bank

## Branch: feature/issue-40-recipe-question
## Dependencies: Issue 16, Issue 24"

create_issue 41 "Recipe: Iterative Editor" \
  "M9: Four Bundled Recipes" "m9,recipes,finetune" \
  "## Why
Conversation-shaped task; cleanest training signal of the four.

## What to build
- Public draft corpora (IteraTeR / WritingPrompts / OSS-licensed essays)
- Labelled feedback operators ('shorter', 'mention X', 'less promotional', 'fix tone')
- Multi-round chains preserved in chat template

## Files to create
- src/recipes/iterative_editor/{recipe.yaml,synth_gen.py,USAGE_NOTES.md}
- tests/integration/test_recipe_iterative_editor.py

## How to test locally
\`\`\`bash
slmforge build --recipe iterative_editor --auto
\`\`\`

## Acceptance Criteria
- [ ] Builds in < 25 min on shared GPU
- [ ] Honours feedback in >= 80% of samples
- [ ] No context loss after 3 rounds

## Branch: feature/issue-41-recipe-editor
## Dependencies: Issue 16, Issue 24"

# --- M10: Packaging + Production Polish ---

create_issue 42 "pip install slmforge, Docker image, end-to-end CI smoke tests, v1.0 release" \
  "M10: Packaging + Production Polish" "m10,infra" \
  "## Why
The tool is only useful if someone outside the pod can pip install it and have it work.

## What to build
- Publishable wheel via pyproject.toml
- Docker image tagged slmforge:v1.0
- CI smoke runs all four recipes (or marked gpu and skipped by default)
- Release notes covering M1-M10

## Files to create
- Final pyproject.toml polish
- Final Dockerfile
- .github/workflows/release.yml
- CHANGELOG.md
- scripts/smoke_recipes.sh

## How to test locally
\`\`\`bash
python -m build
docker build -t slmforge:v1.0 .
bash scripts/smoke_recipes.sh
\`\`\`

## Acceptance Criteria
- [ ] pip install slmforge works from fresh venv
- [ ] Docker image runs /health and slmforge --help
- [ ] All four recipe smoke tests pass (or behind gpu mark)
- [ ] v1.0.0 tag with release notes

## Branch: feature/issue-42-release
## Dependencies: All preceding"

echo ""
echo "All 42 issues created on $REPO."
echo "Verify: gh issue list --repo $REPO --limit 50"
