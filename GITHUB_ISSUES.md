# SLMForge - GitHub Issues

All 42 issues in detailed format for GitHub creation via `bash scripts/create_github_issues.sh`.

---

## M1: Scaffold + Engine API Contract

---

### Issue 1 - Initialize repo scaffold, CI workflow, Docker setup, pre-commit hooks

**Why:**
SLMForge needs a working dev environment from day one. Without CI and pre-commit hygiene, contributors drift on style, leak non-ASCII characters, and accidentally commit internal-data paths.

**What to build:**
- Top-level `pyproject.toml`, `requirements.txt`, `.gitignore`, `.env.example`
- `Dockerfile` and `docker-compose.yml` (api + redis services)
- `.github/workflows/ci.yml` running ASCII guard, internal-data guard, ruff, black, pytest
- `.pre-commit-config.yaml` with: trailing-whitespace, end-of-file-fixer, ruff, black, internal-data block, ASCII-only

**Files to create/update:**
- `pyproject.toml`, `requirements.txt`, `.gitignore`, `.env.example`
- `Dockerfile`, `docker-compose.yml`
- `.github/workflows/ci.yml`
- `.pre-commit-config.yaml`

**How to test locally:**
```bash
pre-commit install && pre-commit run --all-files
docker compose build && docker compose up -d
curl http://localhost:8000/health
```

**Acceptance Criteria:**
- [ ] `pre-commit run --all-files` passes
- [ ] `docker compose up -d` brings the API up on port 8000
- [ ] `/health` returns `{"status":"ok"}`
- [ ] CI green on a no-op PR
- [ ] Pre-commit blocks a deliberate `_internal/<other-file>` path

**Branch:** `feature/issue-1-scaffold`
**Dependencies:** None

---

### Issue 2 - Design SQLite schema for builds, runs, sources, datasets, evals, serves

**Why:**
SLMForge tracks every build, dataset, eval, and serve session. SQLite by default so it runs anywhere with zero setup; upgrade path to Postgres for shared deploys.

**What to build:**
- SQLAlchemy models: Build, Run, Source, Dataset, Eval, Serve
- Alembic migration setup with initial migration
- Default `SLMFORGE_DB_URL=sqlite:///./slmforge.db`

**Files to create/update:**
- `src/slmforge/engine/state.py` (SQLAlchemy models)
- `alembic.ini`, `alembic/env.py`, `alembic/versions/001_initial.py`
- `src/slmforge/api/db.py` (session factory)

**How to test locally:**
```bash
alembic upgrade head
python -c "from slmforge.engine.state import Build; print(Build.__table__.columns.keys())"
pytest tests/unit/test_models.py
```

**Acceptance Criteria:**
- [ ] All six tables exist after `alembic upgrade head`
- [ ] Models import cleanly with no circular deps
- [ ] One unit test per model exercises create + read

**Branch:** `feature/issue-2-db-schema`
**Dependencies:** Issue 1

---

### Issue 3 - FastAPI skeleton with health + build + run endpoints (contract only)

**Why:**
The API surface is the contract for the CLI + Web UI. Locking endpoint shapes early prevents weeks of churn later.

