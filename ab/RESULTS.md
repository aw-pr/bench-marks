# A/B results

One section per lever. A lever appears here only once it has run; a lever that
cannot run honestly says so and why, rather than being quietly absent.

Raw records are in `runs/<lever>.jsonl`, one JSON object per cell.

---

## model_tier — Opus 5 vs Sonnet 5

**Status:** run 2026-08-23, 12 cells (2 tasks x 2 arms x n=3), harness `5f14fa9`.
**Full write-up:** [BENCH-008](../tasks/BENCH-008/scorecard.md)

| Metric | Opus 5 | Sonnet 5 | Delta |
|---|---:|---:|---:|
| gate pass | 6/6 | 6/6 | none |
| tool calls | 7.5 | 4.5 | −40.0% |
| cost USD | 0.3852 | 0.1096 | −71.6% |
| wall-clock | 46.7s | 17.9s | −61.7% |

No quality separation, so the cost delta is real saving rather than a cheaper
wrong answer. Holds across both task shapes (−71.4% narrative, −72.2%
enumerative).

**Routing guide, first row:** cold repository comprehension and dependency
lookup route to Sonnet. Scope this narrowly — see the scorecard's "what this
does not support".

---

## codegraph — BLOCKED, not run

`codegraph` is not installed on this machine. `/opt/homebrew/bin/codegraph`
does not exist; node has been upgraded to 26.5.0 and the global package set no
longer contains it. This is the breakage `TOKEN-SPEND-TODO.md` predicted:
*"it will break on a node upgrade and need re-linking."*

`bin/preflight.sh` refuses the lever. That refusal is the point of the gate:
with codegraph absent, the treatment arm would have silently used grep/Read —
the control arm's toolset — both arms would have produced identical numbers,
and this file would now report "no measurable difference" for a lever that
never ran. Item 1's rollout decision would have been settled by a tool that was
not there.

Still outstanding while it is blocked:

- Three repos register a dead server in `.mcp.json`: `bench-marks`,
  `fractals-from-the-90s`, `token-maxing`. Two of those registrations were
  committed this month.
- The global `codegraph-first` skill still instructs agents to reach for it
  first, citing BENCH-006.
- The fractals index is stale regardless: built 2026-07-20, 39 files changed
  since. `preflight.sh` would refuse on that alone.

**To unblock:** reinstall codegraph, re-index the target repo, then
`bin/run-grid.sh codegraph 3`. The preflight will confirm all three conditions
before a single cell runs.

---

## repo_priming — READY, not yet run

Fixtures exist: each corpus task carries a `priming` block injected into the
treatment arm via `--append-system-prompt`. `TOKEN-SPEND-TODO` item 4.

## subagent_hygiene — READY, not yet run

Promoted in priority by an observation from BENCH-008's smoke runs: with
`Agent` permitted, Sonnet failed T1's gate after 20 tool calls and one
delegation; with `Agent` denied it passed 3/3 in 6–12 calls. If controlled
running reproduces that, permitting delegation on cold comprehension makes a
model both worse and more expensive. `TOKEN-SPEND-TODO` item 5.

## prompt_cache — OBSERVATIONAL only

The CLI exposes no flag to disable prompt caching, so there is no control arm
to build and this can never be a true A/B by this method. Recorded so the lever
is not mistaken for untested when it is untestable here. `cache_read_input_tokens`
is captured on every run; BENCH-008 saw 376k (Opus) and 260k (Sonnet) cache
reads per task-pair, so caching is demonstrably active.
