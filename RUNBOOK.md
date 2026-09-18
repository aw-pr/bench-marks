# RUNBOOK — bench-marks

## Status

- 2026-07-04: Queued (post-exam): run the Fable row on BENCH-007, complete scorecard + LEDGER + iTone draft.

## Purpose

"The Bench" — a four-tool eval harness. The same task is run through Claude Max, Codex Plus, Cursor Pro, and Gemini Plus, scored against `rubric.md`; results feed an iTone Substack series.

## Lead model and boundary

One lead model owns each project's trunk. Cross-model comparison happens only in the bench-marks repo, never on trunk.

This is the ONLY repo where cross-model comparison is allowed; all four tools are deliberately subjects under test on isolated copies of a task. Lead orchestrator is Claude Opus. See `MODELS.md` and `rubric.md`.

## How to run

1. Give `START-PROMPT.md` to a Claude Opus session along with a task description.
2. Claude Opus creates `tasks/<id>/brief.md` from the `templates/` directory.
3. Run each of the four tools against the brief independently.
4. Claude Opus scores `tasks/<id>/scorecard.md` and appends a row to `LEDGER.md`.

## Verification gates

- Every scorecard scores all four tools on all rubric dimensions.
- Claude scores its own run with no self-favouring.
- A `LEDGER.md` row is added for the completed task.

## Task list

- [x] Scaffold rubric, templates, ledger, orchestrator prompt
- [ ] Run BENCH-001: Gray-Scott kernel implementation across all four tools
- [ ] Score BENCH-001, write scorecard, add `LEDGER.md` row
- [ ] Draft first iTone data point from BENCH-001 findings

## Backlog

Subsequent BENCH tasks forked from emergence-lab, aegis, and agentic-rag-kimble work as it arises.
