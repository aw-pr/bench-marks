# A/B results

One section per lever. A lever appears here only once it has run; a lever that
cannot run honestly says so and why, rather than being quietly absent.

Raw records are in `runs/<lever>.jsonl`, one JSON object per cell.

## Routing guide

The one piece of this file meant to be acted on. Every row is about **cold
repository comprehension**, because that is what the corpus contains; nothing
here speaks to bulk edits, classification or extraction.

| Backend | Task shape | Cheapest tier that holds the gate | Evidence |
|---|---|---|---|
| Claude | Narrative trace: follow a value through a call chain | Sonnet 5 | `model_tier` (Opus 5 buys nothing), `model_tier_haiku` (Haiku fails 3 of 5) |
| Claude | Enumerative lookup: which callers touch X | Sonnet 5 | `model_tier`; Haiku holds the gate but costs 75.8% more |
| Codex | All four corpus shapes | Luna, medium effort | `codex_tier`: gate 18/20 against Terra's 19/20, 45% less of the 5-hour window; both misses on the Swift type listing |

Read as: **route down from Opus to Sonnet, and stop there.** Opus 5 showed no
quality advantage over Sonnet on either shape while costing 3.5x more. One tier
lower the gate starts failing on narrative work, and on enumerative work the
cheaper tier is not actually cheaper.

On Codex, **route down from Terra to Luna.** Luna spends more tokens than Terra
and still draws far less of the 5-hour window. Leave Terra's reasoning effort at
`high`: `codex_effort` did not show that `medium` holds the gate.

A note on the noise floor, since it governs every figure below: two grep-vs-grep
runs of the same configuration disagreed by 33 percentage points, which puts the
harness floor at roughly +/-20% at n=3 over two tasks. A delta smaller than that
is not an effect. Where a lever's two tasks disagree in sign, the per-task
spread is the result and the headline is a summary of something that did not
happen twice.

---

## Context hygiene -- mcp_prune and tool_deferral

**Status:** run 2026-11-15, 40 cells (2 levers x 2 tasks x 2 arms x n=5) on
Sonnet 5.5 (`claude-sonnet-5-5`), Claude Code 2.1.325, harness `496c026`. This
is `TOKEN-SPEND-TODO` item 6, split in two because the harness takes two arms.

**The claim.** Every connected MCP server's tool schemas sit in context before
any work starts, so pruning the servers a task does not need
(`--strict-mcp-config`) cuts cost without touching the gate.

**The regime measured, which decides the answer.** Tool search is on by default
in a headless `claude -p` on this CLI: MCP tools are listed by name and their
schemas load only when the model calls `ToolSearch`. The operator's headless
setup loads two user-scope servers, a notes vault and a device controller, 24
tools between them; the fractals checkout registers no project server. Both levers
share one control, that setup as it stands. `mcp_prune` adds
`--strict-mcp-config` with no config. `tool_deferral` sets
`ENABLE_TOOL_SEARCH=false` for the one process, which turns deferral off without
touching a settings file.

### What each configuration puts in front of every turn

The turn-1 prompt (system prompt, tool schemas and task) is deterministic per
configuration: every cell in an arm recorded the same figure, and the preflight
probes reproduced it to the token. Measured on a trivial prompt, with the
cells' own tool flags:

| Configuration | Turn-1 prompt | Against the default |
|---|---:|---:|
| Default: 2 MCP servers, tool search on | 29,251 | -- |
| `--strict-mcp-config`, tool search on | 28,736 | -515 (-1.8%) |
| `--strict-mcp-config`, tool search off | 43,942 | +14,691 |
| Default MCP servers, tool search off | 49,809 | +20,558 (+70.3%) |

Read across the rows: fully loaded, the 24 MCP schemas cost 5,867 tokens a turn
(49,809 against 43,942). Deferred, they cost 515. **Tool search already removes
91% of what pruning was meant to remove.** And most of what tool search removes
is not MCP at all: 15,206 tokens a turn are Claude Code's own deferrable tools
(43,942 against 28,736), which no MCP config can touch. The third row is a
probe, not an arm; it was not run as cells.

### mcp_prune -- banked by tool search

