# Scorecard — BENCH-007

> Scoring rubric and anchor definitions: see `rubric.md`.
> All scores are integers 1–5. Total is the sum of all six dimensions (max 30).
> **Off-format:** this is a model-variant meta-bench, not the standard
> four-subscription bench. The rows are four **frontier peer models** —
> Fable, Opus, GPT-5.5, Gemini-Pro — run against the identical brief in
> their own native harnesses. Sonnet/Haiku are not subjects here. See
> `MODELS.md` for the Fable working-hypothesis this task is designed to
> test.

---

## Metadata

| Field | Value |
|-------|-------|
| Task ID | BENCH-007 |
| Date scored | 2026-07-05 — Opus and Fable rows complete; GPT-5.5 and Gemini-Pro pending |
| Scorer | Opus 4.8 orchestrator. The Fable row was scored after independently re-running its test suite (9/9 green) and reading its solution; the Opus row remains a self-assessment. Both are same-provider (Anthropic) scores, not a cross-family independent judge — flagged as a standing limitation of this bench. |
| Brief | [brief.md](./brief.md) |

---

## Tool / model provenance

Record the exact model and harness behind each row — mandatory per the
provenance void rule in `rubric.md`. This is a MODEL-variant bench: the
comparison axis is the model, not the tool/subscription.

| Row | Harness | Underlying model | Provider | Date run | Status |
|-----|---------|-------------------|----------|----------|--------|
| Fable | general-purpose agent (Claude Code), `model=fable`, isolated (no sight of the Opus row) | Fable (frontier-above-Opus tier) | Anthropic | 2026-07-05 | complete — see `fable/output.md` |
| Opus | Claude Code (native) | Claude Opus 4.8 | Anthropic | 2026-07-04 | complete — see `opus/output.md` |
| GPT-5.5 | pending (native GPT-5.5 harness, not yet run) | GPT-5.5 | OpenAI | — | pending — see `gpt-5.5/PENDING.md` |
| Gemini-Pro | pending (native Gemini-Pro harness, not yet run) | Gemini-Pro (frontier tier) | Google | — | pending — see `gemini-pro/PENDING.md` |

**Fable note.** The Fable row was run on 2026-07-05 in an isolated agent
harness with no visibility of the Opus solution, against the identical
`brief.md`. Its test suite was re-executed independently by the scorer
(9/9 green) before scoring. The score below is a real result, not the
`MODELS.md` prior.

---

## Results

| Row | Correctness | Iterations | Quality | Failure mode | Autonomy | Time | **Total** |
|-----|:-----------:|:----------:|:-------:|:------------:|:--------:|:----:|:---------:|
| Fable | 5 | 5 | 5 | 5 | 5 | 5 | **30** |
| Opus | 5 | 5 | 5 | 5 | 5 | 5 | **30** |
| GPT-5.5 | — | — | — | — | — | — | **pending** |
| Gemini-Pro | — | — | — | — | — | — | **pending** |

Both scored rows are Anthropic-family and neither is judged by an
independent cross-family scorer — the Opus row is a self-assessment and
the Fable row is scored by the Opus orchestrator (with an independent
test re-run). This is consistent with the repo's "no automated judge"
model and is the main reason a GPT-5.5 or Gemini-Pro row matters: a
genuinely external row is what would stress-test whether two 30/30s
reflect the task saturating the rubric rather than the scorer being
generous.

---

## Per-row notes

### Fable

