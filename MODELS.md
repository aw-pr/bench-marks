# Model Policy

## Worker and verifier tiers, chosen per stage card

Work is authored as a stage card that declares a **worker** tier and a
**verifier** tier, and cross-family verification is the default: a worker and a
verifier from different model families catch each other's hallucinated-green
results. Which model leads a given piece of work is a per-card choice, not a
standing property of the repo.

Routing between tiers is measured rather than assumed. The current guide, from
`ab/RESULTS.md`, covers cold repository comprehension only:

| Task shape | Cheapest tier that holds the gate |
|---|---|
| Narrative trace: follow a value through a call chain | Sonnet 5 |
| Enumerative lookup: which callers touch X | Sonnet 5 |

Read as: route down from Opus to Sonnet, and stop there. One tier lower the gate
starts failing on narrative work, and on enumerative work the cheaper tier is
not actually cheaper.

### Superseded: the one-lead-model rule

Until 2026-06-06 this file required one lead model to own each project's trunk,
with comparison happening only in this repo. The rationale was that mixed-model
authorship on a single trunk makes debugging harder, inflates comparisons, and
destroys provenance.

The first and third of those are now handled without the restriction. Per-agent
git authorship records which model wrote each commit, so provenance survives
mixed authorship. The second still holds, and is why cross-tool comparison is
still confined to this repo: a scored bake-off needs isolated arms, and that is
what `tasks/` provides.

Recorded rather than deleted, because the replacement is narrower than the rule
it replaced and it is worth knowing which part was dropped.

## This repo is the exception

In bench-marks specifically, all four tools are deliberately subjects under test. They are run on isolated copies of the same brief and their outputs are captured separately. They do not collaborate. They do not see each other's output before artefacts are saved. The comparison is post-hoc.

## The four tools under test

| Handle | Subscription | Characteristic strength (working hypothesis) |
|--------|-------------|----------------------------------------------|
| `claude` | Claude Max (Opus) | Reasoning, long-context coherence, instruction-following |
| `codex` | Codex Plus | Agentic shell tasks, iterative file editing |
| `cursor` | Cursor Pro | IDE-native refactoring, in-file autocomplete, codebase navigation |
| `gemini` | Gemini Plus | Large-context ingestion, multimodal tasks |

These are working hypotheses to be tested, not conclusions. The bench exists to replace these hunches with scored data.

## Fable working hypothesis (frontier-above-Opus tier)

`Fable` denotes the frontier-tier model above Opus in the Anthropic
lineup. As of BENCH-007, no Fable row has been run — this is a **stated
prior**, to be tested against real scored rows, not a conclusion:

- **Correctness:** hypothesised roughly flat vs. Opus on well-specified,
  bounded kernel/algorithm tasks like BENCH-007 — Opus already reaches
  5/5 correctness on this class of task in one pass, so there is limited
  headroom for Fable to visibly improve on Correctness specifically,
  though it may show on messier or more ambiguous briefs not yet
  benched.
- **Iterations:** hypothesised flat-to-slightly-better — both models are
  expected to converge in one cycle on a brief this well-specified;
  Fable is not expected to need materially fewer or more cycles than
  Opus here.
- **Failure mode:** hypothesised flat-to-better — if Fable fails at all
  on this task class, the prior is that it fails loud (asks a
  clarifying question or flags the O(1) trap explicitly) rather than
  silently producing a heap-based or sorted-structure "O(1)" cache that
  looks plausible but violates the brief's complexity requirement.
- **Time: predicted to REGRESS relative to Opus.** The explicit
  prediction is that Fable will be *slower* wall-clock on this task, not
  faster — more reasoning/deliberation for a comparable or marginally
  better answer, trading Time for headroom on dimensions where Opus is
  already near the ceiling. This is the one dimension where this
  hypothesis predicts a Fable regression rather than a wash or an
  improvement.

This entry is a prior stated before the Fable row is run (see
`tasks/BENCH-007/scorecard.md`, which marks the Fable row explicitly
UNSCORED). It should be checked against, not read into, the eventual
scored result.

### Result vs hypothesis (Fable row run 2026-07-05)

The Fable row scored **30/30**, identical to Opus. Against the prior:

- **Correctness / Iterations / Failure mode / Autonomy:** hypothesis
  held — all flat vs Opus (both 5/5), as predicted for a brief this
  well-specified. Fable did not fall into the O(1) trap and produced a
  correct heap-free design in one pass.
- **Time (predicted to REGRESS):** **not falsifiable at this rubric's
  granularity.** Fable's measured wall-clock was ≈138s, which is still
  inside the coarsest "under 5 minutes → 5" bucket, and the Opus row's
  wall-clock was never captured. A real Fable slowdown therefore cannot
  surface as a score difference here. The Time prior is neither
  confirmed nor refuted — it is untestable without raw elapsed-time
  instrumentation, which is now logged as a bench gap.
- **Meta-finding:** the task **saturates the rubric** for frontier peers.
  Two frontier models both hit the 30/30 ceiling, so this task class
  measures task difficulty, not the model's headroom. To discriminate
  frontier tiers, future BENCH tasks in this class need either a harder
  brief (ambiguous spec, larger design space) or finer-grained anchors
  (raw time, token count, a quality dimension that does not top out at a
  correct-and-clean kernel). The one visible Fable/Opus difference was
  stylistic, not scored: Fable leaned on `OrderedDict`; Opus hand-rolled
  the linked list.

## Acting on a result

A bench result informs how a stage card is authored: which tier to name as
worker, which family to name as verifier. The decision belongs to the person
authoring the card, not to the bench.

Quote a result with its scope attached. Everything measured here is a specific
corpus on a specific date, and several findings reversed once the fixtures were
checked. The reversals are kept in `ab/RESULTS.md` rather than tidied away.