| Metric | Default | Pruned | Delta | Per task |
|---|---:|---:|---:|---|
| gate | 9/10 | 10/10 | -- | the one miss is T1, `BigFixed` |
| turn-1 prompt | 29,303 | 28,788 | **-1.8%** | -1.8% on both, every cell |
| cost USD | 0.0539 | 0.0626 | +16.2% | T1 +18.0%, T2 -1.2%, disagree |
| cache read tokens | 94,298 | 112,158 | +18.9% | T1 +28.3%, T2 -1.8%, disagree |
| tool calls | 3.5 | 4.0 | +14.3% | T1 +16.7%, T2 flat |
| wall-clock | 11.7s | 12.2s | +4.0% | T1 +4.6%, T2 flat |

The headline says pruning cost 16% more. It did not: the pruned arm happened to
take one more tool call at the median on T1, and the extra turns that call
bought outweigh a 515-token prefix many times over. The two controls below show T1 swinging by that much between
identical arms. T2 is the clean task here, one Grep and two turns in every cell
of both arms, and on T2 pruning saved exactly what the prefix predicts: 1,030
cache-read tokens (two turns of 515) and 1.2% of cost.

So the lever works and is worth about 2%: real, deterministic, and an order of
magnitude under the noise floor of any task that varies its own path. Nothing
a pruned config saves here would show up on a bill.

### tool_deferral -- this is where item 6 was banked

| Metric | Deferred (default) | All schemas loaded | Delta | Per task |
|---|---:|---:|---:|---|
| gate | 10/10 | 10/10 | -- | -- |
| turn-1 prompt | 29,303 | 49,861 | **+70.2%** | T1 +70.1%, T2 +70.2% |
| cache read tokens | 109,766 | 184,199 | +67.8% | T1 +66.9%, T2 +70.2% |
| cost USD | 0.0523 | 0.0611 | **+16.9%** | T1 +14.1%, T2 +42.1% |
| tool calls | 3.0 | 4.0 | +33.3% | T1 +40.0%, T2 flat |
| wall-clock | 11.9s | 12.4s | +4.4% | T1 +4.8%, T2 +2.0% |

Turning deferral off costs more on both tasks, in the same direction on every
token and cost metric. The headline +16.9% sits just under the noise floor;
read T2 instead, which is behaviourally identical in both arms (one Grep, two
turns, every cell) and so measures nothing but the prefix: **+42.1% cost**, the
cells spread across 0.0099-0.0103 against 0.0129-0.0147. On T1 the same prefix
is diluted by more turns of output and tool results, and lands at +14.1%.
Cost rises less than tokens because cache reads are the cheapest tokens on the
bill; the extra 20k tokens a turn are almost all cache reads.

### The two controls are the same configuration

Both levers' control arms are the default setup, run minutes apart, one grid
after the other. Between them: turn-1 prompt identical, T2 cost +0.1%, T1 tool calls -16.7%, T1 cache
reads +23.8%, T1 cost -3.3%, gate 9/10 against 10/10. T2 is near-deterministic
and T1 is not, which is why T1 deltas of the sizes above cannot be read and T2
deltas can.

### What this means for item 6

**Pruning MCP servers per session: banked, do not bother.** With tool search
on, the 24 schemas the operator loads cost 515 tokens a turn, about 2% of a
cheap task and less of an expensive one. `--strict-mcp-config` is still the
right hygiene for a reproducible headless run, because it pins what loads, but
not as a spend lever.

**Prefer deferred tool loading: already the default, and worth keeping.**
Turning it off adds 70% to every turn's prompt and 14% to 42% to the cost of
the same correct answer, with the gate unchanged. The one action this result
supports is a negative one: never set `ENABLE_TOOL_SEARCH=false`, and treat any
harness that cannot defer (an SDK session handed every tool up front, an older
CLI) as the regime where pruning pays, at about 5.9k tokens a turn for these
24 tools.

**Scope.** Two tasks, one repository, one model, two MCP servers. A setup
with many more servers raises the residual roughly in proportion, about 21
tokens a tool here, and would need hundreds of tools to reach the noise floor. The deferral-off regime
was measured with these 24 tools only. `duration_ms` is the CLI's own figure;
it did not move, and process start-up, which is where MCP servers launch, was
not timed.

**Raw:** `runs/mcp_prune.jsonl`, `runs/tool_deferral.jsonl`. Each record
carries `prefix_tokens` and what the session loaded (`mcp_servers_connected`,
`mcp_tools`, `tool_search`), so every cell proves its arm.

---

## Reading the Codex levers

