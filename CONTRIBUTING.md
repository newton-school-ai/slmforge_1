# Contributing to SLMForge

## Branch Strategy

```
main  (stable - milestone-complete merges only)
 |
 +-- dev  (all feature branches merge here)
      |
      +-- feature/issue-N-short-name
```

- Never push to main directly
- All PRs target dev
- Maintainer merges to main after milestone review

### Branch Naming

```
feature/issue-16-lora-harness
fix/issue-19-resume-loss-mismatch
docs/issue-4-engine-api
```

For competitive PRs, append your name: `feature/issue-16-lora-harness-alice`

## PR Workflow

1. Create branch from dev: `git checkout -b feature/issue-N-name dev`
2. Make changes, commit with descriptive messages
3. Push: `git push origin feature/issue-N-name`
4. Open PR targeting dev on GitHub
5. Fill in PR template (link issue, describe changes, testing done)
6. Request 2 reviews from other contributors
7. Address review comments
8. Maintainer merges after 2 approvals

## Commit Messages

Format: `type: short description`

Types: feat, fix, docs, test, refactor, chore, perf

Examples:
- `feat: add task detector heuristic for QA datasets`
- `fix: QLoRA OOM on Llama 3.1 8B with bs 32`
- `test: add ship-gate calculator edge cases`
- `docs: update ENGINE_API.md with cancel event`
- `refactor: extract adapter registry from vllm_app`

## Coding Standards

### Python (Backend, CLI, Engine)
- Python 3.11+
- Linting: ruff + black (configured in `pyproject.toml`)
- Type hints on all function signatures
- Docstrings on all public functions
- Tests in `tests/` using pytest
- Async where applicable (FastAPI handlers, WebSocket streaming)

### TypeScript (Frontend)
- TypeScript strict mode
- ESLint + Prettier
- Functional components with hooks
- Props interfaces for all components
- React Query for server state, useState for UI state

### Engine API Contract
- [`docs/ENGINE_API.md`](docs/ENGINE_API.md) is the source of truth for CLI <-> UI <-> engine boundaries
- Any change to the contract requires maintainer review on the same PR
- Bump the contract version (v0 -> v1) on breaking changes

### Data Policy (Hard Rules)
- Source type must be `synthetic`, `public:<id>`, or `local:<path>`
- `internal:` is stubbed -- not implemented in this repo, ever
- No real NST data in commits -- pre-commit hook + CI guard enforce this
- Public datasets must have an OSS-compatible licence; record it in `docs/dataset_card.md`

### General
- ASCII-only in all files (no em dashes, arrows, smart quotes, box-drawing)
- Environment variables in `.env` (never commit secrets)
- All tests must pass before PR

## Pod Roles

| Role | Permission | Responsibility |
|------|-----------|---------------|
| Faculty | Admin | Reviews milestones, merges dev to main |
| Maintainer | Maintain | Reviews PRs, merges to dev, owns the ENGINE_API contract, does NOT write code |
| Contributors (4) | Write | Build features, raise PRs, review each other |

## Collaboration Model

Per issue, the team picks one approach:

**Option A: Competitive PRs** -- each contributor implements independently on their own branch. Maintainer merges the best implementation.

**Option B: Collaborative PR** -- team designs together, one PR with all contributors as co-authors.

## Testing

```bash
# Run all tests
pytest tests/ -v

# Unit tests only (fast)
pytest tests/unit -v

# Integration tests (require shared GPU)
pytest tests/integration -v -m gpu

# Specific test file
pytest tests/unit/test_task_detector.py -v

# With coverage
pytest tests/ --cov=src/slmforge --cov-report=term-missing

# Lint
ruff check src/
black --check src/
```

## Recipe Smoke Tests

```bash
# Run a single recipe end-to-end
slmforge build --recipe feedback_summariser --auto

# Run all four recipes (used in v1.0 release gate)
bash scripts/smoke_recipes.sh
```

## Verify No Special Characters

```bash
grep -rPn '[^\x00-\x7F]' --include="*.md" --include="*.py" --include="*.sh" --include="*.yml" --include="*.yaml" --include="*.toml" . | grep -v '.git/' | grep -v '_internal/'
```

This should return empty. If it finds matches, replace special characters with ASCII equivalents.

## Verify No Internal-Data Leaks

```bash
# Pre-commit hook does this automatically, but to check manually:
find . -type f -path '*/_internal/*' ! -name 'PROJECT_CONTEXT.md' ! -path '*/.git/*'
```

This should return empty. Anything else under `_internal/` is a violation of the data policy.

## Useful gh CLI Snippets

```bash
# Open the issue you are working on
gh issue view <N> --web

# List open PRs targeting dev
gh pr list --base dev

# Check your PR's CI status
gh pr checks
```