**What to build:**
- FastAPI app under `slmforge.api.main:app`
- Endpoints (skeletons returning 501 where logic isn't ready): `/health`, `POST /builds`, `GET /builds`, `GET /builds/{id}`, `WS /builds/{id}/stream`
- Pydantic request + response schemas mirroring `docs/ENGINE_API.md`

**Files to create/update:**
- `src/slmforge/api/main.py`
- `src/slmforge/api/routes/builds.py`
- `src/slmforge/api/schemas.py`

**How to test locally:**
```bash
uvicorn slmforge.api.main:app --reload
curl http://localhost:8000/health
curl -X POST http://localhost:8000/builds -d '{"sources":[],"task_type":"auto"}' -H 'Content-Type: application/json'
```

**Acceptance Criteria:**
- [ ] `/health` returns 200
- [ ] `POST /builds` validates payload against `docs/ENGINE_API.md`
- [ ] OpenAPI docs render at `/docs`
- [ ] Pytest covers happy + invalid payload

**Branch:** `feature/issue-3-fastapi-skeleton`
**Dependencies:** Issue 2

---

### Issue 4 - Commit docs/ENGINE_API.md (contract between CLI / UI and engine)

**Why:**
Both surfaces (CLI + Web UI) consume the same engine. Without a locked contract the two will diverge.

**What to build:**
- `docs/ENGINE_API.md` v0 contract: build request schema, streamed events, on-disk build layout, versioning policy
- All future engine changes that affect the contract must update this file in the same PR

**Files to create/update:**
- `docs/ENGINE_API.md`

**How to test locally:**
```bash
# No code to test; review-driven
grep -n "v0" docs/ENGINE_API.md
```

**Acceptance Criteria:**
- [ ] Contract covers request, response, streamed events, on-disk layout, versioning
- [ ] CONTRIBUTING.md links to it
- [ ] Maintainer signs off

**Branch:** `docs/issue-4-engine-api`
**Dependencies:** Issue 3

---

## M2: Data Layer + Source Adapters

---

### Issue 5 - Source adapter base class + registry

**Why:**
SLMForge must support multiple data sources (synthetic, public, local, future internal) behind one interface. A registry pattern lets each capability declare its source explicitly.

**What to build:**
- `Source` ABC with `iter_records()` + `metadata()` methods
- Concrete adapters: `SyntheticSource`, `PublicHFSource`, `LocalSource`
- `INTERNAL` stub adapter that raises NotImplementedError
- Registry that maps `type -> adapter class`

**Files to create/update:**
- `src/slmforge/data/sources/base.py`
- `src/slmforge/data/sources/{synthetic,public,local,internal}.py`
- `src/slmforge/data/sources/registry.py`

**How to test locally:**
```bash
pytest tests/unit/test_source_registry.py
```

**Acceptance Criteria:**
- [ ] Registry rejects unknown source types
- [ ] `INTERNAL` adapter raises NotImplementedError with clear message
- [ ] All adapters return iterables with the same record shape

**Branch:** `feature/issue-5-source-adapters`
**Dependencies:** Issue 1

---

### Issue 6 - Multi-format ingestion (jsonl, csv, parquet, txt-folder)

**Why:**
Users will throw any of these at SLMForge. Detect-and-load should "just work" without a config file.

**What to build:**
- Per-format reader functions returning a normalised record stream
- `python-magic` based format detection with extension fallback
- Sample-preview helper (first N records) for UI

**Files to create/update:**
- `src/slmforge/data/ingest.py`
- `src/slmforge/data/preview.py`

**How to test locally:**
```bash
pytest tests/unit/test_ingest.py
```

**Acceptance Criteria:**
- [ ] Each of `.jsonl`, `.csv`, `.parquet`, and a folder of `.txt` files loads correctly
- [ ] Format detection works even when extension is missing
- [ ] Sample preview returns first 5 records

**Branch:** `feature/issue-6-multi-format`
**Dependencies:** Issue 5

---

### Issue 7 - Dataset Builder with seeded 80/10/10 split + dataset card

**Why:**
Reproducibility starts with deterministic splits. Eval split must be frozen across runs.

**What to build:**
- `DatasetBuilder.build(sources, seed)` returning a `datasets.DatasetDict` (train/val/eval)
- Dataset-card markdown auto-generation listing every source + licence + size
- Deterministic seed by default (42); user-overridable

**Files to create/update:**
- `src/slmforge/data/builder.py`
- `src/slmforge/data/card.py`

**How to test locally:**
```bash
pytest tests/unit/test_dataset_builder.py
```

**Acceptance Criteria:**
- [ ] Same seed produces same splits across runs
- [ ] Dataset card lists every source with type, id/path, size, licence
- [ ] Eval split has no leak into train (verified by set intersection check)

**Branch:** `feature/issue-7-dataset-builder`
**Dependencies:** Issue 6

---

### Issue 8 - Source guard + CI regex scan

**Why:**
Internal NST data must never enter the public repo. Two-layer defence: in-process refusal + CI scan.

**What to build:**
- `source_guard.validate(source)` raising on unregistered types and `_internal/` paths
- CI step that greps tracked files for known NST identifier patterns
- Pre-commit hook variant of the same check

**Files to create/update:**
- `src/slmforge/data/source_guard.py`
- `.github/workflows/ci.yml` (extend)
- `.pre-commit-config.yaml` (extend)

**How to test locally:**
```bash
pytest tests/unit/test_source_guard.py
# Force a violation:
mkdir -p _internal/leak && echo "secret" > _internal/leak/x.txt && pre-commit run --all-files
```

**Acceptance Criteria:**
- [ ] In-process guard rejects unregistered + internal-path sources
- [ ] CI fails on a deliberate violation
- [ ] Pre-commit fails on a deliberate violation
- [ ] `_internal/PROJECT_CONTEXT.md` remains the only allowed path under `_internal/` (gitignored anyway)

**Branch:** `feature/issue-8-source-guard`
**Dependencies:** Issue 5

---

### Issue 9 - Public dataset prefetch helper

**Why:**
Recipes need their public datasets cached locally before training; doing it inline slows the first build dramatically.

**What to build:**
- `prefetch(dataset_id)` that downloads + caches via `datasets.load_dataset`
- License-attribution writeback into the dataset card
- CLI: `slmforge data prefetch <id>`

**Files to create/update:**
- `src/slmforge/data/prefetch.py`
- `src/slmforge/cli/main.py` (add `data prefetch` subcommand)

**How to test locally:**
```bash
slmforge data prefetch samsum
ls data/cache/samsum
```

**Acceptance Criteria:**
- [ ] Subsequent prefetches are no-ops (cache hit)
- [ ] License recorded in dataset card
- [ ] CLI prints the cache path on success

**Branch:** `feature/issue-9-prefetch`
**Dependencies:** Issue 5

---

## M3: Task Type System

---

### Issue 10 - Task detector v1 (heuristic + small classifier)

**Why:**
The whole "just point at data" UX rests on the detector picking the right task type more often than not.

**What to build:**
- Heuristic detector: schema-shape + content-feature rules for `classification`, `summarisation`, `qa`, `instruction`, `chat`
- Confidence score per task
- Fallback prompt for low-confidence cases

**Files to create/update:**
- `src/slmforge/task/detector.py`

**How to test locally:**
```bash
pytest tests/unit/test_task_detector.py
```

**Acceptance Criteria:**
- [ ] >= 85% accuracy on the regression suite (Issue 14)
- [ ] Returns confidence + alternative suggestions
- [ ] Documented heuristics in module docstring

**Branch:** `feature/issue-10-task-detector`
**Dependencies:** Issue 7

---

### Issue 11 - Per-task chat template + instruction format

**Why:**
Each task type needs a canonical prompt shape so the same engine can train + serve all of them.

**What to build:**
- Template per task type (classification, summarisation, qa, instruction, chat)
- Renderer that turns a dataset record into a model-ready prompt + target

**Files to create/update:**
- `src/slmforge/task/templates.py`

**How to test locally:**
```bash
pytest tests/unit/test_task_templates.py
```

**Acceptance Criteria:**
- [ ] Each task type has a single canonical template
- [ ] Roundtrip test: render then strip equals original
- [ ] Templates align with Phi-3 + Llama 3.1 chat formats

**Branch:** `feature/issue-11-task-templates`
**Dependencies:** Issue 10

---

### Issue 12 - Per-task metric selector

**Why:**
Eval has to "just work" -- the user does not pick metrics manually.

**What to build:**
- Selector that maps task type to a metric suite (accuracy/F1 for classification, ROUGE for summarisation, etc.)
- Plug-in interface for new metrics later

**Files to create/update:**
- `src/slmforge/task/metrics.py`

**How to test locally:**
```bash
pytest tests/unit/test_task_metrics.py
```

**Acceptance Criteria:**
- [ ] Each task type returns a non-empty metric suite
- [ ] Metrics can be invoked uniformly (`metric(preds, refs)`)
- [ ] Documented mapping in module docstring

**Branch:** `feature/issue-12-task-metrics`
**Dependencies:** Issue 11

---

### Issue 13 - User-override path in CLI + UI

**Why:**
Detector will be wrong sometimes. Users must be able to override task type, base model, and template without editing code.

**What to build:**
- CLI flags: `--task`, `--base`, `--template`
- UI: dropdowns with the detector's suggestion as default
- Server-side validation against the registry

**Files to create/update:**
- `src/slmforge/cli/main.py` (extend build subcommand)
- `src/slmforge/api/schemas.py` (extend build request)

**How to test locally:**
```bash
slmforge build --task classification --auto --recipe sanity
```

**Acceptance Criteria:**
- [ ] CLI accepts overrides and they reach the engine
- [ ] Invalid override values are rejected with a helpful message
- [ ] UI sets the overrides via the same API surface

**Branch:** `feature/issue-13-overrides`
**Dependencies:** Issue 10

---

### Issue 14 - Task-detector regression suite

**Why:**
The detector must not silently regress as we expand task coverage. Lock in a labelled test set.

**What to build:**
- Directory `tests/fixtures/task_detection/` with 5-10 labelled samples per task type
- Pytest that runs the detector and asserts the right label
- CI gate on this test

**Files to create/update:**
- `tests/integration/test_task_detector_regression.py`
- `tests/fixtures/task_detection/...`

**How to test locally:**
```bash
pytest tests/integration/test_task_detector_regression.py
```

**Acceptance Criteria:**
- [ ] >= 30 labelled samples in the fixture
- [ ] Overall accuracy >= 85%
- [ ] CI fails if accuracy drops below threshold

**Branch:** `feature/issue-14-detector-regression`
**Dependencies:** Issue 10

---

## M4: Fine-Tune Engine

---

### Issue 15 - Base model registry

**Why:**
We back a small, opinionated list of bases. Anything outside the registry needs a deliberate add, not a casual prompt.

**What to build:**
- Registry entries for Phi-3-mini, Llama 3.1 8B Instruct, Qwen 2.5 7B Instruct, DeepSeek V3 distill
- Per-entry: HF id, default LoRA recipe, VRAM footprint, licence, recommended task types

**Files to create/update:**
- `src/slmforge/finetune/registry.py`
- `docs/model_card.md` (one card per base)

**How to test locally:**
```bash
pytest tests/unit/test_base_registry.py
```

**Acceptance Criteria:**
- [ ] Four bases registered with full metadata
- [ ] Registry rejects unregistered HF ids
- [ ] Each base has a unit test loading config (no weight download in CI)

**Branch:** `feature/issue-15-base-registry`
**Dependencies:** Issue 7

---

### Issue 16 - LoRA training harness

**Why:**
Core engine: turn a dataset + base + config into a trained adapter.

**What to build:**
- `train_lora(dataset, base, lora_cfg, training_cfg) -> adapter_path`
- Uses HF Trainer + peft; checkpoints per epoch; saves adapter only
- Deterministic with a seed

**Files to create/update:**
- `src/slmforge/finetune/lora.py`
- `src/slmforge/finetune/train.py` (CLI entrypoint)

**How to test locally:**
```bash
pytest tests/integration/test_lora_smoke.py -m gpu
```

**Acceptance Criteria:**
- [ ] Trains a tiny adapter on a 50-record dataset end-to-end
- [ ] Adapter loads + generates a token
- [ ] Same seed produces same final eval score within tolerance

**Branch:** `feature/issue-16-lora-harness`
**Dependencies:** Issue 15, Issue 7

---

### Issue 17 - QLoRA (4-bit) path for 8B-class models

**Why:**
Llama 3.1 8B and Qwen 2.5 7B do not fit on shared GPU in fp16. QLoRA is the way.

**What to build:**
- 4-bit NF4 quantisation path using `bitsandbytes`
- Auto-selected when base is registered as 8B-class
- Smoke test on Llama 3.1 8B

**Files to create/update:**
- `src/slmforge/finetune/qlora.py`

**How to test locally:**
```bash
pytest tests/integration/test_qlora_smoke.py -m gpu
```

**Acceptance Criteria:**
- [ ] QLoRA selected automatically for 8B-class bases
- [ ] Memory footprint < 16GB for Llama 3.1 8B
- [ ] Smoke test passes

**Branch:** `feature/issue-17-qlora`
**Dependencies:** Issue 16

---

### Issue 18 - Run planner with VRAM + walltime estimator

**Why:**
A planner saves shared GPU from oversubscription and gives the user a realistic ETA before they hit Build.

**What to build:**
- Estimator: dataset_size + base + LoRA cfg + epochs -> VRAM_gb, est_minutes
- Warning when over shared-GPU budget
- Plan is part of the streamed build response

**Files to create/update:**
- `src/slmforge/engine/planner.py`

**How to test locally:**
```bash
pytest tests/unit/test_planner.py
```

**Acceptance Criteria:**
- [ ] Estimates within +-30% of actual on a smoke run
- [ ] Warning fires when planned VRAM > configured shared budget
- [ ] Plan event emitted before training starts

**Branch:** `feature/issue-18-run-planner`
**Dependencies:** Issue 15

---

### Issue 19 - Checkpoint + resume; deterministic by seed

**Why:**
Long runs on shared GPU get pre-empted. Resume must work without losing progress.

**What to build:**
- Save checkpoint after every epoch
- `slmforge build --resume <build_id>` continues from last checkpoint
- Seed propagation across resume

**Files to create/update:**
- `src/slmforge/finetune/checkpoint.py`
- `src/slmforge/cli/main.py` (extend)

**How to test locally:**
```bash
# Start, kill after epoch 1, resume
slmforge build --recipe sanity --auto --kill-after-epoch 1
slmforge build --resume <id>
```

**Acceptance Criteria:**
- [ ] Resumed run produces identical final eval as uninterrupted run
- [ ] Checkpoint path recorded in DB
- [ ] No double-counted epochs

**Branch:** `feature/issue-19-checkpoint-resume`
**Dependencies:** Issue 16

---

### Issue 20 - Log + progress streaming over WebSocket

**Why:**
CLI and UI both need live progress; one stream serves both.

**What to build:**
- WebSocket endpoint `WS /builds/{id}/stream`
- Event types: discover_sources, detect_task, plan, epoch, checkpoint, eval, complete
- CLI client renders progress via `rich`

**Files to create/update:**
- `src/slmforge/api/routes/builds.py` (WS handler)
- `src/slmforge/cli/tty.py`

**How to test locally:**
```bash
slmforge build --recipe sanity --auto
# Verify live progress in terminal
```

**Acceptance Criteria:**
- [ ] All event types emit in order
- [ ] CLI shows live loss + GPU util
- [ ] Reconnect resumes the stream

**Branch:** `feature/issue-20-stream`
**Dependencies:** Issue 3, Issue 16

---

## M5: Eval Engine

---

### Issue 21 - Per-task metric suite end-to-end

**Why:**
Eval picks the right metrics automatically based on detected task type.

**What to build:**
- `eval_run(adapter, eval_dataset, task_type) -> metrics dict`
- Wires the per-task selector from Issue 12 into a runnable pipeline

**Files to create/update:**
- `src/slmforge/eval/run.py`

**How to test locally:**
```bash
pytest tests/integration/test_eval_run.py
```

**Acceptance Criteria:**
- [ ] Returns the right metric set for each task type
- [ ] Metric values land in the build's DB row
- [ ] Reproducible with a fixed seed

**Branch:** `feature/issue-21-eval-run`
**Dependencies:** Issue 16, Issue 12

---

### Issue 22 - Optional LLM-as-judge harness

**Why:**
Generative tasks need a quality signal beyond ROUGE. LLM-as-judge with a strong reference model gives a blinded win-rate.

**What to build:**
- Judge harness: blinded A/B between SLM and reference; configurable judge model
- Win-rate + per-category breakdown

**Files to create/update:**
- `src/slmforge/eval/judge.py`

**How to test locally:**
```bash
SLMFORGE_JUDGE_MODEL=... pytest tests/integration/test_judge.py
```

**Acceptance Criteria:**
- [ ] Judge runs blinded (no position bias)
- [ ] Win-rate is in [0, 1]
- [ ] Sample annotations are persisted for review

**Branch:** `feature/issue-22-judge`
**Dependencies:** Issue 21

---

### Issue 23 - Ship-gate calculator + Pareto plot

**Why:**
Build must be told "ship / iterate / kill" not just "here are some numbers".

**What to build:**
- Ship gate: quality >= 0.95 * baseline, cost <= 0.10 * baseline, latency p95 <= 1.5 * baseline
- Pareto plot: quality vs cost across runs
- Output a clear verdict string

**Files to create/update:**
- `src/slmforge/eval/ship_gate.py`
- `src/slmforge/eval/pareto.py`

**How to test locally:**
```bash
pytest tests/unit/test_ship_gate.py
```

**Acceptance Criteria:**
- [ ] Calculator outputs PASS / FAIL per gate dimension
- [ ] Pareto plot saved to build dir
- [ ] Verdict text in eval report

**Branch:** `feature/issue-23-ship-gate`
**Dependencies:** Issue 21

---

### Issue 24 - Eval report markdown generator

**Why:**
Every build needs a human-readable eval report in the build directory.

**What to build:**
- `generate_eval_report(build_id) -> eval_report.md`
- Metric cards, ship-gate verdict, sample outputs, Pareto reference

**Files to create/update:**
- `src/slmforge/eval/report.py`
- `docs/MODEL_CARD_TEMPLATE.md` (use as base)

**How to test locally:**
```bash
slmforge eval <build_id>
cat builds/<build_id>/eval_report.md
```

**Acceptance Criteria:**
- [ ] Report exists in build dir after eval run
- [ ] All ship-gate dimensions present
- [ ] At least 3 side-by-side sample outputs vs reference

**Branch:** `feature/issue-24-eval-report`
**Dependencies:** Issue 23

---

## M6: Serving Engine

---

### Issue 25 - vLLM single-LoRA serve, OpenAI-compatible /v1/chat/completions

**Why:**
The single most-asked-for surface: drop the new SLM into existing code by changing one line.

**What to build:**
- vLLM server wrapper exposing `/v1/chat/completions`
- Adapter loaded by build_id
- Health + model-list endpoints

**Files to create/update:**
- `src/slmforge/serve/vllm_app.py`

**How to test locally:**
```bash
slmforge serve <build_id>
curl http://localhost:8000/v1/chat/completions -H 'Content-Type: application/json' -d '{"model":"<build_id>","messages":[{"role":"user","content":"hi"}]}'
```

**Acceptance Criteria:**
- [ ] Server boots in < 60s on shared GPU
- [ ] `/v1/chat/completions` returns valid OpenAI-shape response
- [ ] OpenAI Python client works with `base_url` override

**Branch:** `feature/issue-25-vllm-serve`
**Dependencies:** Issue 16

---

### Issue 26 - Multi-LoRA hot-swap

**Why:**
One base loaded, many adapters registered. Picking the adapter via the `model` field lets a single server cover all four recipes.

**What to build:**
- Adapter registry that vLLM swaps per request
- `slmforge serve --adapters a,b,c` registers multiple

**Files to create/update:**
- `src/slmforge/serve/adapter_registry.py`
- `src/slmforge/serve/vllm_app.py` (extend)

**How to test locally:**
```bash
slmforge serve --adapters build_a,build_b
curl ... -d '{"model":"build_a", ...}'
curl ... -d '{"model":"build_b", ...}'
```

**Acceptance Criteria:**
- [ ] Two adapters registered at once
- [ ] Per-request swap works with no base reload
- [ ] Latency p95 within 1.2x of single-adapter serve

**Branch:** `feature/issue-26-multi-lora`
**Dependencies:** Issue 25

---

### Issue 27 - USAGE.md auto-generator (curl + Python + JS)

**Why:**
The on-ramp from "build done" to "I am using this in my code" must be one screen.

**What to build:**
- Generate `USAGE.md` per build with: serving command, curl, Python (openai client), JS (fetch)
- Include "drop into your existing OpenAI client by changing one line" snippet

**Files to create/update:**
- `src/slmforge/serve/usage_doc.py`

**How to test locally:**
```bash
slmforge usage <build_id>
```

**Acceptance Criteria:**
- [ ] USAGE.md generated alongside adapter
- [ ] curl example is copy-pasteable and works
- [ ] Python and JS snippets are also copy-pasteable

**Branch:** `feature/issue-27-usage-doc`
**Dependencies:** Issue 25

---

### Issue 28 - Auth modes (off by default, optional bearer-token)

**Why:**
Localhost has no auth so the tool "just works". Shared deployments need a token.

**What to build:**
- Feature-flagged bearer-token middleware
- Token lives in `.env`
- 401 with helpful message when token mismatches

**Files to create/update:**
- `src/slmforge/serve/auth.py`
- `src/slmforge/api/main.py` (extend)

**How to test locally:**
```bash
SLMFORGE_AUTH_TOKEN=secret uvicorn slmforge.api.main:app
curl -H 'Authorization: Bearer secret' http://localhost:8000/builds
```

**Acceptance Criteria:**
- [ ] Off by default
- [ ] When on, requests without token return 401
- [ ] Token check timing-safe

**Branch:** `feature/issue-28-auth`
**Dependencies:** Issue 3

---

## M7: CLI

---

### Issue 29 - Typer entrypoint with subcommands

**Why:**
The CLI is one of the two primary surfaces. The full subcommand surface lands here.

**What to build:**
- `slmforge init / build / eval / serve / list / usage / ui` via Typer
- Each subcommand delegates to the engine via the contract from Issue 4

**Files to create/update:**
- `src/slmforge/cli/main.py` (extend stub)

**How to test locally:**
```bash
slmforge --help
slmforge build --help
```

**Acceptance Criteria:**
- [ ] All seven subcommands present
- [ ] Each shows useful `--help`
- [ ] `slmforge --version` works

**Branch:** `feature/issue-29-cli-entrypoint`
**Dependencies:** Issue 3

---

### Issue 30 - Interactive prompts + --auto flag

**Why:**
Default flow walks the user through task / base / config; `--auto` skips for scripts and CI.

**What to build:**
- Interactive Q&A for task type, base model, LoRA defaults
- `--auto` accepts all defaults without prompting
- Validation of all interactive answers

**Files to create/update:**
- `src/slmforge/cli/prompts.py`

**How to test locally:**
```bash
slmforge build                # interactive
slmforge build --auto         # silent
```

**Acceptance Criteria:**
- [ ] Interactive mode covers task / base / LoRA / epochs / batch
- [ ] `--auto` produces same artefact as accepting all defaults manually
- [ ] Invalid answers re-prompt with reason

**Branch:** `feature/issue-30-interactive`
**Dependencies:** Issue 29

---

### Issue 31 - Pretty terminal output (rich-based)

**Why:**
Live progress, GPU util, end-of-build summary panel -- the CLI should feel polished.

**What to build:**
- `rich.Live` progress bar + multi-row stats
- End-of-build summary panel (model, eval, latency, serve command)

**Files to create/update:**
- `src/slmforge/cli/tty.py` (extend)

**How to test locally:**
```bash
slmforge build --recipe sanity --auto
```

**Acceptance Criteria:**
- [ ] Progress bar updates per epoch
- [ ] GPU util reflected live
- [ ] Summary panel shows the same content as USAGE.md preamble

**Branch:** `feature/issue-31-tty-polish`
**Dependencies:** Issue 20

---

### Issue 32 - slmforge ui launches the localhost UI

**Why:**
Single command to start backend + frontend + open the browser.

**What to build:**
- Start FastAPI (uvicorn) + frontend dev server
- Open `http://localhost:3000` automatically
- Clean Ctrl-C tears both down

**Files to create/update:**
- `src/slmforge/cli/main.py` (extend `ui` subcommand)
- `scripts/dev_ui.sh`

**How to test locally:**
```bash
slmforge ui
```

**Acceptance Criteria:**
- [ ] Backend on 8000, frontend on 3000
- [ ] Browser opens automatically
- [ ] Ctrl-C cleans up both processes

**Branch:** `feature/issue-32-cli-ui`
**Dependencies:** Issue 29

---

## M8: Web UI

---

### Issue 33 - React + Vite scaffold and routing

**Why:**
Locks the frontend stack and pages early.

**What to build:**
- Vite + React + TypeScript scaffold under `frontend/`
- Routing for Home / NewBuild / Run / EvalReport / Serve / Library
- Page stubs returning "TODO"

**Files to create/update:**
- `frontend/package.json`, `frontend/vite.config.ts`
- `frontend/src/pages/{Home,NewBuild,Run,EvalReport,Serve,Library}.tsx`
- `frontend/src/App.tsx`

**How to test locally:**
```bash
cd frontend && npm install && npm run dev
```

**Acceptance Criteria:**
- [ ] All six routes render
- [ ] Build passes (`npm run build`)
- [ ] No console errors on initial load

**Branch:** `feature/issue-33-ui-scaffold`
**Dependencies:** Issue 32

---

### Issue 34 - New Build screen with + source rows

**Why:**
This is the headline UX: paste a file path, hit `+`, paste another, click Build.

**What to build:**
- Source row component with file picker + remove button
- `+ Add source` button below the last row
- Task-type dropdown (defaults to detector suggestion)
- Advanced disclosure: base, LoRA rank/alpha/dropout, epochs, batch, lr
- Live "Estimated VRAM + walltime" line
- Big primary Build button

**Files to create/update:**
- `frontend/src/pages/NewBuild.tsx`
- `frontend/src/components/SourceRow.tsx`
- `frontend/src/components/AdvancedDisclosure.tsx`

**How to test locally:**
```bash
npm run dev  # open /new-build
```

**Acceptance Criteria:**
- [ ] Add / remove sources works
- [ ] Advanced disclosure toggles
- [ ] Build POSTs to `/builds` with the right payload
- [ ] Estimated VRAM line updates live

**Branch:** `feature/issue-34-new-build-ui`
**Dependencies:** Issue 33, Issue 18

---

### Issue 35 - Live Run screen (WebSocket-driven)

**Why:**
The user waits here while training runs; the screen has to make that wait pleasant + informative.

**What to build:**
- Connect to `WS /builds/{id}/stream`
- Progress bar, train + val loss chart, GPU util, log stream
- Cancel button

**Files to create/update:**
- `frontend/src/pages/Run.tsx`
- `frontend/src/components/LiveChart.tsx`
- `frontend/src/components/LogStream.tsx`

**How to test locally:**
```bash
# Start a build, open /run/<id>
```

**Acceptance Criteria:**
- [ ] Live chart updates per epoch
- [ ] Cancel kills the run cleanly
- [ ] Reconnect on temporary disconnect

**Branch:** `feature/issue-35-run-ui`
**Dependencies:** Issue 34, Issue 20

---

### Issue 36 - Eval Report screen

**Why:**
After a build, the user wants the verdict at a glance plus side-by-side sample outputs.

**What to build:**
- Metric cards (one per ship-gate dimension)
- Pareto plot embed
- Side-by-side: SLM output vs reference, paginated

**Files to create/update:**
- `frontend/src/pages/EvalReport.tsx`
- `frontend/src/components/MetricCard.tsx`

**How to test locally:**
```bash
# Open /eval/<build_id>
```

**Acceptance Criteria:**
- [ ] Three metric cards (quality / cost / latency) render
- [ ] Verdict (PASS / FAIL) is visually obvious
- [ ] At least 5 side-by-side samples

**Branch:** `feature/issue-36-eval-ui`
**Dependencies:** Issue 24

---

### Issue 37 - Serve screen + Library list

**Why:**
One click to serve a build; library shows everything ever built in this workspace.

**What to build:**
- Serve screen: Start / Stop buttons; curl / Python / JS tabs; QR for mobile
- Library: list with filter / sort / search; click a row to open Serve

**Files to create/update:**
- `frontend/src/pages/Serve.tsx`
- `frontend/src/pages/Library.tsx`

**How to test locally:**
```bash
# Open /serve/<id> then /library
```

**Acceptance Criteria:**
- [ ] Start spins up the local endpoint
- [ ] curl / Python / JS tabs all show working snippets
- [ ] Library filters by task type + date

**Branch:** `feature/issue-37-serve-library`
**Dependencies:** Issue 27, Issue 26

---

## M9: Four Bundled Recipes

---

### Issue 38 - Recipe: Interview Coach

**Why:**
First recipe ships a multi-turn chat SLM using only public + synthetic data, proving the pipeline on the kickoff-meeting "longer project" use case.

**What to build:**
- Synthetic multi-turn transcript generator grounded in a public LeetCode-style HF dataset
- Recipe config (`recipe.yaml`), generator script (`synth_gen.py`), USAGE notes
- End-to-end smoke target: `slmforge build --recipe interview_coach --auto`

**Files to create/update:**
- `src/recipes/interview_coach/{recipe.yaml,synth_gen.py,USAGE_NOTES.md}`
- `tests/integration/test_recipe_interview_coach.py`

**How to test locally:**
```bash
slmforge build --recipe interview_coach --auto
```

**Acceptance Criteria:**
- [ ] Recipe builds end-to-end in < 30 min on shared GPU
- [ ] Adapter holds a coherent multi-turn interview on the eval split
- [ ] Smoke test green in CI

**Branch:** `feature/issue-38-recipe-interview-coach`
**Dependencies:** Issue 16, Issue 24

---

### Issue 39 - Recipe: Feedback Summariser

**Why:**
Easiest first proof point: narrow surface, easy automated eval, well-structured input.

**What to build:**
- Pipeline: take public doc corpora (cnn_dailymail / samsum / xsum), inject 3-7 synthetic "faculty-style" comments per doc, synthesise reference rework summaries
- Faithfulness check: model must not invent asks not present in comments

**Files to create/update:**
- `src/recipes/feedback_summariser/{recipe.yaml,synth_gen.py,USAGE_NOTES.md}`
- `tests/integration/test_recipe_feedback_summariser.py`

**How to test locally:**
```bash
slmforge build --recipe feedback_summariser --auto
```

**Acceptance Criteria:**
- [ ] Recipe builds end-to-end in < 20 min on shared GPU
- [ ] ROUGE-L >= 0.55 on the held-out eval
- [ ] Faithfulness gate: zero invented asks on 100-sample manual review

**Branch:** `feature/issue-39-recipe-feedback`
**Dependencies:** Issue 16, Issue 24

---

### Issue 40 - Recipe: Question Assistant

**Why:**
Combines retrieval + ranking + clarification in one recipe; closest to the "give me a binary search question" use case.

**What to build:**
- Synthetic queries + synthetic solve histories over a public question bank
- FAISS semantic + Meilisearch keyword retrieval, re-rank, "not solved" filter
- Recipe wraps it all under `slmforge build --recipe question_assistant`

**Files to create/update:**
- `src/recipes/question_assistant/{recipe.yaml,synth_gen.py,USAGE_NOTES.md}`
- `tests/integration/test_recipe_question_assistant.py`

**How to test locally:**
```bash
slmforge build --recipe question_assistant --auto
```

**Acceptance Criteria:**
- [ ] Recipe builds end-to-end in < 30 min on shared GPU
- [ ] MRR@10 >= 0.6 on the eval split
- [ ] Anti-hallucination: model never invents a question outside the public bank

**Branch:** `feature/issue-40-recipe-question`
**Dependencies:** Issue 16, Issue 24

---

### Issue 41 - Recipe: Iterative Editor

**Why:**
Conversation-shaped task; cleanest training signal of the four (feedback in, revision out).

**What to build:**
- Public draft corpora (IteraTeR / WritingPrompts / OSS-licensed essays)
- Labelled feedback-operator library: "shorter", "mention X", "less promotional", "fix tone"
- Multi-round chains preserved in chat template

**Files to create/update:**
- `src/recipes/iterative_editor/{recipe.yaml,synth_gen.py,USAGE_NOTES.md}`
- `tests/integration/test_recipe_iterative_editor.py`

**How to test locally:**
```bash
slmforge build --recipe iterative_editor --auto
```

**Acceptance Criteria:**
- [ ] Recipe builds end-to-end in < 25 min on shared GPU
- [ ] Diff-quality metric: revised draft honours the feedback >= 80% of samples
- [ ] Multi-round chains preserved (no context loss after 3 rounds)

**Branch:** `feature/issue-41-recipe-editor`
**Dependencies:** Issue 16, Issue 24

---

## M10: Packaging + Production Polish

---

### Issue 42 - pip install slmforge, Docker image, end-to-end CI smoke tests, v1.0 release

**Why:**
The tool is only useful if someone outside the pod can `pip install` it and have it work.

**What to build:**
- Publishable wheel via `pyproject.toml` (already scaffolded)
- Docker image tagged `slmforge:v1.0`
- CI smoke tests run all four recipes on a GPU runner (or mark `gpu` and skip in default CI)
- Release notes covering everything from M1-M10

**Files to create/update:**
- `pyproject.toml` (final polish)
- `Dockerfile` (slim final layer)
- `.github/workflows/release.yml`
- `CHANGELOG.md`
- `scripts/smoke_recipes.sh`

**How to test locally:**
```bash
python -m build
docker build -t slmforge:v1.0 .
bash scripts/smoke_recipes.sh
```

**Acceptance Criteria:**
- [ ] `pip install slmforge` works from a fresh venv
- [ ] Docker image runs `/health` and `slmforge --help`
- [ ] All four recipe smoke tests pass in CI (or behind `gpu` mark)
- [ ] Tag `v1.0.0` published with release notes

**Branch:** `feature/issue-42-release`
**Dependencies:** All preceding issues