The two Codex levers ran unattended on the night of 2026-10-10, 22:01 to 01:13
UTC, through `bin/overnight.sh` at harness `acd529e`. Four things about how
they were measured apply to both sections below.

**No paid credits were drawn.** `credits_spent` is 0 on all 80 records, and the
credit balance was the same at the end of the night as at the start.

**The quota figure is coarse.** `quota_pct_used` is the change in a
whole-number percentage of the 5-hour window, so a single cell usually reads 0, 1 or 2
and a median of it is mostly ties. Quota is therefore reported here as the sum
over an arm's cells, which is accurate to a point or two, and the analyser's
median row is quoted only for its direction.

**The night was not quiet.** A Codex worker from another repository ran
`codex exec` from 21:58 to 22:02 and from 22:14 to 22:22 UTC, drawing on the
same window. 24 of the 80 cells overlap it. Token counts are per thread and
unaffected; quota is not. Each section gives the quota sums over all cells and
over the cells that ran alone, and the two agree in direction.

**The noise floor has a Codex measurement.** Terra at medium effort is the
control arm of `codex_tier` and the treatment arm of `codex_effort`: the same
configuration, run twice an hour apart. Between those two runs the per-task
medians moved by up to +45% on output tokens and from -32% to +42% on reasoning
tokens, with mixed signs, and the gate went from 19/20 to 16/20. A delta inside
that is not an effect, and a gate gap of three passes in twenty is not a
separation.

---

## codex_tier -- Terra vs Luna, both at medium effort

**Status:** run 2026-10-10, 40 cells (4 tasks x 2 arms x n=5).

**The gate did not separate the arms.**

| Task | Terra | Luna |
|---|---:|---:|
| T1-orbit-trace (narrative) | 4/5 | 5/5 |
| T2-viewport-consumers (enumerative) | 5/5 | 5/5 |
| T3-go-package-types (fan-out, Go) | 5/5 | 5/5 |
| T4-swift-declared-types (fan-out, Swift) | 5/5 | 3/5 |
| **total** | **19/20** | **18/20** |

Terra's miss traced the orbit correctly and called `BigFixed` "fixed-point
bignum" without naming it. Luna's two misses are the same omission twice: its
listing for `FractalMetalView.swift` named fourteen types from that file and
left out `HUDSnapshot`. A 3/5 against a 5/5 on one task is inside what the
same Terra configuration did across two runs (T1 4/5, then 2/5), so it is a
watch item rather than a routing exclusion.

**Luna spends more tokens and draws less quota.** Paired medians over passing
runs, from `analyse.py`, except the quota row:

| Metric | Terra | Luna | Delta | Per task |
|---|---:|---:|---:|---|
| 5-hour window, summed over the arm's 20 cells | 20 pts | 11 pts | **-45%** | T1 7 to 5, T2 3 to 1, T3 6 to 3, T4 4 to 2 |
| output tokens | 912 | 1435 | +57.4% | +54.9% to +88.3%, all four |
| reasoning tokens | 232 | 458 | +97.6% | +68.8% to +137.4%, all four |
| tool calls | 2.5 | 3.5 | +40.0% | T1-T3 +100% to +125%, T4 flat |
| input tokens | 106032 | 130514 | +23.1% | T4 -4.8%, disagrees |
| wall-clock | 27.0s | 18.0s | -33.3% | T2 +28.6%, disagrees |

On the 27 cells that ran alone the gap is wider, not narrower: Terra drew 12
points over 13 cells (0.92 a cell) and Luna 4 points over 14 (0.29 a cell).
Per passing answer over all cells, Terra cost 1.05 points and Luna 0.61. The
analyser's median row reads 1.0 against 0.5, the same direction at a
resolution that cannot carry a magnitude.

Luna's output and reasoning deltas are beyond the Codex noise floor and agree in
sign on all four tasks; its quota saving agrees in direction on all four. **The two
results together are the finding: across models, fewer tokens is not less
quota.** Luna explored more, with twice the reasoning tokens and more tool
calls, and the window charged it a little over half as much for the answer.

**Routing:** cold repository comprehension on Codex routes to Luna at medium
effort. That is the guide's first Codex row.

**What this does not say.** One night, one repository, n=5, a quota counter
with one-point resolution and a third of its cells sharing the window with
another job. The T4 misses are the place to look first if Luna is routed more
widely: an exhaustive listing over a file that declares more than a dozen types
is where it dropped one. Quota share is what a Plus subscription pays, and it
does not convert to a price.

