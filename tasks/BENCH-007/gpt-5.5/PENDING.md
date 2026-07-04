# BENCH-007 — GPT-5.5 row: PENDING

This row has not been run yet. GPT-5.5 cannot be invoked from this
session (no harness available here); this task was authored and the
Opus row was solved standing in as the Claude-frontier solver, but the
GPT-5.5 row requires a human (or an agent with GPT-5.5 harness access)
to actually paste `../brief.md` into GPT-5.5's own native harness
(Codex CLI / ChatGPT / API, whichever is the designated GPT-5.5
harness for this bench) and capture the real output.

## To complete this row

1. Open a fresh GPT-5.5 session in its native harness.
2. Paste the full, unmodified contents of `../brief.md` as the initial
   prompt — no edits, no hints, no context beyond what the brief itself
   contains.
3. Save the raw output (code + any prose) to `output.md` in this
   directory, in the same format as `../opus/output.md`.
4. Record iteration count, wall-clock time, and any clarifying questions
   asked, for scoring against `rubric.md`.
5. Update `../scorecard.md`'s GPT-5.5 row from "pending" to real scores,
   and update `LEDGER.md`'s BENCH-007 row to reflect completion status
   once all rows (including Fable) are done.

Do not fabricate a score or output for this row in the meantime.
