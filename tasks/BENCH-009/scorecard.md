# Scorecard — BENCH-009

> **Off-format, deliberately**, for the reason BENCH-008 gives: the six rubric
> dimensions measure quality, and this bench measures what reaching the *same*
> answer costs. The harness's own metric set is used instead; see
> `ab/README.md`.
>
> Rows are the two **tier lanes**, not the four subscriptions.

---

## Metadata

| Field | Value |
|-------|-------|
| Task ID | BENCH-009 |
| Date scored | 2026-11-15 |
| Scorer | orchestrator (Claude Opus 5.5) |
| Brief | [brief.md](./brief.md) |
| Raw records | `ab/runs/codex_tier.jsonl` (40 cells) |
| Harness | `ab/` at `acd529e` |

## Tool provenance

| Lane | Harness | Underlying model | Provider |
|------|---------|------------------|----------|
| control | Codex CLI `exec --sandbox read-only` | gpt-5.6-terra, reasoning effort medium | OpenAI |
| treatment | Codex CLI `exec --sandbox read-only` | gpt-5.6-luna, reasoning effort medium | OpenAI |
| claude, cursor, gemini | N/A — single-harness tier A/B | — | — |

Identical prompt, corpus, working directory and sandbox in both arms. The
only variable is `-m`, and every record carries its own argv.

---

## Credits

`credits_spent` is 0 on all 40 records, and the credit balance was unchanged
across the night. No paid credits were drawn.

---

## Gate: answer-key pass rate

| Task | Terra | Luna |
|------|------:|-----:|
| T1 orbit trace | 4/5 | 5/5 |
| T2 viewport consumers | 5/5 | 5/5 |
| T3 Go package types | 5/5 | 5/5 |
| T4 Swift declared types | 5/5 | 3/5 |
| **total** | **19/20** | **18/20** |

**No separation.** Terra's miss named the precision type as "fixed-point
bignum" rather than `BigFixed`. Luna's two misses both left `HUDSnapshot` out
of a fourteen-type listing for one file. The same Terra configuration, run
again an hour later as `codex_effort`'s treatment arm, went from 4/5 to 2/5 on
T1, so a two-pass gap on one task is inside what identical arms produce here.

---

## Efficiency

Paired per-task medians over passing runs, from `ab/bin/analyse.py`, except the
quota row, which is a sum: `quota_pct_used` moves in whole points, so a single
cell usually reads 0, 1 or 2 and its median is mostly ties.

| Metric | Terra | Luna | Delta |
|---|---:|---:|---:|
| 5-hour window, sum over 20 cells | 20 pts | 11 pts | **-45%** |
| output tokens | 912 | 1,435 | +57.4% |
| reasoning tokens | 232 | 458 | +97.6% |
| tool calls | 2.5 | 3.5 | +40.0% |
| input tokens | 106,032 | 130,514 | +23.1% |
| wall-clock | 27.0s | 18.0s | -33.3% |

Per task, the quota saving holds in direction everywhere:

| Task | Terra quota | Luna quota | Output-token delta | Reasoning-token delta |
|---|---:|---:|---:|---:|
| T1 orbit trace | 7 | 5 | +88.3% | +123.3% |
| T2 viewport consumers | 3 | 1 | +77.4% | +79.6% |
| T3 Go package types | 6 | 3 | +61.3% | +68.8% |
| T4 Swift declared types | 4 | 2 | +54.9% | +137.4% |

**Quota contamination.** 13 of the 40 cells overlapped a `codex exec` worker
from another repository, drawing on the same window. Token counts are per
thread and unaffected. On the 27 cells that ran alone: Terra 12 points over 13
cells (0.92 a cell), Luna 4 points over 14 (0.29 a cell). The gap widens rather
than closes.

---

## Verdict

**Winner:** Luna, on cost, at no measurable cost to the gate.

**Key finding (one sentence):**
On cold repository comprehension, Luna at medium effort reached the answer key
18 times in 20 against Terra's 19 and drew 45% less of the 5-hour window while
spending 57% more output tokens and twice the reasoning tokens, so on Codex
the token count is the wrong proxy for what an answer costs.

**Routing guide, first Codex row:** cold repository comprehension routes to
Luna at medium effort.

---

## What this does NOT support

- **Not "Luna for everything".** Four read-only comprehension tasks on one
  repository. No edits, no multi-step work.
- **Not a precise saving.** The quota counter has one-point resolution and a
  third of the cells shared the window with another job. The direction is
  solid: all four tasks, and wider on the clean cells. Quote "about half the
  quota", not "45.0%".
- **Not a price.** Quota share is what a Plus subscription pays. It does not
  convert to dollars, and it is not comparable with the Claude levers'
  `total_cost_usd`.
- **T4 is the watch item.** Both Luna misses were one omission on an exhaustive
  listing. If Luna is routed more widely, exhaustive enumeration over large
  files is where to check it first.

## Related

`codex_effort` ran the same night: Terra at `high` against `medium`. It came
back inconclusive and leaves the `high` default in place. See `ab/RESULTS.md`.