**Raw:** `runs/codex_tier.jsonl`. `runs/codex_tier.plan` is the consumed plan;
it is empty, and it must stay present, because `bin/overnight.sh` writes a fresh
plan and re-runs the lever if the file is missing.

---

## codex_effort -- Terra at high vs medium reasoning effort -- INCONCLUSIVE

**Status:** run 2026-10-10/11, 40 cells (4 tasks x 2 arms x n=5). The window
reached 90% after 22 cells; the governor slept 158 minutes for the reset and
finished the last 18 cells between 01:05 and 01:13 UTC.

The question was whether `high` buys any gate passes over `medium` or only
spends quota, and a null result was to change the local default, which is
`high`.

**The gate leaned towards `high`, by a margin the same night produced between
identical arms.**

| Task | high | medium |
|---|---:|---:|
| T1-orbit-trace (narrative) | 5/5 | **2/5** |
| T2-viewport-consumers (enumerative) | 5/5 | 5/5 |
| T3-go-package-types (fan-out, Go) | 5/5 | 4/5 |
| T4-swift-declared-types (fan-out, Swift) | 5/5 | 5/5 |
| **total** | **20/20** | **16/20** |

All three T1 misses at medium are the miss Terra made once in `codex_tier`:
each names `ReferenceOrbit.swift` as the producer and `FractalMetalView`,
`FractalRenderer` and `fractal.metal` as consumers, which covers the other three
key terms, and describes the precision type as "fixed-point bignum" without
naming it. The T3 miss left `PerturbationStats` out of its package list. The
gate is a substring match over named types, so a paraphrase fails it by design.
What `high` bought on T1 was naming precision; the medium answers had the shape
of the path right.

Whether that is real is not shown. Terra at medium is also `codex_tier`'s
control arm, run an hour earlier, where it scored 19/20 with T1 at 4/5. Two
identical arms differed by three passes; this lever's arms differ by four.
Pooling both medium runs gives 35/40 against `high`'s 20/20, and if the arms
were identical a split at least that lopsided would turn up about one time in
eight (Fisher exact, one-sided; about one in nineteen for this lever's own 20
against 16).

**Medium costs about a third less quota.** T1 is left out of the efficiency
comparison: medium passed it twice, the same exclusion `model_tier_haiku`
applied to Haiku's T1. Over T2 to T4:

| Metric | high | medium | Delta | Per task |
|---|---:|---:|---:|---|
| 5-hour window, summed over T2-T4 cells | 17 pts | 10 pts | **-41%** | T2 4 to 3, T3 6 to 5, T4 7 to 2 |
| reasoning tokens | 281 | 182 | -35.2% | -30.0% to -39.6%, all three |
| output tokens | 749 | 588 | -21.5% | -11.9% to -28.7%, all three |
| cache read tokens | 86272 | 68864 | -20.2% | T2 flat |
| tool calls | 2.0 | 2.0 | flat | flat on all three |
| wall-clock | 16.0s | 21.0s | +31.2% | disagrees in sign |

Over all four tasks and all 40 cells, `high` drew 31 points and `medium` 20
(-35%). On the cells that ran alone, `high` drew 1.21 points a cell and `medium`
0.60. The reasoning-token saving agrees in sign on every task, which the Codex
A/A comparison did not; the output-token saving is near the edge of it.

**Verdict: inconclusive on the gate, default unchanged.** The condition for
changing the default was a null gate, and the gate came back four passes
towards `high` rather than null. Those four passes sit inside what identical
arms produced the same night, so this does not show that `high` is needed
either. `high` stays the default, because the evidence to move it is not here.
Settling it needs n=10 per arm on T1 alone, 20 cells, which is where the whole
difference sits.

**An observation across the two levers, not a finding.** Luna at medium passed
T1 5/5, where Terra at medium passed it 6 times in 10. Luna took a median of 9
tool calls on T1 against Terra's 4 and named the type. Dropping a tier and
dropping effort did not behave alike here: the smaller model explored more and
named the type, the larger model at lower effort explored less and paraphrased
it. One task, so it is recorded rather than relied on.

**Raw:** `runs/codex_effort.jsonl`, and the consumed, empty
`runs/codex_effort.plan`.

