# The A/B harness

Answers one question per lever: **does this lever change the cost of reaching
the same answer, and by how much?**

## The vocabulary

Five words do all the work here, so they are worth fixing up front.

- **Lever** -- one thing you can switch on or off: a cheaper model, an
  architecture map in the system prompt, a search tool on PATH.
- **Arm** -- one side of the comparison. *Control* has the lever off,
  *treatment* has it on. Nothing else may differ between them.
- **Cell** -- one task, in one arm, run once. A cell is the unit that gets
  metered and written to `runs/<lever>.jsonl`.
- **Repeat (`n`)** -- how many cells each task gets in each arm. `n=5` means
  five runs of every task in every arm.
- **Gate** -- correctness as pass/fail against an answer key, never a score.
  Cost is compared only across runs that passed, because the cost of reaching a
  wrong answer is not a number worth comparing.

## The corpus

Four tasks, all read-only questions about one repository, `fractals-from-the-90s`
(a Go core and a SwiftUI app). They are referred to by number everywhere else.

| Task | Shape | The question |
|---|---|---|
| T1 orbit trace | Narrative trace | How a reference orbit is produced and bound into the render path, and which Swift files consume it |
| T2 viewport consumers | Enumerative lookup | Which Go packages depend on `internal/viewport` |
| T3 Go package types | Fan-out listing | The exported types of every package under `internal/` (57 files, 13 packages) |
| T4 Swift declared types | Fan-out listing | The types declared in every Swift source file (17 files) |

Each task's answer key is a short list of names the final answer must contain,
matched as substrings. T1 and T2 are the default pair for a Claude lever. T3 and
T4 allow delegation to a sub-agent, so among the Claude levers only
`subagent_hygiene` may use them; the Codex levers run all four.

That repository is private. The prompts and answer keys are in `tasks/*.yaml`
and every raw record is in `runs/`, so the analysis can be repeated by anyone,
but the cells cannot be re-run without the checkout. That is the one part of
this harness a reader has to take on trust.

The models are named as their vendors name them. Opus 5, Sonnet 5 and Haiku 4.5
are Anthropic's tiers, largest to smallest; the context-hygiene lever ran on
Sonnet 5.5 (`claude-sonnet-5-5`). Terra and Luna are the two tiers of
OpenAI's GPT-5.6 that the Codex CLI offers (`gpt-5.6-terra` and
`gpt-5.6-luna`); Terra is the larger.

## Reading a lever

Each lever is one entry in `levers.yaml` and one section in `RESULTS.md`. The
entry gives the question, the two arms, what pre-flight must find before the
lever may run, and a `status`:

| Status | Meaning |
|---|---|
| `RUN` | The arms differed as intended and the result can be read |
| `REFUTED` | Ran cleanly, and the claim the lever tested did not hold |
| `BANKED` | Ran cleanly, and the saving turned out to be in place already |
| `INCONCLUSIVE` | Ran, but the arms did not differ in practice or the gap is inside the noise |
| `OBSERVATIONAL` | No control arm can be built, so it is recorded but is not an A/B |
| `RETIRED` | Could not be run, and the reason is recorded |

The status describes the experiment. The verdict in the top-level README's table
describes the claim, which is why a lever with status `RUN` can carry the
verdict "refuted": the experiment worked and the claim lost.

A section in `RESULTS.md` reports the gate first, as passes out of cells per
arm, then a table of arm medians with the delta and the per-task spread. Read
the gate before the delta, and the per-task spread before the headline.

## Why a gate and not the rubric

It is not a second rubric. `rubric.md` scores *quality*, and quality is not what
these levers move: model tiering, prompt caching and repo priming mostly leave
the answer identical and change what it cost to get there. Trying to read them
off the quality rubric is what produced a 27-27 tie on one task and a saturated
30/30 on another. The rubric was not wrong, it was being asked a question it
cannot answer.

## What this fixes about BENCH-006

BENCH-006 was the right experiment run once, by hand. Its own brief lists the
limits: *"single-session, self-measured, no metered tokens"*. Each is now
closed:

| BENCH-006 | Here |
|---|---|
| n=1 per arm | n≥3 per task and arm, median and spread reported |
| self-reported token counts | metered: `claude -p --output-format json` returns real `usage` and `total_cost_usd` |
| tool calls counted by hand | counted from `stream-json` `tool_use` blocks |
| one lever (codegraph) | a lever registry; each is one row in `levers.yaml` |
| correctness scored 1-5 | correctness is a **gate**, not a score -- see below |

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

**Repeated.** n≥3 per task and arm. A single run cannot distinguish a real effect from
sampling noise, which is the main reason BENCH-006's split verdict had to be
argued from the transcript rather than read off the numbers.

**Cold per run.** Every run is a fresh `claude -p` session (a fresh
`codex exec` session for a `codex_*` lever, see below). Task order is
randomised across repeats so no arm systematically benefits from a warm cache.
Note that `cache_read_input_tokens` is non-zero even on a trivial cold prompt --
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
| `prefix_tokens` | first assistant message's `usage` | the whole turn-1 prompt: system prompt, tool schemas, task; what a context lever moves |
| `mcp_servers_connected`, `mcp_tools`, `tool_search` | `stream-json` `init` event | what the session actually loaded, so a record proves its arm |

