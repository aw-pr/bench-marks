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

**The cost deltas are not quotable and are omitted deliberately.** Efficiency is
compared only across runs passing in both arms, so Haiku's three failures drop
T1 to n=2 and the analyser flags it. Quoting a -27.8% cost saving off that would
be averaging over exactly the cases where the cheap tier worked and discarding
the ones where it did not -- which is how a tier that fails 30% of the time
looks like a bargain. The gate is the finding; the saving is unmeasured.

**Routing guide, second row:** enumerative lookup -- "which callers touch X",
answerable by enumeration -- may route to Haiku. Narrative tracing -- following
a value through a call chain -- stays at Sonnet. Do not read this as a general
Haiku verdict on n=5 over two tasks; read it as one task-shape boundary found.

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

**Clears the noise floor.** Every metric moves the same direction by roughly a
third, against a floor of +/-20% established by the two disagreeing `ast_grep`
runs. No gate movement, so this is the same answer reached for less.

**TOKEN-SPEND-TODO item 4 is validated.** A 20-30 line architecture map at the
top of `CLAUDE.md` / `AGENTS.md` cuts roughly a third of the orientation cost.
The remaining work is rollout, not measurement.

---

## subagent_hygiene — conclusions vs file dumps

**Status:** run 2026-09-18, 20 cells (2 tasks x 2 arms x n=5), harness `a9a78b2`.

| Metric | Control | Treatment | Delta |
|---|---:|---:|---:|
| gate pass | 10/10 | 10/10 | none |
| cost USD | 0.3820 | 0.3660 | −4.2% |
| tool calls | 7.0 | 9.0 | +28.6% |
| wall-clock | 21.3s | 26.4s | +23.9% |
| output tokens | 2921 | 2977 | +1.9% |

**No effect.** −4.2% on cost is far inside the +/-20% noise floor and cannot be
distinguished from zero at n=5. The tool-call and wall-clock figures move the
wrong way by a similar margin, which is itself consistent with noise rather than
with a real penalty.

**What this does not say.** It does not say the hygiene instruction is wrong. It
says the effect is not detectable on these two tasks, and there is a structural
reason to expect that: both corpus tasks are small enough that the parent
answers them in 6-10 tool calls without heavy delegation, so there is barely a
sub-agent transcript for the instruction to shrink. The lever was designed
against a claim about *fan-out* cost and the corpus does not fan out.

**TOKEN-SPEND-TODO item 5 is not validated and not refuted.** Testing it
honestly needs a task whose control arm actually delegates and returns a large
dump. That is a corpus gap, not a result.

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
both harness tasks with plain Grep/Read in 1–7 tool calls on repos of 3k–41k
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
   unmeasurable as configured — that is a property of the harness, and it
   applies to `repo_priming` and `subagent_hygiene` before they are run.
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
lines, plain Grep/Read passes the gate every time in 1–16 tool calls. ast-grep
is installed and costs nothing to keep (one static binary, no index, no
registration), so it stays available for the structural queries where regex
genuinely cannot express the question. It is not worth steering toward, and no
skill should be written telling agents to prefer it.

Raw: `runs/ast_grep.jsonl` (instrumented), `runs/ast_grep.uninstrumented.jsonl`
(first run, kept as the evidence for the noise-floor claim).

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
