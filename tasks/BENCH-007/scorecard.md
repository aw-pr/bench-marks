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
| Date scored | pending — only the Opus row is complete as of 2026-07-04 |
| Scorer | orchestrator (Claude, standing in as Opus solver) |
| Brief | [brief.md](./brief.md) |

---

## Tool / model provenance

Record the exact model and harness behind each row — mandatory per the
provenance void rule in `rubric.md`. This is a MODEL-variant bench: the
comparison axis is the model, not the tool/subscription.

| Row | Harness | Underlying model | Provider | Date run | Status |
|-----|---------|-------------------|----------|----------|--------|
| Fable | n/a | Fable (frontier-above-Opus tier) | Anthropic | — | **UNSCORED — pending, post-exam** |
| Opus | Claude Code (native) | Claude Opus 4.8 | Anthropic | 2026-07-04 | complete — see `opus/output.md` |
| GPT-5.5 | pending (native GPT-5.5 harness, not yet run) | GPT-5.5 | OpenAI | — | pending — see `gpt-5.5/PENDING.md` |
| Gemini-Pro | pending (native Gemini-Pro harness, not yet run) | Gemini-Pro (frontier tier) | Google | — | pending — see `gemini-pro/PENDING.md` |

**Fable note.** Fable is explicitly left unscored in this scorecard. No
folder, output, or score has been fabricated for it. Per `LEDGER.md` and
`MODELS.md`, the Fable row is queued to run once the model is available
to this operator (see the HANDOFF.md status line for BENCH-007).

---

## Results

| Row | Correctness | Iterations | Quality | Failure mode | Autonomy | Time | **Total** |
|-----|:-----------:|:----------:|:-------:|:------------:|:--------:|:----:|:---------:|
| Fable | — | — | — | — | — | — | **UNSCORED (pending — post-exam)** |
| Opus | 5 | 5 | 5 | 5 | 5 | 5 | **30** |
| GPT-5.5 | — | — | — | — | — | — | **pending** |
| Gemini-Pro | — | — | — | — | — | — | **pending** |

Opus scores are this operator's honest self-assessment against the
rubric anchors (see `opus/output.md`'s self-review section), not an
independent judge — flagged here as a limitation, consistent with this
repo's "no automated judge" scoring model.

---

## Per-row notes

### Fable

Not run. This row is reserved and intentionally left blank rather than
estimated. See `MODELS.md` for the stated *working hypothesis* about
what a Fable row is predicted to look like on this task class — that
hypothesis is a prior, not a result, and must not be read as a score.

### Opus (Claude Opus 4.8)

One-pass solution: two-level doubly-linked-list design (key->Node hash
map, freq->DLL hash map, running `min_freq` pointer), matching the
brief's O(1)-amortised requirement exactly and avoiding the heap/sorted-
structure trap the brief calls out as the likely failure mode. All six
required test cases implemented and passing (verified by executing the
extracted code block directly — 6/6 tests green). Structural O(1)
argument given in prose, not a timing benchmark, per the brief's
constraint. No clarifying questions were needed; brief was unambiguous
enough to proceed in one cycle. Total: 30/30 — no deductions identified
against the rubric anchors, though this is a self-scored row (see
Results note above) and should be revisited once a genuinely independent
frontier row (GPT-5.5, Gemini-Pro, or a fresh Fable pass) is available
to sanity-check whether 30/30 self-scoring is itself a bias signal worth
tracking across future rows in this bench.

### GPT-5.5

Not run — see `gpt-5.5/PENDING.md`. No score fabricated.

### Gemini-Pro

Not run — see `gemini-pro/PENDING.md`. No score fabricated.

---

## Verdict

**Winner:** TBD — cannot be determined with three of four rows
incomplete (Fable unscored, GPT-5.5 pending, Gemini-Pro pending). Opus
is the only scored row and is provisionally in the lead by default, not
by comparison.

**Runner-up:** TBD.

**Key finding (one sentence):**
Not yet determinable — this scorecard captures a real, verified Opus
solution as the baseline row; the comparative finding this bench exists
to produce (does the frontier-above-Opus tier change correctness,
iteration count, or failure mode, and does it cost more time — see the
Fable working-hypothesis in `MODELS.md`) requires the three pending rows
to be completed first.

**iTone post angle (optional):**
"An LFU cache with a real O(1) trap baked into the brief (the heap/
sorted-structure temptation) as a lens on whether the newest frontier
tier is actually *more* correct on a well-specified kernel task, or just
slower to get to the same correct answer Opus already reaches in one
pass" — pending the Fable/GPT-5.5/Gemini-Pro rows to have real data
behind it.
