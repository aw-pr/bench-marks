# Scorecard — BENCH-006

> Scoring rubric and anchor definitions: see `rubric.md`.
> All scores are integers 1–5. Total is the sum of all six dimensions (max 30).
> **Off-format:** this is a tooling A/B on one model, so the rows are the two
> *toolset lanes*, not the four subscriptions. cursor/gemini rows are N/A
> (not void — there is no second model to interpret). Scores reflect the
> headline head-to-head, Exp 1 (cold comprehension trace).

---

## Metadata

| Field | Value |
|-------|-------|
| Task ID | BENCH-006 |
| Date scored | 2026-06-03 |
| Scorer | orchestrator (Claude Opus 4.8) |
| Brief | [brief.md](./brief.md) |
| Finding | [finding.md](./finding.md) |

---

## Tool provenance

| Tool row | Harness | Underlying model | Provider |
|----------|---------|------------------|----------|
| codegraph | Claude Code (native), codegraph MCP only | Opus 4.8 | Anthropic |
| baseline | Claude Code (native), grep + Read only | Opus 4.8 | Anthropic |
| cursor | N/A — single-model tool A/B | — | — |
| gemini | N/A — single-model tool A/B | — | — |

Both lanes are the **same model**; the only variable is the toolset. Any
delta is attributable to the tools, not the model.

---

## Results

| Lane | Correctness | Iterations | Quality | Failure mode | Autonomy | Time | **Total** |
|------|:-----------:|:----------:|:-------:|:------------:|:--------:|:----:|:---------:|
| codegraph | 5 | 5 | 4 | 3 | 5 | 5 | **27** |
| baseline | 4 | 4 | 4 | 5 | 5 | 5 | **27** |

---

## Per-lane notes

### codegraph (Claude Code + codegraph MCP)

Reached the correct, *most complete* trace in 2 round-trips, volunteering
callers, covering tests, and the Swift parity mirror unprompted
(Correctness 5, Iterations 5). Failure mode is its weakness (3): graph
edges can be silently-confident — `callees` conflated type-uses with
calls and missed a value-receiver method call, and the `explore`
blast-radius summary mislabeled caller file distribution. High token
volume per call (returns whole files) did not cost a Quality point but is
worth noting.

### baseline (Claude Code + grep/Read)

Correct on the core path (4) but needed extra greps to match codegraph's
completeness, in 5 calls / 3 round-trips (Iterations 4). Failure mode is
its strength (5): an empty grep is loud and obvious — no silent-wrong
risk. Token-frugal (pulls only chosen ranges).

### cursor / gemini

N/A. This is a single-model tooling A/B; there is no second model to
interpret against, so these lanes are not run (distinct from the Cursor
*void* rule, which applies to unrecorded-model rows in a real
four-subscription bench).

---

## Verdict

**Winner:** codegraph *(on the task purpose — cold comprehension &
impact; practical winner despite the rubric tie)*

**Runner-up:** baseline (grep/Read)

**Key finding (one sentence):**
On cold comprehension and "what depends on X", codegraph wins decisively
on round-trips and free blast-radius/cross-language context, while
grep/Read wins token-frugality and failure-mode honesty — so the rubric
ties at 27 but the practical rule is **codegraph-first, grep-verify**.

**iTone post angle (optional):**
"A code-graph MCP doesn't make the model smarter — it changes the *failure
mode*. It trades grep's loud empty-result for a graph's quiet
confidently-wrong edge. The win is real on cold navigation; the discipline
is verifying the edge before you trust it."
