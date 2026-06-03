# Task Brief — BENCH-006

> A **tooling meta-bench**, not a four-subscription comparison. The thing
> being benchmarked is whether a **codegraph code-intelligence MCP** beats
> the baseline **grep + Read** workflow for working in a codebase — and
> *where*. Both arms run on the **same model** (Claude Code / Opus 4.8);
> the variable is the toolset, not the subscription. This mirrors the
> meta-bench framing of BENCH-005 (which benched orchestration, not raw
> code-gen).

---

## Metadata

| Field | Value |
|-------|-------|
| Task ID | BENCH-006 |
| Date | 2026-06-03 |
| Source repo | fractals-from-the-90s (`feat/julia-deep-zoom`) |
| Source issue / PR | n/a — trial commissioned by repo owner |
| Lanes | **codegraph** (MCP only) vs **baseline** (grep/Read only) — both Claude Code / Opus 4.8. cursor + gemini lanes N/A: this is a single-model tool A/B. |

---

## Spec

Run four sub-experiments on a real repo (52 files, Go + Swift; codegraph
index: 757 nodes / 2278 edges) and score each on four metrics —
(1) tool calls + token volume, (2) answer correctness, (3) wall-clock
feel / friction, (4) index accuracy:

1. **Comprehension trace.** Cold question ("how is a reference orbit
   produced and bound into the live perturbation render path, and what
   consumes it?") answered arm A (codegraph) vs arm B (grep/Read).
2. **Index accuracy audit.** Query codegraph's `callers`/`callees`/
   `impact` edges and check each against grep ground truth.
3. **Implement (orientation).** Cost to orient to an edit site. To avoid
   warm-cache contamination, each arm gets a *separate but comparable*
   cold target (an unread `Validate() error` method).
4. **Capability exploration.** Exercise all 7 codegraph tools; record
   what works on a mixed Go+Swift repo.

---

## Constraints

- Both arms run on the identical question/target; no arm sees the other's work where it would contaminate the measurement (see warm-cache note in Exp 3).
- Index accuracy claims must be checked against grep, not asserted.
- Be honest about methodology limits (single-session, self-measured, no metered tokens).

---

## Definition of done

- [ ] All four experiments run with real tool calls (counts exact).
- [ ] Each edge claim in Exp 2 verified against grep ground truth.
- [ ] A finding written up with a scoreboard + caveats.
- [ ] A clear recommendation: keep/drop codegraph, and *when* to use which tool.

---

## Context paste

Source-repo write-up lives at
`fractals-from-the-90s/docs/metrics/codegraph-ab-benchmark.md` (the full
experiment log). The condensed result is in this task's `finding.md`.

---

## Notes for the scorer

Rubric mapping for a tooling A/B (the six dimensions apply to each *arm*,
not to a model):
- **Correctness** → did the arm reach the right, complete answer.
- **Iterations** → round-trips / tool calls to get there.
- **Failure mode** → when the tool is wrong, is it loud (grep returns
  empty) or silently-confident (a wrong/conflated graph edge)?
- **Autonomy / Time** → both arms are fully autonomous and sub-5-min here;
  they do not discriminate on this task and are recorded for completeness.

The interesting result is the *split*: codegraph wins
speed/round-trips/completeness; baseline wins failure-mode honesty. The
rubric total can tie while the practical recommendation is clear
(codegraph-first, grep-verify).
