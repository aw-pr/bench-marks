# Cleanup prompt — bench-marks

Paste into Claude Opus (lead orchestrator). Read `RUNBOOK.md`, `rubric.md`,
`MODELS.md` first; do not restate them.

## Deltas only

1. **BENCH-001 is run but uncommitted.** `LEDGER.md` modified, `tasks/BENCH-001/`
   untracked. Before committing, verify the scorecard against `rubric.md`:
   every one of the four tools scored on every dimension, Claude's own run
   scored with no self-favouring, and the `LEDGER.md` winner row matches the
   scorecard total. Fix any gap, then commit as one unit (`feat(bench):
   BENCH-001 …`).
2. **Provenance is already wired** into `templates/scorecard-template.md` (the
   "Tool provenance" block + harness-isolation note) and enforced by the void
   rule in `rubric.md` — do not re-add it. Just bring
   `tasks/BENCH-001/scorecard.md` up to the new template: add a provenance
   block. BENCH-001's Cursor row was dropped (prose brief), so mark it void
   per the rule, not scored — the joint-29 claude/codex result stands.
3. **Publishable content:** the RUNBOOK task list still shows BENCH-001 as not
   run. Tick it and add the "first iTone data point" line as a real next
   action, not a backlog item — Codex edging Claude on voice-writing is the
   hook.

## Done =

`git status` clean, scorecard rubric-complete, Cursor-model field in the
template and backfilled, RUNBOOK current. Push only on Tony's explicit
go-ahead (origin/dev is the public remote).
