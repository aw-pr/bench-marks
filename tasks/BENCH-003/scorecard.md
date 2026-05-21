# Scorecard — BENCH-003

> Scoring rubric and anchor definitions: see `rubric.md`.
> All scores are integers 1–5. Total is the sum of all six dimensions (max 30).

---

## Metadata

| Field | Value |
|-------|-------|
| Task ID | BENCH-003 |
| Date scored | 2026-05-21 |
| Scorer | orchestrator (Claude Opus 4.7) |
| Brief | [brief.md](./brief.md) |

---

## Tool provenance

| Tool row | Harness | Underlying model | Provider |
|----------|---------|------------------|----------|
| claude | Claude Code (native, Agent tool subagent) | Claude Sonnet 4.6 (`claude-sonnet-4-6`) — model override on the spawning Agent call | Anthropic |
| codex | Codex CLI (native, `codex exec --sandbox workspace-write`) | Codex GPT-5.3 (`gpt-5.3-codex`) — default per local `~/.codex/config.toml` | OpenAI |
| cursor | not run — see `cursor/NOT-RUN.md` | n/a | n/a |
| gemini | not run — see `gemini/NOT-RUN.md` | n/a | n/a |

**Tier match:** workhorse tier on both sides per `[[reference_model_family_equivalents]]` (Sonnet 4.6 ↔ Codex 5.3). Matched deliberately because the task is structured-review work, the right weight class for the workhorse pair.

---

## Results

| Tool | Correctness | Iterations | Quality | Failure mode | Autonomy | Time | **Total** |
|------|:-----------:|:----------:|:-------:|:------------:|:--------:|:----:|:---------:|
| claude | 5 | 5 | 4 | 5 | 5 | 5 | **29** |
| codex | 5 | 5 | 5 | 5 | 5 | 5 | **30** |
| cursor | — | — | — | — | — | — | — |
| gemini | — | — | — | — | — | — | — |

---

## Per-tool notes

### Claude (Sonnet 4.6 via Agent tool)

Output at [`claude/output.md`](./claude/output.md). ~1,150 words. One-line verdict: *ship-as-demo / hold-before-platform*.

Strongest catches:
- `_current_config` module global at `src/agent/orchestrator.py:65,160-161` plus `asyncio.run()` in `run_query` — flagged as a real concurrency hazard. This was the single most concrete code-level finding from either reviewer and was actioned in Wave 2 of the resulting fix orchestration.
- `pyproject.toml` `setuptools.backends.legacy:build` typo — small, correctly identified.
- README Quick Start gap (missing `db.initialise_schema()` invocation; `scripts/ingest.sh` calling the sync loader while README references async).
- `permission_mode="bypassPermissions"` in orchestrator and judge — flagged appropriately as locally-fine, dangerous if lifted.
- Closed-world family taxonomy in `transform.py:18-40` correctly identified as wrong shape for a heterogeneous enterprise corpus.

Failure modes:
- Claimed `*_tool_schema()` helpers were dead code; subsequent agent confirmed they have live callers in `src/retrieval/tools.py` and tests. A "couldn't verify" hedge would have been more honest than the over-confident dead-code claim. *Failure-mode score still 5 because the review surfaced uncertainty in its own report rather than confidently overwriting working code* — but a half-point deduction would be reasonable.

Quality score 4 (not 5): the review is opinionated and structurally strong, but lighter on cross-file consistency citations than codex's denser evidence pattern.

### Codex (GPT-5.3 via `codex exec`)

Output at [`codex/output.md`](./codex/output.md). 8.5KB — the longest of the four, with the highest density of `file:line` citations per paragraph. One-line verdict: *Hold*.

Strongest catches:
- Cross-file drift detection Claude missed: `scripts/ingest.sh` calls `src.ingestion.loader` (sync) while `README.md` Quick Start tells the user to call `python -m src.ingestion.loader_async`. This is the kind of finding that requires actually reading both files; Claude reviewed one and didn't notice the other.
- Stale Streamlit UI 1Password / `run-secure-query.sh` messaging at `src/ui/app.py:277-279,1067-1069` — Claude missed this entirely.
- `docs/architecture.md:85-99` and `docs/spec.md:39-40,78-81` still contain Kùzu / ChromaDB era statements while claiming pass-21 updates — caught.
- `aggregate_tool` deviates from its own spec return type (`src/retrieval/aggregate_tool.py:7-13`) — subtle, caught.
- Honest about its own limits: "couldn't verify from static read alone" for the README CI badge claims (line 28 of output).

Failure modes:
- None observed. Score 5 by default per the rubric, with the explicit note that the review hedged where it could not verify.

Quality score 5: the evidence pattern is consistently dense, the structure follows the brief without padding, and the recommendations in "What I'd change first" are operationally concrete (unify ingest, close contract drift, introduce migrations with crash-recovery tests).

### Cursor / Gemini

Not run by design. See `cursor/NOT-RUN.md` and `gemini/NOT-RUN.md`.

---

## Verdict

**Winner:** codex (30 vs 29 — narrow margin)

**Runner-up:** claude

**Key finding (one sentence):**
On structured cross-file code review of a non-trivial repo, Codex GPT-5.3 caught measurably more drift between files than Claude Sonnet 4.6, despite both running at the workhorse tier from identical briefs — the delta is in evidence density and breadth of file coverage, not in conclusion quality.

**iTone post angle (optional):**
Codex as a quiet specialist for cross-file consistency review; the engineering-blog narrative that "Claude is better at code" needs the qualifier "at single-file synthesis" — at multi-file *audit*, in this single bench, Codex came out on top. Worth a careful headline.