---

## model_tier_haiku -- Sonnet 5 vs Haiku 4.5

**Status:** run 2026-09-18, 20 cells (2 tasks x 2 arms x n=5), harness `a9a78b2`.

**The gate discriminated, and that is the result.**

| Task | Sonnet 5 | Haiku 4.5 |
|---|---:|---:|
| T1-orbit-trace (narrative) | 5/5 | **2/5** |
| T2-viewport-consumers (enumerative) | 5/5 | 5/5 |

This is the first time in this harness that the answer-key gate has separated
two arms at all. `model_tier` found Opus and Sonnet tied 6/6, which is what made
its cost delta readable as real saving. One tier lower the tie breaks, and it
breaks by **task shape rather than uniformly**: Haiku is perfect on enumerative
lookup and fails the narrative trace three times in five.

**On T1 the cost is genuinely unmeasurable.** Efficiency is compared only across
runs passing in both arms, so Haiku's three failures drop T1 to n=2 and the
analyser refuses to treat it as a result. A saving computed from those two
survivors would be an average over exactly the cases where the cheap tier
worked, with the failures discarded: the arithmetic by which a tier that fails
three times in five looks like a bargain.

**On T2 the cost is perfectly measurable, and Haiku is the more expensive arm.**
Both arms passed 5/5, so nothing is excluded:

| T2-viewport-consumers | Sonnet 5 | Haiku 4.5 | Delta |
|---|---:|---:|---:|
| gate pass | 5/5 | 5/5 | none |
| median cost USD | 0.0205 | 0.0360 | +75.8% |
| median tool calls | 1 | 2 | +100% |

Sonnet answered T2 with a single Grep in all five runs. Haiku needed two calls
at the median and nine in two of the five.

**So there is no routing row here.** The obvious recommendation -- send
enumerative lookup to the cheaper tier -- survives the gate and then fails on
cost, which is the one place it was supposed to pay. On the task Haiku can do
reliably it costs more than Sonnet; on the task where it might have saved
something it is wrong three times in five. Across these two task shapes there is
no case for routing to Haiku at all.

**What this does not say.** Two tasks, n=5, one repository. This is not a
general verdict on Haiku 4.5, and a cheaper tier may well pay on task shapes not
represented here -- bulk mechanical edits, classification, extraction. It says
that *cold repository comprehension*, in both the shapes this corpus contains,
has now been measured down to Haiku and stops paying at Sonnet.

---

## repo_priming -- architecture map present vs absent

**Status:** run twice. The first run (2026-09-18) is **void**; the second
(2026-09-18, harness `1c24a92`) is valid and **reverses its finding**.

### The valid run

20 cells, 2 tasks x 2 arms x n=5, both arms given the identical 32-line map.
Gate 10/10 in both arms.

| Metric | Control | Treatment | Delta | Per task |
|---|---:|---:|---:|---|
| cost USD | 0.3034 | 0.3666 | **+20.8%** | T1 +20.2%, T2 +24.6% |
| wall-clock | 16.5s | 19.6s | +18.6% | T1 +18.8%, T2 +18.0% |
| tool calls | 5.5 | 6.0 | +9.1% | T1 +11.1%, T2 +0.0% |
| cache read tokens | 251676 | 336559 | +33.7% | T1 +43.2%, T2 +1.7% |

**The map costs more and finds nothing faster.** Tool calls are flat (T1 9 to
10, T2 2 to 2), so the map did not reduce search at all. Cost and wall-clock
both rise by roughly a fifth, and they rise on **both tasks, in the same
direction, by similar amounts**. The mechanism is unremarkable once stated: the map is prompt
weight that is paid for on every turn, and it bought no fewer round trips.

**Read the size honestly.** +20.8% sits right on the +/-20% noise floor, so the
magnitude is not reliable. What is reliable is the direction: four metrics, two
tasks, same sign throughout, no metric favouring the map. The safe claim is
"no saving, plausibly a modest penalty", not "costs 20% more".

### Why the first run said the opposite

The first run reported **-34.0% cost and -36.8% tool calls** and was written up
here as validating the hypothesis. It measured something else.

T1's priming block named `ReferenceOrbit`, `BigFixed`, `FractalRenderer` and
`FractalMetalView` -- all four of that task's four answer-key terms -- and then
described how they connect, which is the question restated. T2's named the
`scene` and `nav` packages and asserted that `internal/viewport` is consumed by
scene composition and the navigation engine, which is that task's answer. The
treatment arm was not oriented, it was told. A -43.8% saving on T1 was recall
from the system prompt.

