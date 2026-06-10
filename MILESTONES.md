# Milestones - SLMForge

## M1: Scaffold + Engine API Contract (Week 1)

### Key Output
Working repo with CI, Docker, SQLite-backed jobs/runs/builds models, FastAPI skeleton, and the locked engine API contract in `docs/ENGINE_API.md`.

### Acceptance Criteria
- Repo scaffold + CI + Docker Compose run end-to-end
- Pre-commit hooks block ASCII violations and internal-data paths
- SQLAlchemy models for builds / runs / sources / datasets / evals / serves with Alembic migrations
- FastAPI skeleton serves `/health`, `POST /builds`, `GET /builds`, `WS /builds/{id}/stream`
- `docs/ENGINE_API.md` v0 committed and linked from CONTRIBUTING.md
- Maintainer signs off on the contract

### Defense Questions
- Walk through `docs/ENGINE_API.md`. Why this shape? What is versioned?
- Explain the SQLite schema. Why these six tables? What relationships?
- Why SQLite by default? When do we switch to Postgres?
- How does the pre-commit internal-data hook actually work?
- What does the WebSocket stream emit? When?

---

## M2: Data Layer + Source Adapters (Week 2)

### Key Output
Multi-format ingestion (jsonl / csv / parquet / txt-folder) behind a `Source` adapter pattern, with `synthetic`, `public:<id>`, `local:<path>` adapters and an `internal:` stub. Source guard refuses anything else.

### Acceptance Criteria
- `Source` ABC + registry + four concrete adapters (synthetic, public, local, internal stub)
- All four file formats load via `slmforge.data.ingest`
- `DatasetBuilder` produces seeded 80/10/10 splits with a frozen eval split
- Auto-generated `dataset_card.md` per build
- Source guard rejects unregistered types and `_internal/` paths
- CI regex scan fails on a deliberate NST identifier in a test PR
- Public dataset prefetch helper caches via `datasets.load_dataset`

### Defense Questions
- Why have a `Source` ABC at all? What does it buy us?
- How does the seeded split stay frozen across runs?
- Walk through the source guard. What does it block, and at which layer?
- What happens when someone adds an unregistered source type? Where does the error surface?
- Why is the `internal:` adapter a stub? Who implements it later?

---

## M3: Task Type System (Week 3)

### Key Output
Auto task detection (heuristic + small classifier) across classification, summarisation, QA, instruction, chat -- with per-task templates and a per-task metric selector. User can always override.

### Acceptance Criteria
- Detector returns task type + confidence + alternative suggestions
- Regression suite of >= 30 labelled samples; detector >= 85% accuracy
- One canonical chat template + instruction format per task type
- Per-task metric selector wired into eval
- CLI `--task` flag and UI dropdown both flow through to the engine

### Defense Questions
- Walk through the detector heuristics. Why these signals?
- What does the regression suite look like? How would you add a new task type?
- Why one canonical template per task type? What breaks if we let users define their own?
- How is the per-task metric selector different from a generic metric list?
- What does an override look like in `docs/ENGINE_API.md`?

---

## M4: Fine-Tune Engine (Week 4)

### Key Output
Working LoRA + QLoRA training harness with a base model registry, a run planner (VRAM + walltime), checkpoint + resume, and live progress streaming to both CLI and UI.

### Acceptance Criteria
- Base registry covers Phi-3-mini, Llama 3.1 8B Instruct, Qwen 2.5 7B Instruct, DeepSeek V3 distill
- LoRA harness trains a tiny adapter on a 50-record dataset end-to-end
- QLoRA path auto-selected for 8B-class bases; Llama 3.1 8B fits in < 16GB VRAM
- Run planner estimates VRAM + walltime within +-30%
- Checkpoint per epoch; `slmforge build --resume <id>` continues without losing progress
- WebSocket stream emits discover_sources / detect_task / plan / epoch / checkpoint / eval / complete events in order

### Defense Questions
- Why LoRA over full fine-tune for our use cases?
- When does QLoRA kick in? What is NF4?
- Walk through the run planner. How do the estimates work?
- How does resume actually work? What is saved per checkpoint?
- What is in the streamed `plan` event, and where does it come from?

---

## M5: Eval Engine (Week 5)

### Key Output
Per-task metric suite, optional LLM-as-judge harness, ship-gate calculator, Pareto plot, and a human-readable eval report markdown per build.

### Acceptance Criteria
- Eval picks the right metric set automatically based on detected task type
- LLM-as-judge runs blinded (no position bias); win-rate in [0,1]
- Ship-gate: quality >= 0.95 * baseline, cost <= 0.10 * baseline, latency p95 <= 1.5x; clear PASS/FAIL per dimension
- Pareto plot saved to each build directory
- `eval_report.md` contains metric cards, verdict, and >= 3 side-by-side samples

### Defense Questions
- Why a ship gate? Why these specific thresholds?
- How does LLM-as-judge avoid position bias?
- When would you pick ROUGE over an LLM-judge win-rate? When the opposite?
- Walk through one cell of the Pareto plot. What does each axis mean?
- What's in the auto-generated eval report? Why this content?

