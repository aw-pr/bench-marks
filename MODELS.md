# Model Policy

## The one-lead-model rule

One lead model owns each project's trunk. Comparison happens only here, never on other repos' trunks.

In practice: if a project's lead model is Claude Opus, then Claude Opus writes the code that lands on `main`. If a developer wants to explore whether Gemini or Codex would have done better on a specific task, they bring that task to bench-marks, run it in isolation, and score it. The result informs future lead-model decisions; it does not produce a mixed-authorship artefact that gets merged into the source repo.

Rationale: mixed-model authorship on a single trunk makes debugging harder (each model has characteristic failure modes), makes the comparison meaningless (collaboration inflates results), and makes provenance impossible to track.

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

## Updating the lead model

If bench results over several tasks consistently show a different tool outperforming the current lead model on that project's task profile, raise an issue in the source repo with a link to the relevant LEDGER.md rows. The decision to change the lead model belongs to the project owner, not the bench.
