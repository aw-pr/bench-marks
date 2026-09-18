# The A/B harness

Answers one question per lever: **does this lever change the cost of reaching
the same answer, and by how much?**

It is not a second rubric. `rubric.md` scores *quality*, and quality is not what
these levers move — CodeGraph, prompt caching, model tiering and repo priming
almost all leave the answer identical and change what it cost to get there.
Trying to read them off the quality rubric is what produced BENCH-006's 27–27
tie and BENCH-007's saturated 30/30. The rubric was not wrong; it was being
asked a question it cannot answer.

## What this fixes about BENCH-006

BENCH-006 was the right experiment run once, by hand. Its own brief lists the
limits: *"single-session, self-measured, no metered tokens"*. Each is now
closed:

| BENCH-006 | Here |
|---|---|
| n=1 per arm | n≥3 per cell, median and spread reported |
| self-reported token counts | metered: `claude -p --output-format json` returns real `usage` and `total_cost_usd` |
| tool calls counted by hand | counted from `stream-json` `tool_use` blocks |
| one lever (codegraph) | a lever registry; each is one row in `levers.yaml` |
| correctness scored 1–5 | correctness is a **gate**, not a score — see below |

## Method

**Correctness is a gate, not a score.** Every corpus task carries a
machine-checkable answer key. A run passes or fails. Efficiency is compared
only across *passing* runs, because the cost of reaching a wrong answer is not
a number worth comparing. The per-arm failure rate is reported separately and
is itself a result: a lever that halves cost while doubling the failure rate
has not helped.

**Paired.** Same task, same model, same prompt. Arms differ by exactly one
lever. Runs are aggregated per task before the arms are compared, so an
unusually hard task cannot swing the result by landing in one arm more often.

Read the headline row carefully: it compares each arm's median of per-task
medians, which is not the same as the median of per-task deltas. On a two-task
corpus the larger task dominates it, so a lever that helps one task and not the
other still shows a large headline figure. `analyse.py` prints the per-task
spread beneath every metric and marks the metrics whose tasks disagree in sign.
When they disagree, the spread is the result and the headline is a summary of
something that did not happen twice.

**Repeated.** n≥3 per cell. A single run cannot distinguish a real effect from
sampling noise, which is the main reason BENCH-006's split verdict had to be
argued from the transcript rather than read off the numbers.

**Cold per run.** Every run is a fresh `claude -p` session. Task order is
randomised across repeats so no arm systematically benefits from a warm cache.
Note that `cache_read_input_tokens` is non-zero even on a trivial cold prompt —
that is the shared system-prompt cache, identical across arms, so it is a
constant rather than a confound. It is recorded anyway.

## Metrics

Captured per run, all from the CLI's own accounting:

| Field | Source | Why |
|---|---|---|
| `passed` | answer-key check | the gate |
| `tool_calls` | `stream-json` `tool_use` count | the round-trip cost BENCH-006 cared about |
| `num_turns` | `usage` JSON | assistant turns |
| `input_tokens`, `output_tokens` | `usage` | raw volume |
| `cache_read_input_tokens`, `cache_creation_input_tokens` | `usage` | whether caching is doing anything |
| `total_cost_usd` | CLI | metered, not estimated |
| `duration_ms`, `duration_api_ms`, `ttft_ms` | CLI | wall-clock and latency |

## Pre-flight is a hard gate

`bin/preflight.sh` refuses to run a lever whose machinery is absent, because a
missing tool does not fail loudly — it silently degrades the treatment arm into
the control arm, and the experiment then reports "no difference" for a lever
that never ran. That is a false negative that would kill a rollout on
manufactured evidence.

This is not hypothetical. On 2026-08-23, when this harness was written,
`codegraph` was **not installed** — `/opt/homebrew/bin/codegraph` did not
exist, exactly as `token-maxing/TOKEN-SPEND-TODO.md` warned it would ("it will
break on a node upgrade and need re-linking"). Three repos
(`bench-marks`, `fractals-from-the-90s`, `token-maxing`) still registered it in
`.mcp.json`, and the `codegraph-first` skill still instructed agents to prefer
it. The fractals index was also 39 changed files stale, last built 2026-07-20.

Had the codegraph A/B simply been run that day, both arms would have used
grep/Read, the result would have read "no measurable difference", and the
rollout decision in `TOKEN-SPEND-TODO.md` item 1 would have been settled
wrongly by a tool that was not there.

The pre-flight therefore checks, per lever: the binary resolves, the MCP server
answers, and any index is newer than the repo's last commit. Any failure is a
refusal, never a warning.

## Layout

```
ab/
  README.md          this file
  levers.yaml        lever registry: how each is switched on and off
  bin/preflight.sh   per-lever machinery check; refuses rather than warns
  bin/run-cell.sh    one run: one task x one arm x one repeat
  bin/analyse.py     aggregate runs into per-lever arm medians
  tasks/*.yaml       corpus: prompt + machine-checkable answer key
  runs/*.jsonl       raw run records, one JSON object per run
```

## Running it

```sh
ab/bin/preflight.sh <lever>              # refuses if the machinery is absent
ab/bin/run-cell.sh <task> <lever> <arm> <repeat>
ab/bin/analyse.py ab/runs/*.jsonl        # arm medians, per-task spread, failure rates
```

Results land in `RESULTS.md` and a `BENCH-NNN` scorecard is written only when a
lever produces a decision, so the ledger stays a record of conclusions rather
than of runs.
