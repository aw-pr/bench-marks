# A/B results

One section per lever. A lever appears here only once it has run; a lever that
cannot run honestly says so and why, rather than being quietly absent.

Raw records are in `runs/<lever>.jsonl`, one JSON object per cell.

---

## model_tier_haiku — Sonnet 5 vs Haiku 4.5

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
| median cost USD | 0.0205 | 0.0360 | +75.6% |
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

## repo_priming — architecture map present vs absent

**Status:** run 2026-09-18, 20 cells (2 tasks x 2 arms x n=5), harness `a9a78b2`.

| Metric | Control | Treatment | Delta |
|---|---:|---:|---:|
| gate pass | 10/10 | 10/10 | none |
| tool calls | 9.5 | 6.0 | −36.8% |
| cost USD | 0.4250 | 0.2805 | −34.0% |
| wall-clock | 23.7s | 17.2s | −27.5% |
| output tokens | 2962 | 2176 | −26.6% |

No gate movement, so wherever cost fell it is the same answer reached for less.
But the aggregate above hides the shape of the effect, and two caveats decide
how far it generalises.

**The whole effect is T1. T2 moved the other way.**

| Per task | Metric | Control | Treatment | Delta |
|---|---|---:|---:|---:|
| T1-orbit-trace | tool calls | 16 | 9 | −43.8% |
| | cost USD | 0.7513 | 0.4515 | −39.9% |
| T2-viewport-consumers | tool calls | 3 | 3 | 0.0% |
| | cost USD | 0.0986 | 0.1095 | +11.1% |
| | wall-clock | 7.6s | 10.4s | +37.5% |

T1 is a large win well clear of the noise floor. T2 is flat on tool calls and
slightly worse on everything else. The headline reads as a uniform third because
`analyse.py` takes the mean of the two per-task medians, and T1 is an order of
magnitude larger in absolute terms, so it dominates. One task improved; the
other did not.

**The fixtures are a 6-line and a 4-line map, not the 20-30 line map the
hypothesis describes.** Whatever this measured, it was not the thing item 4
proposes writing. And T1's priming block names `ReferenceOrbit`, `BigFixed`,
`FractalRenderer` and `FractalMetalView` -- four of that task's five answer-key
terms, near-verbatim. That is much closer to putting the answer in the system
prompt than to orienting an agent in an unfamiliar tree, which is the more
plausible reading of why T1 moved so far and T2, whose 4-line map names no
answer-key term, did not move at all.

**So: promising, not validated.** The honest claim is that *naming the relevant
files in the system prompt* cuts the cost of finding them, which is close to
tautological. Whether a generic architecture map helps an agent that does not
already have the answer handed to it is untested, and the fixtures need
rewriting before it can be: a map of comparable length for both tasks, naming
structure rather than answer-key terms.

---

## subagent_hygiene — VOID: the lever could not fire

**Status:** first run 2026-09-18 is void and is not reported as a result. A
corrected run is in progress against new fixtures.

**What happened.** All 20 cells carried `Agent` and `Task` in
`disallowed_tools`, and `subagent_stats.spawned` is `0` in every one. The two
arms differed only by an `--append-system-prompt` telling the model how to
brief a sub-agent, given to a model that could not spawn one. Both arms were
therefore the same run, and the -4.2% cost difference they produced was the
harness measuring itself.

**This is the `ast_grep` failure repeating**, which is the part worth recording.
There the treatment arm was told to prefer a tool and silently kept using grep;
here it was told how to delegate and silently could not. Both produced a
confident null from arms that were never different, and in both cases the
number looked plausible enough to explain rather than check. The first write-up
of this run duly explained it, attributing the null to the corpus being too
small to need delegation. That explanation was wrong and, worse, it was
reasonable -- which is how an unfirable lever becomes a finding.

**Why the denial was there, and why it was right.** A sub-agent's tool calls
never appear in the parent stream, so a delegated run under-counts `tool_calls`,
the metric every other lever compares. Deleting the denial to suit this lever
would have quietly corrupted the rest of the registry. The fix is fixtures of
its own: T3 and T4 permit `Agent`, and both directions are now enforced -- a
task may name the levers allowed to use it, and a lever may name the only tasks
it may run on. `run-cell.sh` refuses the mismatch rather than recording a
corrupted cell.

**Prior evidence, unchanged and still the reason this lever is interesting.**
BENCH-008's smoke runs saw Sonnet fail T1's gate after 20 tool calls and one
delegation with `Agent` permitted, then pass 3/3 in 6-12 calls with `Agent`
denied. If that reproduces under control, permitting delegation on cold
comprehension makes a model both worse and more expensive -- which would make
the instruction this lever tests less valuable than simply not delegating.

**Metric note for the corrected run.** `tool_calls` is not comparable on T3/T4
for the reason above, so the lever is judged on parent-context tokens
(`input_tokens`, `cache_read_input_tokens`), which is what its question actually
asks about, plus the gate.

**Raw:** the void run is kept as `runs/subagent_hygiene.void-agent-disallowed.jsonl`.
A lever that could not fire and a lever that fired and showed nothing are
different findings, and only the first one is true here.

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

