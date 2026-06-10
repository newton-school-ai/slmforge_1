# Issues Tracker - SLMForge

All 42 issues across M1-M10 with: Why, What, Files, Test, Acceptance, Dependencies.

Full bodies in `GITHUB_ISSUES.md`. Authoritative roadmap in `_internal/PROJECT_CONTEXT.md`.

---

## M1: Scaffold + Engine API Contract

### Issue 1 - Initialize repo scaffold, CI workflow, Docker setup, pre-commit hooks
**Why:** Clean dev env from day one. CI + pre-commit prevent style drift, non-ASCII leaks, and internal-data path mistakes.
**What:** Directory tree, `__init__.py`, GitHub Actions CI, Dockerfile, docker-compose, pre-commit hooks.
**Files:** `.github/workflows/ci.yml`, `Dockerfile`, `docker-compose.yml`, `.pre-commit-config.yaml`, `pyproject.toml`, `requirements.txt`, `.gitignore`, `.env.example`.
**Test:** `pre-commit run --all-files` + `docker compose up -d` + `curl /health`.
**Acceptance:** CI green on no-op PR, pre-commit blocks deliberate `_internal/<other>` path, `/health` returns ok.
**Depends on:** None.

### Issue 2 - Design SQLite schema for builds, runs, sources, datasets, evals, serves
**Why:** SLMForge tracks every build, dataset, eval, and serve. SQLite default so it runs anywhere; Postgres-ready for shared deploys.
**What:** SQLAlchemy models, Alembic config, initial migration.
**Files:** `src/slmforge/engine/state.py`, `alembic.ini`, `alembic/env.py`, `alembic/versions/001_initial.py`, `src/slmforge/api/db.py`.
**Test:** `alembic upgrade head` + `pytest tests/unit/test_models.py`.
**Acceptance:** Six tables exist, models import without circular deps, one unit test per model.
**Depends on:** #1

### Issue 3 - FastAPI skeleton with health + build + run endpoints (contract only)
**Why:** API surface is the contract for CLI + Web UI. Lock endpoint shapes early to prevent churn.
**What:** FastAPI app, route stubs returning 501 where logic is missing, Pydantic schemas matching `docs/ENGINE_API.md`.
**Files:** `src/slmforge/api/main.py`, `src/slmforge/api/routes/builds.py`, `src/slmforge/api/schemas.py`.
**Test:** `uvicorn slmforge.api.main:app --reload` + `curl /health` + `POST /builds`.
**Acceptance:** `/health` 200, `POST /builds` validates payload, OpenAPI docs render at `/docs`.
**Depends on:** #2

### Issue 4 - Commit docs/ENGINE_API.md (contract between CLI / UI and engine)
**Why:** Without a locked contract, the CLI and UI drift. This file is the source of truth.
**What:** v0 contract: request schema, streamed events, on-disk layout, versioning policy.
**Files:** `docs/ENGINE_API.md`.
**Test:** Maintainer reads and signs off.
**Acceptance:** Contract covers request, response, streamed events, on-disk layout, versioning; CONTRIBUTING.md links to it.
**Depends on:** #3

---

## M2: Data Layer + Source Adapters

### Issue 5 - Source adapter base class + registry
**Why:** Multiple data sources (synthetic, public, local, future internal) behind one interface keeps the engine clean and the data-policy guardrails enforceable.
**What:** `Source` ABC, four adapters (`SyntheticSource`, `PublicHFSource`, `LocalSource`, `INTERNAL` stub), registry.
**Files:** `src/slmforge/data/sources/{base,synthetic,public,local,internal,registry}.py`.
**Test:** `pytest tests/unit/test_source_registry.py`.
**Acceptance:** Registry rejects unknown types, `INTERNAL` raises NotImplementedError with clear message, all adapters yield same record shape.
**Depends on:** #1

### Issue 6 - Multi-format ingestion (jsonl, csv, parquet, txt-folder)
**Why:** Users will throw any format at SLMForge. Detect-and-load should "just work".
**What:** Per-format readers, format detection (`python-magic` + extension fallback), sample-preview helper.
**Files:** `src/slmforge/data/ingest.py`, `src/slmforge/data/preview.py`.
**Test:** `pytest tests/unit/test_ingest.py` with fixtures in all four formats.
**Acceptance:** All four formats load; detection works without extension; preview returns first 5 records.
**Depends on:** #5