The two maps also differed in kind -- T1's answer-shaped and six lines, T2's
generic and four -- so the arms were not comparable across tasks either. That
is the more likely explanation for the sign disagreement on four of six metrics
than the noise floor, which was the explanation offered at the time.

Both tasks now use one identical 32-line map giving the shape of the tree:
module, package count, binary count, test convention, where the Swift sources
and build artefacts live, what is not part of either build. No dependency facts
at all. The length matches the hypothesis, which describes a 20-30 line
architecture map rather than the 4-6 lines first measured.

### What this means for the hypothesis

The claim was that a tight architecture map at the top of `CLAUDE.md` or
`AGENTS.md` cuts the cost of orientation. On this corpus it does not. It adds
roughly a fifth to the bill and saves no round trips.

**Scope the conclusion.** Two tasks, one repository, both questions answerable
by a handful of greps against a tree whose layout is conventional. A map most
plausibly earns its place where the layout is *not* guessable -- unusual
directory conventions, a monorepo with many entry points, generated code that
should be ignored -- and none of that is represented here. What this refutes is
the general form of the claim: that a map is a cheap win worth adding
everywhere. On a conventionally laid-out repo it is a cost.

**Guard added.** `bin/preflight.sh` now refuses this lever if any priming block
names one of its task's answer-key terms, listing the offenders. Substring
matched, because the gate is. Run against the fixtures it replaces, it refuses
both.

**Raw:** `runs/repo_priming.jsonl` (valid), and
`runs/repo_priming.void-answer-in-priming.jsonl` (void).

---

## subagent_hygiene -- INCONCLUSIVE: the model will not delegate

**Status:** run twice. The first run (2026-09-18, T1/T2) is **void**; the second
(2026-09-18, T3/T4, harness `d454600`) is valid and inconclusive, for a reason
that is itself the finding.

### The valid run

20 cells, 2 fan-out tasks x 2 arms x n=5. Gate 10/10 in both arms.

| Metric | Control | Treatment | Delta | Per task |
|---|---:|---:|---:|---|
| tool calls | 3.5 | 4.0 | +14.3% | T3 +0.0%, T4 +33.3% |
| cost USD | 0.1724 | 0.1836 | +6.5% | T3 -0.1%, T4 +12.1% |
| output tokens | 2044 | 2042 | -0.1% | T3 -5.4%, T4 +3.4% |
| cache read tokens | 163580 | 192262 | +17.5% | T3 +24.1%, T4 +11.0% |

Every figure is inside the noise floor and four of six metrics disagree in sign
between the two tasks. Nothing here is a result.

**`subagent_stats.spawned` is 0 in all 20 cells.** `Agent` and `Task` were
allowed this time -- the argv confirms it -- and both tasks were built to need
breadth: T3 wants exported types from 57 Go files across 13 packages, T4 wants
declared types from 17 Swift files. The treatment arm was told, in the system
prompt, how to brief a sub-agent. Opus 5 delegated zero times and answered
everything with Bash.

So the instruction was inert, and the arms were identical again -- but this time
for a reason that is a finding rather than a fixture bug.

### The finding: availability plus instruction is not adoption. Third instance.

This harness has now produced the same result three times, with three different
tools, and it is the most durable thing in this file:

| Lever | Offered | Instructed | Used |
|---|---|---|---|
| `ast_grep` | binary on PATH | named, with syntax, in the system prompt | 0 of 6 cells |
| `codegraph` | MCP registered fleet-wide | a whole skill telling agents to prefer it | never measured; the tool was gone for weeks and nothing noticed |
| `subagent_hygiene` | `Agent` allowed, tasks built for fan-out | told how to brief a sub-agent | 0 of 20 cells |

Three levers, three attempts to change tool selection by making a capability
available and describing it, and no change in behaviour any of the three times.
The model uses what it is used to. That is not a Claude-specific quirk to
report; it is a constraint on this whole method: **a lever whose treatment is
"the model should prefer X" cannot be measured by prompt-level A/B.** To
measure it you must remove the alternative, which changes the question into
something else.