## codegraph — RETIRED, never measured

Retired 2026-08-23 without ever producing a number. Recorded here rather than
deleted, because "we tried it and it lost" and "we could never run the test"
are different findings and only one of them is true.

**Why it could not run.** `codegraph` was not installed. Two independent
failures, either sufficient on its own: it declares `engines: node ">=20.0.0
<25.0.0"` against an installed node 26.5.0, and its global npm prefix pointed
inside a version-pinned Homebrew Cellar path, so the node upgrade took the
symlink with it. `TOKEN-SPEND-TODO.md` predicted exactly this — *"it will break
on a node upgrade and need re-linking"* — and the prediction was right without
being acted on, which is the more interesting half.

`bin/preflight.sh` refused the lever, and that refusal is the whole point of
the gate. With codegraph absent the treatment arm would have silently fallen
back to grep/Read — the control arm's toolset — both arms would have produced
identical numbers, and this file would now report "no measurable difference"
for a lever that never ran.

**Why it was retired rather than reinstalled.** Reinstalling needs a pinned
node@20 and a moved npm prefix, and then buys an index that must be rebuilt per
repo and goes stale silently: the fractals index was built 2026-07-20, 39 files
behind HEAD. Against that, the measured baseline is cheap — BENCH-008 answered
both harness tasks with plain Grep/Read in 1-15 tool calls on repos of 3k-41k
lines — and the only prior evidence, BENCH-006 at n=1, was a rubric tie whose
noted failure mode was the graph being *confidently wrong* about edges. A tool
that is expensive to keep honest and unproven when honest is not worth the
node pin.

**What was removed.** 40 `.mcp.json` registrations across the estate (29 of
them already pointing at nothing), the `codegraph-first` skill that told
claude_code/codex/cursor to prefer it, its control-plane registration, and four
synced skill copies. `emergence-lab` was left alone — another session holds it.

**What replaced it.** `ast_grep` — same question, no index. See its section
below. If that lever also fails to beat grep, the correct reading is that no
discovery tool is warranted at this repo size, and both retirements were right.

**Detection added so this class of failure is loud next time.**
`mcp-hub/scripts/doctor-platforms.py` gained `check_repo_mcp_binaries` (walks
each repo's own `.mcp.json` and fails when a server's command does not resolve)
and `check_npm_global_prefix` (fails when `npm prefix -g` sits inside a Cellar
path). Both are generic and outlive codegraph.

---

## ast_grep — INCONCLUSIVE: the treatment arm never fired

Ran twice, n=3, two tasks, 12 cells each. Gate: 12/12 passed in both arms both
times. **Neither run measured ast-grep**, because in all six treatment cells of
the instrumented run the model never once invoked it. Recorded as inconclusive
rather than as the win the second run's numbers appear to show.

| run | tool calls (paired median delta) | what it looks like |
|---|---|---|
| 1, uninstrumented | **+11.8%** | ast-grep is worse |
| 2, instrumented | **−21.7%** | ast-grep is much better |

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

1. **The noise floor here is roughly ±20% at n=3 over two tasks.** Two
   grep-vs-grep runs differed by 33 percentage points of apparent effect. Any
   lever claiming less than about a 20% delta on this task set is
   unmeasurable as configured. That is a property of the harness, not of any
   one lever, and both levers run on 2026-09-18 were sized against it.
2. **An `--append-system-prompt` nudge does not reliably change tool
   selection.** The treatment prompt named the binary, gave its syntax, and
   said to prefer it for structural questions. The model used grep anyway, six
   times out of six. Availability plus instruction is not adoption.
3. **That is the same failure that made `codegraph-first` harmless-looking for
   weeks** — doctrine asserting a tool should be preferred, with nothing
   measuring whether it was. Retiring the skill removed the assertion; this
   result shows the assertion would not have worked even had the tool existed.

**What would make it measurable.** Force the tool rather than suggest it: deny
`Bash(grep:*)` in the treatment arm so structural search is the only route, and
accept that this measures "ast-grep vs no text search" rather than "ast-grep vs
grep". The honest version of the original question may simply not be reachable
by prompt-level A/B — the model prefers the tool it knows, and that preference
is itself the answer for a low-hassle-tool decision.

**Standing recommendation, unchanged and now better supported:** at 3k–41k
lines, plain Grep/Read passes the gate every time in 1-21 tool calls. ast-grep
is installed and costs nothing to keep (one static binary, no index, no
registration), so it stays available for the structural queries where regex
genuinely cannot express the question. It is not worth steering toward, and no
skill should be written telling agents to prefer it.

Raw: `runs/ast_grep.jsonl` (instrumented), `runs/ast_grep.uninstrumented.jsonl`
(first run, kept as the evidence for the noise-floor claim).

---

## prompt_cache — OBSERVATIONAL only

The CLI exposes no flag to disable prompt caching, so there is no control arm
to build and this can never be a true A/B by this method. Recorded so the lever
is not mistaken for untested when it is untestable here. `cache_read_input_tokens`
is captured on every run; BENCH-008 saw 376k (Opus) and 260k (Sonnet) cache
reads (a mean of the two per-task medians), so caching is demonstrably active.
