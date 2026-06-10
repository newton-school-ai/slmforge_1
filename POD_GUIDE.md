# Pod Guide - SLMForge

## Pod Members

| Role | Name | GitHub Username |
|------|------|----------------|
| Faculty (Admin) | TBD | TBD |
| Maintainer (Student Leader) | TBD | TBD |
| Contributor 1 | TBD | TBD |
| Contributor 2 | TBD | TBD |
| Contributor 3 | TBD | TBD |
| Contributor 4 | TBD | TBD |

## Responsibilities

### Faculty
- Product Manager role
- Reviews milestones (M1-M10)
- Only person who merges dev into main
- Conducts Q&A sessions every 2-3 days per milestone
- Owns v1.0 release decision
- Does NOT review individual PRs

### Maintainer (Student Leader)
- Reviews all PRs from contributors
- Merges approved PRs into dev (after 2+ approvals)
- Resolves merge conflicts on dev
- Tracks sprint progress on project board
- Owns the engine API contract (`docs/ENGINE_API.md`) -- any change goes through them
- Does NOT write code or raise PRs

### Contributors (4)
- Work on all issues (not assigned to specific issues)
- Raise PRs targeting dev
- Review each other's PRs (provide 2 of 2 required approvals)
- Participate in Q&A sessions -- must be able to explain ANY code in the repo
- Maintain ASCII-only + no-internal-data discipline

## Collaboration Model

All 4 contributors work on all issues. Per issue, the team picks one approach:

### Option A: Competitive PRs

Best for self-contained issues where individual practice matters (most of M1-M5 + recipes).

1. Each contributor implements independently on their own branch
2. Branch naming: `feature/issue-N-name-yourname`
3. Each raises a separate PR targeting dev
4. All contributors review all competing PRs
5. Minimum 2 approvals required
6. Maintainer merges the best implementation

### Option B: Collaborative PR

Best for design-heavy issues where discussion adds more value (engine API contract, ship gate, run planner).

1. Team discusses approach, agrees on design, splits work
2. One branch: `feature/issue-N-name`
3. One PR with all contributors as co-authors in commit message
4. Minimum 2 approvals from contributors
5. Maintainer reviews and merges

## Sprint Timeline (10 Weeks)

| Week | Milestone | Issues |
|------|-----------|--------|
| 1 | M1: Scaffold + Engine API Contract | #1-4 |
| 2 | M2: Data Layer + Source Adapters | #5-9 |
| 3 | M3: Task Type System | #10-14 |
| 4 | M4: Fine-Tune Engine | #15-20 |
| 5 | M5: Eval Engine | #21-24 |
| 6 | M6: Serving Engine | #25-28 |
| 7 | M7: CLI | #29-32 |
| 8 | M8: Web UI | #33-37 |
| 9 | M9: Four Bundled Recipes | #38-41 |
| 10 | M10: Packaging + Production Polish | #42 |

## Q&A Sessions

- Frequency: every 2-3 days per milestone
- Format: Faculty asks any contributor to explain any code or design choice
- Scope: not just the code you wrote -- you must understand ALL code in the repo
- Purpose: ensure learning, prevent copy-paste, build defense skills

### Sample Q&A targets (rotating, drawn from MILESTONES.md "Defense Questions")
- "Walk through the ENGINE_API.md request shape. Why versioned?"
- "How does QLoRA fit Llama 3.1 8B on shared GPU?"
- "Why is the ship-gate 95% quality at 10% cost? What changes that?"
- "Walk through the multi-LoRA hot-swap path in vllm_app.py."

## Daily Standup (Async)

Post in `#slmforge` Slack channel daily:
1. What I worked on yesterday
2. What I am working on today
3. Any blockers

## PR Review Checklist

Before approving a PR, verify:
- [ ] Code works (pull branch, run locally)
- [ ] Tests pass (`pytest tests/unit -v`; `pytest tests/integration -m gpu` if applicable)
- [ ] Lint passes (`ruff check src/` and `black --check src/`)
- [ ] No hardcoded secrets or API keys
- [ ] No internal NST data introduced (CI guard also blocks; double-check anyway)
- [ ] ASCII-only across changed files
- [ ] Follows coding standards (type hints, docstrings)
- [ ] PR description links the issue (`Closes #N`) and describes changes
- [ ] Acceptance criteria from the issue are met
- [ ] If `docs/ENGINE_API.md` changed: maintainer has approved the contract change

## Engine API Contract Ownership

`docs/ENGINE_API.md` is load-bearing. Any change requires:
1. Maintainer review on the same PR
2. CLI + UI both updated in the same PR (so they don't drift)
3. Version bump (`v0 -> v1`) on breaking change, with migration notes in the PR body

## Data Policy Enforcement

- Pre-commit hook blocks any path under `_internal/` other than `PROJECT_CONTEXT.md`
- CI regex-scans every PR for internal NST identifier patterns
- All datasets must declare `synthetic`, `public:<id>`, or `local:<path>` in the registry
- Public-source licences logged in `docs/dataset_card.md`
- If you think a data source is fine but the guard rejects it: raise it with the maintainer, don't add a bypass

## Project Board

**Name:** SLMForge Sprint Tracker
**Columns:** Todo | In Progress | In Review | Done

Move issues as you work:
- Pick up issue -> move to "In Progress"
- Raise PR -> move to "In Review"
- PR merged -> move to "Done"

## Communication

- **Slack:** `#slmforge` for day-to-day, `#newton-school-ai` for cross-pod
- **GitHub:** all decisions on PRs and issues (so they're searchable later)
- **Q&A sessions:** scheduled by Faculty in calendar, joinable by all contributors

## Onboarding Checklist (For New Contributors)

- [ ] Repo access granted (ask Faculty or Maintainer)
- [ ] Slack `#slmforge` joined
- [ ] SSH key set up with GitHub
- [ ] `gh auth login` complete
- [ ] Clone, `pip install -e .[dev]`, `pre-commit install` all run successfully
- [ ] `docker compose up -d redis && uvicorn slmforge.api.main:app --reload` returns 200 on `/health`
- [ ] Read `_internal/PROJECT_CONTEXT.md` end-to-end
- [ ] Read `docs/ENGINE_API.md` end-to-end
- [ ] Pick a `good first issue` and raise a sample PR

---

NST Engineering - SLMForge | Summer Profile Building Drive 2026