Ran the identical brief in one cycle, green on the first execution (the
solver reported zero fix cycles; a pre-run comment-wording tweak is not
a fix). Design: three hash maps (`key→value`, `key→freq`,
`freq→OrderedDict of keys`) plus a running `min_freq` pointer, using
CPython's `OrderedDict` as the recency-ordered doubly-linked list
*within* each frequency bucket — exactly the intra-bucket-LRU use the
brief permits. Eviction reads the head of the `min_freq` bucket via
`next(iter(...))` (O(1) head-read, not a scan). The `min_freq`
maintenance invariant is argued structurally in the module docstring: a
fresh insert unconditionally sets `min_freq = 1`; a bump from `f` can
only empty bucket `f`, whose sole successor candidate is `f+1`. No heap,
no sort, no min-scan — it does not fall into the O(n)/O(log n) trap the
brief plants. Nine tests (the four required cases plus five extras: MRU
marking on `get`, `min_freq` reset after bumps, missing key, negative
capacity, `None`-value storage). One defensible spec extension: it
raises `ValueError` on negative capacity, which the brief neither
requires nor forbids (`capacity == 0` is the only edge the brief names).
Scores: Correctness 5 (all named edge cases handled, verified),
Iterations 5 (one cycle), Quality 5 (clean, idiomatic, structural proof
in prose per the no-timing constraint), Failure mode 5 (no failure
observed), Autonomy 5 (no questions), Time 5 (≈138s wall-clock, under the
5-minute anchor). Total 30/30.

**Fable vs Opus — the one real qualitative difference.** Both reach
30/30, but they reach it differently: Opus hand-rolled an explicit
doubly-linked list (a `_Node` type with `prev`/`next` pointers), while
Fable delegated the intra-bucket DLL to `OrderedDict`. Both are O(1) and
correct. Fable's is fewer lines and leans on a C-level structure that is
hard to get wrong; Opus's is more from-first-principles and makes the
pointer mechanics explicit. Neither is better against the rubric — but
this is the kind of fingerprint difference a curator would flag, and it
is the *only* place the two rows visibly diverge.

### Opus (Claude Opus 4.8)

One-pass solution: two-level doubly-linked-list design (key→Node hash
map, freq→DLL hash map, running `min_freq` pointer), matching the
brief's O(1)-amortised requirement exactly and avoiding the heap/sorted-
structure trap the brief calls out as the likely failure mode. All six
required test cases implemented and passing (verified by executing the
extracted code block directly — 6/6 tests green). Structural O(1)
argument given in prose, not a timing benchmark, per the brief's
constraint. No clarifying questions were needed; brief was unambiguous
enough to proceed in one cycle. Total: 30/30 — no deductions identified
against the rubric anchors, though this is a self-scored row.

### GPT-5.5

Not run — see `gpt-5.5/PENDING.md`. No score fabricated.

### Gemini-Pro

Not run — see `gemini-pro/PENDING.md`. No score fabricated.

---

## Verdict

**Winner:** Tie so far — Fable 30/30 and Opus 30/30 on the two completed
rows. GPT-5.5 and Gemini-Pro remain pending, so this is a provisional
two-of-four result, not a final ranking.

**Runner-up:** n/a (tie).

**Key finding (one sentence):**
On a well-specified O(1)-kernel task, the frontier-above-Opus tier
matches Opus at the rubric ceiling rather than beating it — the brief
**saturates the rubric**, so this task class cannot discriminate between
frontier peers, and the interesting signal is that saturation itself.

**Secondary finding — the Time hypothesis is unfalsifiable here.**
`MODELS.md` predicted Fable would *regress* on Time (slower wall-clock
for a comparable answer). Fable's measured wall-clock was ≈138s, which
still lands in the rubric's coarsest "under 5 minutes → 5" bucket. Since
the Opus row's wall-clock was not captured at run time and both plausibly
sit under 5 minutes, a real wall-clock regression could not surface as a
score difference at this granularity. To actually test the Time prior,
future rows need raw elapsed-time capture, not just the bucketed score —
logged here as a bench instrumentation gap.

**iTone post angle (optional):**
"I gave the same O(1) cache brief — with a heap/scan trap deliberately
baked in — to Opus and to the tier above it, blind to each other. Both
scored a perfect 30/30. The interesting result isn't which won; it's
that a well-specified kernel task is *too easy to separate frontier
models*, and the only visible difference was a stylistic fingerprint
(hand-rolled linked list vs. leaning on the standard library). The
lesson for anyone benchmarking frontier models: if your rubric saturates,
you're measuring the task's difficulty, not the model's ceiling."
See `tasks/BENCH-007/itone-draft.md`.
