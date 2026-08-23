# Task Brief — BENCH-008

> A **lever meta-bench**, not a four-subscription comparison, and the first run
> of the `ab/` harness. The thing being benchmarked is the *model tier*: on a
> given task shape, which is the cheapest tier that still reaches the right
> answer? Both arms run the identical prompt, corpus and tool surface; the only
> variable is `--model`. This follows the meta-bench framing of BENCH-005
> (orchestration) and BENCH-006 (toolset).

---

## Metadata

| Field | Value |
|-------|-------|
| Task ID | BENCH-008 |
| Date | 2026-08-23 |
| Source repo | fractals-from-the-90s (`dev`) |
| Source issue / PR | n/a — `token-maxing/TOKEN-SPEND-TODO.md` item 3, open follow-on |
| Lanes | **control** = Opus 5, **treatment** = Sonnet 5, both Claude Code `-p`. cursor + gemini lanes N/A: single-harness tier A/B. |
| Harness | `ab/` — see `ab/README.md` |

---

## The question item 3 leaves open

Item 3 records model tiering as done — stage cards declare a worker tier and
the loop dispatches it. What it leaves open is the routing guide: *which task
shapes map to which tier*, so card authors pick consistently instead of by
feel. This bench is the first evidence for that guide.

---

## Spec

Two corpus tasks of deliberately different shape, each run n=3 per arm in
randomised order:

- **T1 orbit trace** — narrative comprehension over Swift. "How is a reference
  orbit produced and bound into the perturbation render path, and what consumes
  it?" This is BENCH-006's Experiment 1 question verbatim, so the result is
  readable against that n=1 finding.
- **T2 viewport consumers** — enumerative dependency lookup over Go. "Which
  packages depend on `internal/viewport`?"

Both arms get the identical prompt, the identical `--allowedTools`, and the
identical `--disallowedTools` (`Agent` denied, so sub-agent work cannot hide
tool calls from the count).

---

## Constraints

- Correctness is a **gate**, not a rubric score. Each task carries a
  machine-checkable answer key derived from grep ground truth over tracked
  sources on 2026-08-23. Efficiency is compared only across passing runs.
- Every figure is metered from `claude -p --output-format stream-json`
  (`usage`, `total_cost_usd`), never self-reported. This is the limitation
  BENCH-006 declared and could not close.
- Cell order is randomised so drift in cache warmth or provider load lands on
  both arms evenly.

---

## Definition of done

- [ ] 12 cells complete (2 tasks x 2 arms x 3 repeats), all recorded.
- [ ] Per-arm gate pass rate reported before any efficiency figure.
- [ ] Paired per-task deltas for tool calls, turns, cost, wall-clock.
- [ ] A statement of what the result does **not** support, given n=3 and a
      two-task corpus.
- [ ] A routing recommendation, or an explicit finding that the corpus is too
      small to give one.

---

## Notes for the scorer

Do not fill in the six rubric dimensions. They are the wrong instrument here
and forcing them is what produced BENCH-006's 27-27 tie and BENCH-007's
saturated 30/30. The scorecard for this task carries the harness's own metric
set instead, and the rubric block is marked N/A with that reason.

The interesting result is expected to be *shape-dependent*: a tier that fails
the gate on narrative tracing may pass it on enumeration at a fraction of the
cost. A single global "use tier X" conclusion would be the surprising outcome,
and should be treated with suspicion at this corpus size.