---

## M6: Serving Engine (Week 6)

### Key Output
vLLM-backed serving endpoint exposing OpenAI-compatible `/v1/chat/completions` with multi-LoRA hot-swap, plus an auto-generated `USAGE.md` per build with curl / Python / JS snippets.

### Acceptance Criteria
- `slmforge serve <build_id>` boots in < 60s on shared GPU
- One base loaded, multiple adapters registered; per-request adapter swap with no base reload
- p95 latency within 1.2x of single-adapter serve
- `USAGE.md` auto-generated alongside adapter; curl + Python + JS snippets all copy-paste runnable
- Optional bearer-token auth (off by default, on with `SLMFORGE_AUTH_TOKEN`)

### Defense Questions
- Why vLLM over plain transformers serve?
- How does multi-LoRA hot-swap work? What's the cost per request?
- Why an OpenAI-compatible API? Who is the user we are pleasing?
- Walk through the USAGE.md generator. What sections, and why?
- How does the bearer-token auth handle timing attacks?

---

## M7: CLI (Week 7)

### Key Output
Typer-based `slmforge` entrypoint covering `init / build / eval / serve / list / usage / ui`, with rich-based live progress and an end-of-build summary panel.

### Acceptance Criteria
- All seven subcommands present with useful `--help`
- Interactive prompts walk users through task + base + LoRA + epochs + batch; `--auto` skips prompts
- Live progress bar updates per epoch; GPU util reflected; summary panel matches USAGE.md preamble
- `slmforge ui` starts backend on 8000 + frontend on 3000 and opens the browser; Ctrl-C tears both down cleanly

### Defense Questions
- Why Typer over argparse or click directly?
- Walk through the interactive flow. How do you re-prompt invalid answers?
- How does `slmforge ui` manage the two processes? What about port collisions?
- What does the end-of-build summary panel show, and why?
- How does the CLI consume the WebSocket stream from M4?

---

## M8: Web UI (Week 8)

### Key Output
React + Vite localhost app with Home, New Build, Run, Eval Report, Serve, Library screens. New Build screen has the headline "+ source row" UX. Everything talks to the FastAPI backend over REST + WebSocket.

### Acceptance Criteria
- All six routes render, build green, no console errors on initial load
- New Build: add/remove source rows works; advanced disclosure toggles; Build POSTs the right payload; estimated VRAM updates live
- Run: live loss chart updates per epoch; Cancel kills the run; reconnect on temporary disconnect
- Eval Report: three metric cards (quality / cost / latency), Pareto plot, side-by-side samples
- Serve: Start / Stop works; curl / Python / JS tabs show working snippets; Library filters by task type + date

### Defense Questions
- Why React + Vite + TS over Next.js?
- Walk through the source-row component. How does state flow up to the build request?
- How does the Run screen reconnect after a transient disconnect?
- What is on the Eval Report screen that isn't in the markdown file?
- How does the Library list query the backend efficiently?

---

## M9: Four Bundled Recipes (Week 9)

### Key Output
End-to-end working recipes for Interview Coach, Feedback Summariser, Question Assistant, and Iterative Editor -- all built only from synthetic + public data. Each is runnable via `slmforge build --recipe <name>` and ships with a smoke test.

### Acceptance Criteria
- All four recipes build end-to-end in their per-recipe time budgets on shared GPU
- Feedback Summariser hits ROUGE-L >= 0.55 with zero invented asks on 100-sample manual review
- Interview Coach holds coherent multi-turn interview on the eval split
- Question Assistant MRR@10 >= 0.6; model never invents questions outside the public bank
- Iterative Editor honours feedback in >= 80% of samples; no context loss after 3 rounds
- All four smoke tests pass in CI (or behind `gpu` mark)

### Defense Questions
- For each recipe: what is in the synthetic generator?
- How does the Feedback Summariser faithfulness gate work?
- Why MRR@10 for the Question Assistant? Why not just accuracy?
- Walk through the Iterative Editor's labelled feedback operators. How are they sampled?
- What stops a recipe from accidentally pulling internal data?

---

## M10: Packaging + Production Polish (Week 10)

### Key Output
`pip install slmforge` works from a fresh venv, Docker image tagged `slmforge:v1.0`, end-to-end smoke tests in CI, full release notes for v1.0.0.

### Acceptance Criteria
- `pip install slmforge` works from clean venv
- `docker run slmforge:v1.0 slmforge --help` works
- All four recipe smoke tests pass in CI (or marked `gpu` and gated)
- `v1.0.0` tag published with release notes covering M1-M10
- README quickstart works without modification on a clean machine
- `CHANGELOG.md` covers every milestone

### Defense Questions
- Walk through `pyproject.toml`. Why this dependency set?
- What does the Docker image actually contain? What's the layer strategy?
- How are recipe smoke tests gated in CI? When do they run?
- What is in `CHANGELOG.md`, and why this format?
- If a new contributor lands tomorrow, what's the first thing they should run, and why?

---

NST Engineering - SLMForge | Summer Profile Building Drive 2026