For this lever the corollary is practical: an instruction about how sub-agents
should report back is worth nothing on task shapes where the model does not
spawn one, and on cold repository comprehension it does not. BENCH-008 saw the
one case where it did delegate -- Sonnet, T1, `Agent` permitted -- and it failed
the gate after 20 tool calls, against 3/3 passes in 6-12 calls with `Agent`
denied. The available evidence says delegation on comprehension work is a
pessimisation before it is a saving.

**What would make it measurable.** A task the model cannot complete alone --
one exceeding its context, or a genuinely parallel workload -- so delegation is
forced rather than suggested. That is a different experiment from the one this
lever was written for, and a corpus of two comprehension tasks cannot reach it.

### The void run

The first attempt carried `Agent` and `Task` in `disallowed_tools` on both arms,
so the arms could not differ. It returned -4.2% on cost, and the first write-up
explained that null as a property of the corpus: the tasks being too small to
need delegation. The explanation was plausible, and wrong. An unfirable lever
produced a number, and the number got a story.

The denial was not careless -- a sub-agent's tool calls never reach the parent
stream, so delegation under-counts `tool_calls`, the metric every other lever
compares. Weakening it for everyone to suit this lever would have corrupted the
registry. The fix was fixtures of its own, plus enforcement in both directions:
a task may name the levers permitted to use it, and a lever may name the only
tasks it may run on. `run-cell.sh` refuses the mismatch rather than recording a
corrupted cell.

**Raw:** `runs/subagent_hygiene.jsonl` (valid), and
`runs/subagent_hygiene.void-agent-disallowed.jsonl` (void, kept deliberately --
a lever that could not fire and a lever that fired and showed nothing are
different findings).

---

## model_tier -- Opus 5 vs Sonnet 5

**Status:** run 2026-08-23, 12 cells (2 tasks x 2 arms x n=3), harness `5f14fa9`.
**Full write-up:** [BENCH-008](../tasks/BENCH-008/scorecard.md)

| Metric | Opus 5 | Sonnet 5 | Delta |
|---|---:|---:|---:|
| gate pass | 6/6 | 6/6 | none |
| tool calls | 7.5 | 4.5 | -40.0% |
| cost USD | 0.3852 | 0.1096 | -71.6% |
| wall-clock | 46.7s | 17.9s | -61.7% |

No quality separation, so the cost delta is real saving rather than a cheaper
wrong answer. Holds across both task shapes (-71.4% narrative, -72.2%
enumerative).

**Routing guide, first row:** cold repository comprehension and dependency
lookup route to Sonnet. Scope this narrowly -- see the scorecard's "what this
does not support".

---

## codegraph -- RETIRED, never measured

Retired 2026-08-23 without ever producing a number. Recorded here rather than
deleted, because "we tried it and it lost" and "we could never run the test"
are different findings and only one of them is true.

**Why it could not run.** `codegraph` was not installed. Two independent
failures, either sufficient on its own: it declares `engines: node ">=20.0.0
<25.0.0"` against an installed node 26.5.0, and its global npm prefix pointed
inside a version-pinned Homebrew Cellar path, so the node upgrade took the
symlink with it. `TOKEN-SPEND-TODO.md` predicted exactly this -- *"it will break
on a node upgrade and need re-linking"* -- and the prediction was right without
being acted on, which is the more interesting half.

`bin/preflight.sh` refused the lever, and that refusal is the whole point of
the gate. With codegraph absent the treatment arm would have silently fallen
back to grep/Read -- the control arm's toolset -- both arms would have produced
identical numbers, and this file would now report "no measurable difference"
for a lever that never ran.

**Why it was retired rather than reinstalled.** Reinstalling needs a pinned
node@20 and a moved npm prefix, and then buys an index that must be rebuilt per
repo and goes stale silently: the fractals index was built 2026-07-20, 39 files
behind HEAD. Against that, the measured baseline is cheap -- BENCH-008 answered
both harness tasks with plain Grep/Read in 1-15 tool calls on repos of 3k-41k
lines -- and the only prior evidence, BENCH-006 at n=1, was a rubric tie whose
noted failure mode was the graph being *confidently wrong* about edges. A tool
that is expensive to keep honest and unproven when honest is not worth the
node pin.

**What was removed.** 40 `.mcp.json` registrations across the estate (29 of
them already pointing at nothing), the `codegraph-first` skill that told
claude_code/codex/cursor to prefer it, its control-plane registration, and four
synced skill copies. `emergence-lab` was left alone -- another session holds it.

