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

## Updating the lead model

If bench results over several tasks consistently show a different tool outperforming the current lead model on that project's task profile, raise an issue in the source repo with a link to the relevant LEDGER.md rows. The decision to change the lead model belongs to the project owner, not the bench.
