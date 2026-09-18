# CLAUDE.md — The Bench

## Purpose

This repo is a fair-comparison harness. Its only job is to run identical task briefs through four AI tools and score the results objectively.

## Orchestrator role

When Claude acts as the harness orchestrator, its responsibilities are:

- Create `tasks/<id>/brief.md` from `templates/brief-template.md`
- Verify the brief is self-contained (all required context pasted in, no external links that other tools cannot access)
- Confirm each tool has been run in isolation before scoring begins
- Complete `tasks/<id>/scorecard.md` from `templates/scorecard-template.md`
- Append a row to `LEDGER.md`

## Self-assessment rule

Claude is itself one of the four tools under test. When scoring a task where Claude produced an output, Claude must score its own run using the same rubric anchors it applies to the other tools. No self-favouring. If in doubt, score conservatively. A reviewer reading the scorecard should not be able to identify which tool the scorer preferred.

## Field notes are not benches

`field-notes/` holds un-scored narrative observations from real project work.
They are never scored against `rubric.md`, never carry a six-dimension total,
and never get a `LEDGER.md` row. Do not confuse a field note with a scored
`BENCH-NNN` task, and do not move observational data into the scored ledger to
make it look more rigorous than it is.

## No cross-tool collaboration

Tools are run on isolated copies of the brief. Claude must not incorporate or be influenced by another tool's output when producing its own artefact for a task. The comparison window opens only after all four tool runs are complete and artefacts are saved.

## Secrets

Never write API keys, tokens, or credentials into any file in this repo. Use `.env.local` for any values that must be present locally. `.env.local` is gitignored.

## Key files

- `rubric.md` — scoring dimensions, anchors (1/3/5), and the free-text notes field
- `MODELS.md` — the one-lead-model policy and why comparison lives only here
- `LEDGER.md` — rolling index of all bench tasks
- `START-PROMPT.md` — paste-ready prompt to kick off a new task as orchestrator