**What replaced it.** `ast_grep` -- same question, no index. See its section
below. If that lever also fails to beat grep, the correct reading is that no
discovery tool is warranted at this repo size, and both retirements were right.

**Detection added so this class of failure is loud next time.**
`mcp-hub/scripts/doctor-platforms.py` gained `check_repo_mcp_binaries` (walks
each repo's own `.mcp.json` and fails when a server's command does not resolve)
and `check_npm_global_prefix` (fails when `npm prefix -g` sits inside a Cellar
path). Both are generic and outlive codegraph.

---

## ast_grep -- INCONCLUSIVE: the treatment arm never fired

Ran twice, n=3, two tasks, 12 cells each. Gate: 6/6 passed in both arms both
times. **Neither run measured ast-grep**, because in all six treatment cells of
the instrumented run the model never once invoked it. Recorded as inconclusive
rather than as the win the second run's numbers appear to show.

| run | tool calls (paired median delta) | what it looks like |
|---|---|---|
| 1, uninstrumented | **+11.8%** | ast-grep is worse |
| 2, instrumented | **-21.7%** | ast-grep is much better |

Same lever, same tasks, same n, opposite signs. That alone should stop anyone
reporting either number, and the instrumentation says why.

**What the treatment arm actually ran.** `run-cell.sh` now records the leading
word of every Bash command, not just the tool name. Across the six treatment
cells: `grep` 25 times, `cd` 15, `sed`/`cat`/`ls`/`wc`/`head` the rest.
`ast-grep`: **zero**. The control arm denies ast-grep at the tool layer and the
treatment arm declines to use it, so both arms were grep-and-Read. The lever
compared a thing against itself.

**Why this was invisible before.** The tools histogram stores tool *names*.
Every call in both arms logged as `"Bash"`, so a lever whose entire treatment
is "this binary is on PATH" left no trace in its own evidence. The first run
was reported internally as a clean null before that gap was noticed; the second
would have been reported as a 21.7% win. Both would have been wrong, and the
second wrong in the more expensive direction.

**Three things this does establish, none of them about ast-grep:**

1. **The noise floor here is roughly +/-20% at n=3 over two tasks.** Two
   grep-vs-grep runs differed by 33 percentage points of apparent effect. Any
   lever claiming less than about a 20% delta on this task set is
   unmeasurable as configured. That is a property of the harness, not of any
   one lever, and both levers run on 2026-09-18 were sized against it.
2. **An `--append-system-prompt` nudge does not reliably change tool
   selection.** The treatment prompt named the binary, gave its syntax, and
   said to prefer it for structural questions. The model used grep anyway, six
   times out of six. Availability plus instruction is not adoption.
3. **That is the same failure that made `codegraph-first` harmless-looking for
   weeks** -- doctrine asserting a tool should be preferred, with nothing
   measuring whether it was. Retiring the skill removed the assertion; this
   result shows the assertion would not have worked even had the tool existed.

**What would make it measurable.** Force the tool rather than suggest it: deny
`Bash(grep:*)` in the treatment arm so structural search is the only route, and
accept that this measures "ast-grep vs no text search" rather than "ast-grep vs
grep". The honest version of the original question may simply not be reachable
by prompt-level A/B -- the model prefers the tool it knows, and that preference
is itself the answer for a low-hassle-tool decision.

**Standing recommendation, unchanged and now better supported:** at 3k-41k
lines, plain Grep/Read passes the gate every time in 1-21 tool calls. ast-grep
is installed and costs nothing to keep (one static binary, no index, no
registration), so it stays available for the structural queries where regex
genuinely cannot express the question. It is not worth steering toward, and no
skill should be written telling agents to prefer it.

Raw: `runs/ast_grep.jsonl` (instrumented), `runs/ast_grep.uninstrumented.jsonl`
(first run, kept as the evidence for the noise-floor claim).

---

## prompt_cache -- OBSERVATIONAL only

The CLI exposes no flag to disable prompt caching, so there is no control arm
to build and this can never be a true A/B by this method. Recorded so the lever
is not mistaken for untested when it is untestable here. `cache_read_input_tokens`
is captured on every run; BENCH-008 saw 376k (Opus) and 260k (Sonnet) cache
reads (a mean of the two per-task medians), so caching is demonstrably active.