### The Codex backend

A lever whose name starts `codex_` runs the same task through
`codex exec --json --sandbox read-only` instead of `claude -p`. The task, the
working directory, the gate and the record shape are unchanged, so the two
backends compare field for field. The read-only sandbox stands in for the
Claude tasks' tool allowlist, which Codex does not have.

The fields come from Codex's own events: `tool_calls` counts completed
`command_execution` items and the token fields come from `turn.completed`.
`total_cost_usd` is null, because a subscription reports no price. The record
also names its `backend`, `reasoning_effort` and `thread_id`, and adds three
measurement fields:

| Field | Source | Why |
|---|---|---|
| `reasoning_output_tokens` | `turn.completed` usage | reasoning effort is one of the levers |
| `quota_pct_used` | 5-hour window before and after the cell, read by `bin/codex-limits.sh` from the session rollout | what share of the window this answer cost |
| `credits_spent` | credit balance before and after | must be 0: above 100% of the window Codex bills paid credits without warning |

`quota_pct_used` is only clean when nothing else is using Codex, which is why
these levers run overnight. Overnight is not a guarantee: on the first night 24
of 80 cells shared the window with another repository's `codex exec` worker, so
check the session rollouts for foreign threads before quoting quota. It is also
coarse, the change in a whole-number percentage, so one cell usually reads 0, 1 or 2;
sum it over an arm rather than taking a median.

## Overnight runs

`bin/overnight.sh` works through `overnight.queue` unattended, between 23:00
and 06:00 local time by default. Before every cell it checks the Codex rate
limits: it sleeps when the 5-hour window reaches 90% and stops for the night if
the credit balance falls, if the weekly window reaches 95%, or if three cells in
a row error. A non-Codex lever runs only while Anthropic seven-day utilisation
is under 90%. Each lever's randomised plan is written once to
`runs/<lever>.plan` and consumed a line at a time, so a night cut short resumes
where it stopped. The thresholds are environment variables (`OVERNIGHT_*`) at
the top of the script.

`bin/install-overnight.sh` schedules it as a launchd job (macOS) that fires
daily at 22:55 under `caffeinate`, and `--remove` takes it out again.

## Pre-flight is a hard gate

`bin/preflight.sh` refuses to run a lever whose machinery is absent, because a
missing tool does not fail loudly -- it silently degrades the treatment arm into
the control arm, and the experiment then reports "no difference" for a lever
that never ran. That is a false negative that would kill a rollout on
manufactured evidence.

This is not hypothetical. The first lever this harness was built for,
`codegraph`, turned out not to be installed on the day it was due to run, while
40 `.mcp.json` files still registered it and a skill still told agents to prefer it.
Without the pre-flight both arms would have quietly used grep, the result would
have read "no measurable difference", and a rollout decision would have been
settled by a tool that was not there. The full account is in the codegraph
section of `RESULTS.md`.

The pre-flight therefore checks, per lever: the binary resolves, the MCP server
answers, and any index is newer than the repo's last commit. For a context
lever it launches each arm once on a trivial prompt and refuses unless the two
arms load different tool sets. Any failure is a refusal, never a warning.

## Layout

```
ab/
  README.md          this file
  levers.yaml        lever registry: how each is switched on and off
  bin/preflight.sh   per-lever machinery check; refuses rather than warns
  bin/run-cell.sh    one run: one task x one arm x one repeat
  bin/run-grid.sh    one lever's whole grid, in randomised order
  bin/analyse.py     aggregate runs into per-lever arm medians
  bin/codex-limits.sh   latest Codex rate-limit snapshot, read from a rollout
  bin/overnight.sh      unattended runner with the quota governor
  bin/install-overnight.sh  launchd job for overnight.sh (macOS)
  overnight.queue    what overnight.sh runs, top to bottom
  repos.local.sh.example  maps each task's repo_key to a local checkout
  tasks/*.yaml       corpus: prompt + machine-checkable answer key
  runs/*.jsonl       raw run records, one JSON object per run
```

## Running it

```sh
cp ab/repos.local.sh.example ab/repos.local.sh   # then point each key at a checkout
ab/bin/preflight.sh <lever>              # refuses if the machinery is absent
ab/bin/run-cell.sh <task> <lever> <arm> <repeat>
ab/bin/run-grid.sh <lever> <repeats>     # every cell, randomised
ab/bin/analyse.py ab/runs/*.jsonl        # arm medians, per-task spread, failure rates
```

The runs need `claude` (or `codex` for a `codex_*` lever), `yq`, `jq` and `timeout` on
PATH. The corpus repository is private (see "The corpus" above), so to run
cells yourself, write task files against your own repository with your own
answer keys. `analyse.py` needs only Python 3 and the committed records.

Results land in `RESULTS.md` and a `BENCH-NNN` scorecard is written only when a
lever produces a decision, so the ledger stays a record of conclusions rather
than of runs.