### Issue 7 - Dataset Builder with seeded 80/10/10 split + dataset card
**Why:** Reproducibility starts with deterministic splits. Eval split must be frozen across runs.
**What:** `DatasetBuilder.build(sources, seed)` returning `DatasetDict` (train/val/eval); dataset card markdown auto-generation.
**Files:** `src/slmforge/data/builder.py`, `src/slmforge/data/card.py`.
**Test:** `pytest tests/unit/test_dataset_builder.py`.
**Acceptance:** Same seed -> same splits; card lists every source with type/id/path/size/licence; no eval leak into train.
**Depends on:** #6

### Issue 8 - Source guard + CI regex scan
**Why:** Internal NST data must never enter the public repo. Two-layer defence: in-process + CI.
**What:** `source_guard.validate()` raising on unregistered types and `_internal/` paths; CI grep step; pre-commit hook variant.
**Files:** `src/slmforge/data/source_guard.py`, extends `.github/workflows/ci.yml` and `.pre-commit-config.yaml`.
**Test:** `pytest tests/unit/test_source_guard.py`; force a violation manually and watch CI fail.
**Acceptance:** Guard rejects unregistered + internal paths; CI + pre-commit both fail on deliberate violation.
**Depends on:** #5

### Issue 9 - Public dataset prefetch helper
**Why:** Recipes need public datasets cached before training; inline downloads slow the first build badly.
**What:** `prefetch(dataset_id)` via `datasets.load_dataset`; licence attribution in dataset card; CLI subcommand.
**Files:** `src/slmforge/data/prefetch.py`, extends `src/slmforge/cli/main.py`.
**Test:** `slmforge data prefetch samsum`; second run is a no-op.
**Acceptance:** Subsequent prefetches no-op; licence recorded; CLI prints cache path on success.
**Depends on:** #5

---

## M3: Task Type System

