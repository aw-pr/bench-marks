# Scorecard — BENCH-008

> **Off-format, deliberately.** The six rubric dimensions are not scored here.
> They measure quality, and this bench measures what reaching the *same*
> quality costs. Forcing the rubric onto a lever A/B is what produced
> BENCH-006's 27–27 tie and BENCH-007's saturated 30/30. The harness's own
> metric set is used instead; see `ab/README.md`.
>
> Rows are the two **tier lanes**, not the four subscriptions. cursor/gemini
> are N/A (single-harness tier A/B, no second harness to interpret against).

---

## Metadata

| Field | Value |
|-------|-------|
| Task ID | BENCH-008 |
| Date scored | 2026-08-23 |
| Scorer | orchestrator (Claude Opus 5) |
| Brief | [brief.md](./brief.md) |
| Raw records | `ab/runs/model_tier.jsonl` (12 cells) |
| Harness | `ab/` at `5f14fa9` |

## Tool provenance

| Lane | Harness | Underlying model | Provider |
|------|---------|------------------|----------|
| control | Claude Code `-p` | claude-opus-5 | Anthropic |
| treatment | Claude Code `-p` | claude-sonnet-5 | Anthropic |
| cursor | N/A — single-harness tier A/B | — | — |
| gemini | N/A — single-harness tier A/B | — | — |

Identical prompt, corpus, `--allowedTools` and `--disallowedTools` in both
arms. The only variable is `--model`; every record carries its own argv so
that claim is auditable rather than asserted.

---

## Gate: answer-key pass rate

| Lane | Passed | Rate |
|------|--------|------|
| control (Opus 5) | 6/6 | 100% |
| treatment (Sonnet 5) | 6/6 | 100% |

**No quality separation at all.** Every cell in both arms reached the correct,
complete answer. That is the finding that makes the cost figures meaningful:
the cheaper tier is not buying its saving with errors.

---

## Efficiency (paired per-task medians, n=3 per cell)

| Metric | Opus 5 | Sonnet 5 | Delta |
|---|---:|---:|---:|
| tool calls | 7.5 | 4.5 | **−40.0%** |
| turns | 8.5 | 5.5 | −35.3% |
| cost USD | 0.3852 | 0.1096 | **−71.6%** |
| wall-clock ms | 46,729 | 17,908 | −61.7% |
| output tokens | 2,920 | 1,404 | −51.9% |
| cache-read tokens | 376,250 | 259,932 | −30.9% |

Per task, the cost result is strikingly stable across two deliberately
different shapes:

| Task | Shape | Opus | Sonnet | Cost delta | Tool-call delta |
|---|---|---|---|---|---|
| T1 orbit trace | narrative comprehension, Swift | $0.6499 / 12 calls | $0.1856 / 7 calls | −71.4% | −41.7% |
| T2 viewport consumers | enumerative lookup, Go | $0.1206 / 3 calls | $0.0335 / 2 calls | −72.2% | −33.3% |

Sonnet is cheaper on both counts at once: it costs less per token *and* used
roughly half the output tokens to reach the same answer.

---

## Verdict

**Winner:** Sonnet 5, on both task shapes tested.

**Key finding (one sentence):**
On cold repository comprehension and dependency lookup, Sonnet 5 reached the
same verified answer as Opus 5 in 40% fewer tool calls at 28% of the cost with
no gate failures in either arm, so routing this task class to Opus is paying
roughly 3.5x for an answer the cheaper tier already gets right.

---

## What this does NOT support

Stated explicitly because a two-task, n=3, single-repo corpus invites
over-reading:

- **Not "use Sonnet for everything".** Only two task shapes were tested, both
  read-only comprehension. No code was written, no multi-stage work, no
  refactor, no ambiguous or adversarial task. Item 3's routing guide gains one
  row, not a policy.
- **The tool-call delta is not clean at this n.** Spread overlaps on T1
  (Opus 11/12/15, Sonnet 6/7/12) — Sonnet's worst run matches Opus's median.
  The *cost* delta is solid because it is driven largely by price, which is
  deterministic; the *effort* delta needs more repeats before it is quotable.
- **Single repo.** Both tasks target `fractals-from-the-90s`. A repo with
  different structure or size may route differently.

## Observation worth a follow-up, not yet a finding

In pre-grid smoke runs the tool surface differed: `Agent` was permitted. In
that configuration Sonnet **failed** T1's gate, missing `FractalRenderer`,
after 20 tool calls and one sub-agent delegation. With `Agent` denied it passed
3/3 in 6–12 calls.

If that holds up, permitting sub-agent delegation on a cold comprehension task
made a cheaper model *worse and more expensive* — which is `TOKEN-SPEND-TODO`
item 5's hypothesis arriving from an unexpected direction. It is n=1 and was
not a controlled arm, so it is recorded as an observation. The
`subagent_hygiene` lever in `ab/levers.yaml` is the controlled way to settle
it and is READY to run.
