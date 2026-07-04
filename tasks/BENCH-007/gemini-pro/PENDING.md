# BENCH-007 — Gemini-Pro row: PENDING

This row has not been run yet. Gemini-Pro cannot be invoked from this
session (no harness available here); this task was authored and the
Opus row was solved standing in as the Claude-frontier solver, but the
Gemini-Pro row requires a human (or an agent with Gemini-Pro harness
access) to actually paste `../brief.md` into Gemini-Pro's own native
harness (Gemini CLI / AI Studio, whichever is the designated
Gemini-Pro-frontier harness for this bench, distinct from the `gemini`
row used in the standard four-subscription bench) and capture the real
output.

## To complete this row

1. Open a fresh Gemini-Pro (frontier-tier) session in its native
   harness.
2. Paste the full, unmodified contents of `../brief.md` as the initial
   prompt — no edits, no hints, no context beyond what the brief itself
   contains.
3. Save the raw output (code + any prose) to `output.md` in this
   directory, in the same format as `../opus/output.md`.
4. Record iteration count, wall-clock time, and any clarifying questions
   asked, for scoring against `rubric.md`.
5. Update `../scorecard.md`'s Gemini-Pro row from "pending" to real
   scores, and update `LEDGER.md`'s BENCH-007 row to reflect completion
   status once all rows (including Fable) are done.

Do not fabricate a score or output for this row in the meantime.