### Issue 10 - Task detector v1 (heuristic + small classifier)
**Why:** "Just point at data" UX rests on the detector picking the right task type most of the time.
**What:** Heuristics on schema-shape + content features for classification, summarisation, QA, instruction, chat; confidence + fallback prompt.
**Files:** `src/slmforge/task/detector.py`.
**Test:** `pytest tests/unit/test_task_detector.py`.
**Acceptance:** >= 85% accuracy on regression suite (#14); returns confidence + alternatives; heuristics documented.
**Depends on:** #7

### Issue 11 - Per-task chat template + instruction format
**Why:** Each task type needs a canonical prompt shape so one engine trains and serves all of them.
**What:** Template per task + renderer turning records into prompt + target.
**Files:** `src/slmforge/task/templates.py`.
**Test:** `pytest tests/unit/test_task_templates.py`; roundtrip render -> strip equals original.
**Acceptance:** One canonical template per task; templates align with Phi-3 + Llama 3.1 chat formats.
**Depends on:** #10

### Issue 12 - Per-task metric selector
**Why:** Eval must "just work" -- the user does not pick metrics manually.
**What:** Mapping task type -> metric suite (accuracy/F1 for classification, ROUGE for summarisation, etc.); plug-in interface for new metrics.
**Files:** `src/slmforge/task/metrics.py`.
**Test:** `pytest tests/unit/test_task_metrics.py`.
**Acceptance:** Each task type returns non-empty suite; uniform `metric(preds, refs)` call shape; mapping documented.
**Depends on:** #11

### Issue 13 - User-override path in CLI + UI
**Why:** Detector will be wrong sometimes. Users must override task / base / template without editing code.
**What:** CLI flags `--task`, `--base`, `--template`; UI dropdowns with detector suggestion as default; server-side validation.
**Files:** Extends `src/slmforge/cli/main.py` and `src/slmforge/api/schemas.py`.
**Test:** `slmforge build --task classification --auto --recipe sanity`.
**Acceptance:** Overrides reach the engine; invalid values rejected with reason; UI uses same API surface.
**Depends on:** #10

### Issue 14 - Task-detector regression suite
**Why:** Detector must not silently regress as task coverage grows.
**What:** >= 30 labelled samples per task type in `tests/fixtures/task_detection/`; pytest gates CI on accuracy.
**Files:** `tests/integration/test_task_detector_regression.py`, `tests/fixtures/task_detection/...`.
**Test:** `pytest tests/integration/test_task_detector_regression.py`.
**Acceptance:** >= 30 samples; overall >= 85% accuracy; CI fails below threshold.
**Depends on:** #10

---

## M4: Fine-Tune Engine

### Issue 15 - Base model registry
**Why:** Small, opinionated list of bases. Outside the registry needs a deliberate add, not a casual prompt.
**What:** Entries for Phi-3-mini, Llama 3.1 8B Instruct, Qwen 2.5 7B Instruct, DeepSeek V3 distill, each with HF id, default LoRA recipe, VRAM footprint, licence, recommended task types.
**Files:** `src/slmforge/finetune/registry.py`, `docs/model_card.md` per base.
**Test:** `pytest tests/unit/test_base_registry.py` (no weight download in CI).
**Acceptance:** Four bases registered; registry rejects unregistered HF ids; each base has unit test loading config.
**Depends on:** #7

### Issue 16 - LoRA training harness
**Why:** Core engine: dataset + base + config -> trained adapter.
**What:** `train_lora(dataset, base, lora_cfg, training_cfg) -> adapter_path`; HF Trainer + peft; checkpoint per epoch; adapter only; deterministic with seed.
**Files:** `src/slmforge/finetune/lora.py`, `src/slmforge/finetune/train.py`.
**Test:** `pytest tests/integration/test_lora_smoke.py -m gpu` -- tiny adapter on 50 records.
**Acceptance:** Trains end-to-end; adapter loads + generates a token; same seed -> same final eval within tolerance.
**Depends on:** #15, #7

### Issue 17 - QLoRA (4-bit) path for 8B-class models
**Why:** Llama 3.1 8B and Qwen 2.5 7B don't fit on shared GPU in fp16.
**What:** 4-bit NF4 path via `bitsandbytes`; auto-selected for registered 8B-class bases.
**Files:** `src/slmforge/finetune/qlora.py`.
**Test:** `pytest tests/integration/test_qlora_smoke.py -m gpu` on Llama 3.1 8B.
**Acceptance:** Auto-selected for 8B-class; memory < 16GB; smoke test passes.
**Depends on:** #16

### Issue 18 - Run planner with VRAM + walltime estimator
**Why:** Planner saves shared GPU from oversubscription and gives a realistic ETA before training starts.
**What:** Estimator: dataset_size + base + LoRA cfg + epochs -> VRAM_gb, est_minutes; warning over budget; plan emitted on stream.
**Files:** `src/slmforge/engine/planner.py`.
**Test:** `pytest tests/unit/test_planner.py`.
**Acceptance:** Estimates within +-30% on smoke run; warning fires over budget; `plan` event emitted before training.
**Depends on:** #15

### Issue 19 - Checkpoint + resume; deterministic by seed
**Why:** Shared-GPU runs get pre-empted. Resume must work without losing progress.
**What:** Checkpoint per epoch; `slmforge build --resume <id>`; seed propagation across resume.
**Files:** `src/slmforge/finetune/checkpoint.py`, extends `src/slmforge/cli/main.py`.
**Test:** Kill mid-run after epoch 1, resume, confirm identical final eval.
**Acceptance:** Resumed run identical to uninterrupted; checkpoint path in DB; no double-counted epochs.
**Depends on:** #16

### Issue 20 - Log + progress streaming over WebSocket
**Why:** CLI and UI both need live progress; one stream serves both.
**What:** `WS /builds/{id}/stream`; events `discover_sources / detect_task / plan / epoch / checkpoint / eval / complete`; CLI client via `rich`.
**Files:** Extends `src/slmforge/api/routes/builds.py`, new `src/slmforge/cli/tty.py`.
**Test:** Build a recipe; verify live progress in terminal.
**Acceptance:** All event types in order; CLI shows live loss + GPU util; reconnect resumes the stream.
**Depends on:** #3, #16

---

## M5: Eval Engine

### Issue 21 - Per-task metric suite end-to-end
**Why:** Eval picks the right metrics automatically based on detected task type.
**What:** `eval_run(adapter, eval_dataset, task_type) -> metrics dict`; wires #12 into a runnable pipeline.
**Files:** `src/slmforge/eval/run.py`.
**Test:** `pytest tests/integration/test_eval_run.py`.
**Acceptance:** Right metric set per task; values land in build row; reproducible with seed.
**Depends on:** #16, #12

### Issue 22 - Optional LLM-as-judge harness
**Why:** Generative tasks need a quality signal beyond ROUGE. LLM-as-judge gives blinded win-rate vs a reference.
**What:** Blinded A/B between SLM and reference; configurable judge model; win-rate + per-category breakdown.
**Files:** `src/slmforge/eval/judge.py`.
**Test:** `SLMFORGE_JUDGE_MODEL=... pytest tests/integration/test_judge.py`.
**Acceptance:** Judge blinded (no position bias); win-rate in [0,1]; annotations persisted.
**Depends on:** #21

### Issue 23 - Ship-gate calculator + Pareto plot
**Why:** A build must be told ship/iterate/kill, not given numbers and left guessing.
**What:** Ship gate: quality >= 0.95 * baseline, cost <= 0.10 * baseline, latency p95 <= 1.5x; Pareto plot quality-vs-cost.
**Files:** `src/slmforge/eval/ship_gate.py`, `src/slmforge/eval/pareto.py`.
**Test:** `pytest tests/unit/test_ship_gate.py` with injected scores.
**Acceptance:** PASS/FAIL per dimension; Pareto plot saved to build dir; verdict text in eval report.
**Depends on:** #21

### Issue 24 - Eval report markdown generator
**Why:** Every build needs a human-readable eval report.
**What:** `generate_eval_report(build_id) -> eval_report.md` with metric cards, ship-gate verdict, sample outputs, Pareto reference.
**Files:** `src/slmforge/eval/report.py`.
**Test:** `slmforge eval <build_id>` then read the file.
**Acceptance:** Report exists in build dir; all ship-gate dimensions present; >= 3 side-by-side samples.
**Depends on:** #23

---

## M6: Serving Engine

### Issue 25 - vLLM single-LoRA serve, OpenAI-compatible /v1/chat/completions
**Why:** The most-asked-for surface: drop the SLM into existing code by changing one line.
**What:** vLLM server wrapping `/v1/chat/completions`; adapter loaded by build_id; health + model-list endpoints.
**Files:** `src/slmforge/serve/vllm_app.py`.
**Test:** `slmforge serve <build_id>` then curl the endpoint.
**Acceptance:** Boots in < 60s on shared GPU; valid OpenAI-shape response; OpenAI Python client works with base_url override.
**Depends on:** #16

### Issue 26 - Multi-LoRA hot-swap
**Why:** One base loaded, many adapters registered; one server covers all four recipes.
**What:** Adapter registry that vLLM swaps per request; `slmforge serve --adapters a,b,c`.
**Files:** `src/slmforge/serve/adapter_registry.py`, extends `vllm_app.py`.
**Test:** Register two adapters; send requests with different `model` values; confirm hot-swap.
**Acceptance:** Two adapters registered at once; per-request swap with no base reload; p95 within 1.2x of single-adapter serve.
**Depends on:** #25

### Issue 27 - USAGE.md auto-generator (curl + Python + JS)
**Why:** From "build done" to "using it in my code" must be one screen.
**What:** Per-build `USAGE.md` with serving command, curl, Python (openai client), JS (fetch); "change one line" snippet.
**Files:** `src/slmforge/serve/usage_doc.py`.
**Test:** `slmforge usage <build_id>` and copy-paste each snippet.
**Acceptance:** USAGE.md generated; all snippets copy-paste runnable.
**Depends on:** #25

### Issue 28 - Auth modes (off by default, optional bearer-token)
**Why:** Localhost has no auth so the tool just works; shared deploys need a token.
**What:** Feature-flagged bearer-token middleware; token in `.env`; 401 with helpful message.
**Files:** `src/slmforge/serve/auth.py`, extends `src/slmforge/api/main.py`.
**Test:** `SLMFORGE_AUTH_TOKEN=secret uvicorn ...`; curl with and without token.
**Acceptance:** Off by default; 401 on mismatch; timing-safe token check.
**Depends on:** #3

---

## M7: CLI

### Issue 29 - Typer entrypoint with subcommands
**Why:** The CLI is one of two primary surfaces. Full subcommand surface lands here.
**What:** `slmforge init / build / eval / serve / list / usage / ui` via Typer; each delegates to the engine via the contract.
**Files:** Extends `src/slmforge/cli/main.py`.
**Test:** `slmforge --help`; each subcommand `--help`.
**Acceptance:** All seven subcommands; useful `--help` everywhere; `--version` works.
**Depends on:** #3

### Issue 30 - Interactive prompts + --auto flag
**Why:** Default walks the user through task / base / config; `--auto` skips for scripts.
**What:** Interactive Q&A for task type, base model, LoRA defaults, epochs, batch; `--auto` accepts defaults.
**Files:** `src/slmforge/cli/prompts.py`.
**Test:** `slmforge build` (interactive) vs `slmforge build --auto` (silent).
**Acceptance:** Interactive covers task/base/LoRA/epochs/batch; `--auto` matches manual defaults; invalid answers re-prompt.
**Depends on:** #29

### Issue 31 - Pretty terminal output (rich-based)
**Why:** Live progress, GPU util, end-of-build summary panel -- CLI should feel polished.
**What:** `rich.Live` progress + multi-row stats; end-of-build summary panel.
**Files:** Extends `src/slmforge/cli/tty.py`.
**Test:** Run a recipe; verify polished output.
**Acceptance:** Progress per epoch; GPU util live; summary matches USAGE.md preamble.
**Depends on:** #20

### Issue 32 - slmforge ui launches the localhost UI
**Why:** Single command to start backend + frontend + open the browser.
**What:** Start uvicorn (8000) + frontend dev server (3000); open browser; clean Ctrl-C tears both down.
**Files:** Extends `src/slmforge/cli/main.py`, `scripts/dev_ui.sh`.
**Test:** `slmforge ui` from clean shell; Ctrl-C; verify both processes exit.
**Acceptance:** Backend + frontend up; browser opens automatically; Ctrl-C cleans up.
**Depends on:** #29

---

## M8: Web UI

### Issue 33 - React + Vite scaffold and routing
**Why:** Lock the frontend stack and pages early.
**What:** Vite + React + TS scaffold; routes `Home / NewBuild / Run / EvalReport / Serve / Library` with page stubs.
**Files:** `frontend/package.json`, `frontend/vite.config.ts`, `frontend/src/pages/*.tsx`, `frontend/src/App.tsx`.
**Test:** `cd frontend && npm install && npm run dev`.
**Acceptance:** All six routes render; `npm run build` passes; no console errors on initial load.
**Depends on:** #32

### Issue 34 - New Build screen with + source rows
**Why:** Headline UX: paste a path, hit `+`, paste another, click Build.
**What:** Source row component with file picker + remove; `+ Add source` button; task-type dropdown; advanced disclosure; live VRAM/walltime line; Build button.
**Files:** `frontend/src/pages/NewBuild.tsx`, `frontend/src/components/SourceRow.tsx`, `frontend/src/components/AdvancedDisclosure.tsx`.
**Test:** Open `/new-build`; add/remove rows; click Build; watch payload in network tab.
**Acceptance:** Add/remove works; advanced disclosure toggles; Build POSTs the right payload; VRAM estimate updates live.
**Depends on:** #33, #18

### Issue 35 - Live Run screen (WebSocket-driven)
**Why:** The user waits here while training runs.
**What:** Connect to `WS /builds/{id}/stream`; progress bar, train/val loss chart, GPU util, log stream, Cancel button.
**Files:** `frontend/src/pages/Run.tsx`, `frontend/src/components/{LiveChart,LogStream}.tsx`.
**Test:** Start a build; open `/run/<id>`; verify live chart.
**Acceptance:** Live chart per epoch; Cancel kills cleanly; reconnect on transient disconnect.
**Depends on:** #34, #20

### Issue 36 - Eval Report screen
**Why:** Verdict at a glance + side-by-side samples.
**What:** Three metric cards (quality / cost / latency); Pareto plot embed; paginated SLM-vs-reference samples.
**Files:** `frontend/src/pages/EvalReport.tsx`, `frontend/src/components/MetricCard.tsx`.
**Test:** Open `/eval/<build_id>` for a completed build.
**Acceptance:** Three metric cards render; PASS/FAIL visually obvious; >= 5 side-by-side samples.
**Depends on:** #24

### Issue 37 - Serve screen + Library list
**Why:** One-click serve; library shows everything ever built.
**What:** Serve: Start/Stop + curl/Python/JS tabs + QR for mobile; Library: filter/sort/search; click row to open Serve.
**Files:** `frontend/src/pages/Serve.tsx`, `frontend/src/pages/Library.tsx`.
**Test:** Open `/serve/<id>` then `/library`.
**Acceptance:** Start spins up endpoint; all three snippet tabs work; Library filters by task + date.
**Depends on:** #27, #26

---

## M9: Four Bundled Recipes

### Issue 38 - Recipe: Interview Coach
**Why:** First recipe ships a multi-turn chat SLM using only public + synthetic data; demonstrates the longer-term mock-interview use case.
**What:** Synthetic multi-turn transcript generator grounded in a public LeetCode-style HF dataset; recipe config + generator + USAGE notes.
**Files:** `src/recipes/interview_coach/{recipe.yaml,synth_gen.py,USAGE_NOTES.md}`, `tests/integration/test_recipe_interview_coach.py`.
**Test:** `slmforge build --recipe interview_coach --auto`.
**Acceptance:** Builds in < 30 min on shared GPU; coherent multi-turn interview on eval split; smoke green in CI.
**Depends on:** #16, #24

### Issue 39 - Recipe: Feedback Summariser
**Why:** Easiest first proof point -- narrow surface, easy automated eval, well-structured input.
**What:** Public doc corpora (cnn_dailymail / samsum / xsum) + pod-authored synthetic "faculty-style" comment templates; faithfulness check (no invented asks).
**Files:** `src/recipes/feedback_summariser/{recipe.yaml,synth_gen.py,USAGE_NOTES.md}`, `tests/integration/test_recipe_feedback_summariser.py`.
**Test:** `slmforge build --recipe feedback_summariser --auto`.
**Acceptance:** Builds in < 20 min on shared GPU; ROUGE-L >= 0.55; zero invented asks on 100-sample review.
**Depends on:** #16, #24

### Issue 40 - Recipe: Question Assistant
**Why:** Closest to the "give me a binary search question" use case; exercises retrieval + ranking + clarification.
**What:** Synthetic queries + synthetic solve histories over a public question bank; FAISS semantic + Meilisearch keyword retrieval; re-rank; not-solved filter.
**Files:** `src/recipes/question_assistant/{recipe.yaml,synth_gen.py,USAGE_NOTES.md}`, `tests/integration/test_recipe_question_assistant.py`.
**Test:** `slmforge build --recipe question_assistant --auto`.
**Acceptance:** Builds in < 30 min on shared GPU; MRR@10 >= 0.6; never invents questions outside the public bank.
**Depends on:** #16, #24

### Issue 41 - Recipe: Iterative Editor
**Why:** Conversation-shaped task; cleanest training signal of the four (feedback in, revision out).
**What:** Public draft corpora (IteraTeR / WritingPrompts / OSS-licensed essays) + labelled feedback operators ("shorter", "mention X", "less promotional", "fix tone"); multi-round chains preserved.
**Files:** `src/recipes/iterative_editor/{recipe.yaml,synth_gen.py,USAGE_NOTES.md}`, `tests/integration/test_recipe_iterative_editor.py`.
**Test:** `slmforge build --recipe iterative_editor --auto`.
**Acceptance:** Builds in < 25 min on shared GPU; revised draft honours feedback in >= 80% of samples; no context loss after 3 rounds.
**Depends on:** #16, #24

---

## M10: Packaging + Production Polish

### Issue 42 - pip install slmforge, Docker image, end-to-end CI smoke tests, v1.0 release
**Why:** The tool is only useful if someone outside the pod can `pip install` it and it works.
**What:** Publishable wheel via `pyproject.toml`; Docker image tagged `slmforge:v1.0`; CI smoke runs all four recipes (or `gpu`-marked + skipped by default); release notes for v1.0.0.
**Files:** Final `pyproject.toml`, final `Dockerfile`, `.github/workflows/release.yml`, `CHANGELOG.md`, `scripts/smoke_recipes.sh`.
**Test:** `python -m build`; `docker build -t slmforge:v1.0 .`; `bash scripts/smoke_recipes.sh`.
**Acceptance:** `pip install slmforge` works from a fresh venv; Docker runs `/health` + `slmforge --help`; all four recipe smokes pass (or gpu-gated); `v1.0.0` tag with release notes.
**Depends on:** All preceding.
