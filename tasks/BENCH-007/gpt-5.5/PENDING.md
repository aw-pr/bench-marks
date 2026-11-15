# BENCH-007 GPT-5.5 row: run, not yet scored

The row was run on 2026-10-10 by `run-codex.sh`: `codex exec`, model
`gpt-5.5` (no substitution needed), reasoning effort `high`, in an empty
workspace outside this repo holding only `../brief.md`, so the model could not
see the Opus or Fable rows.

| File | What it is |
|---|---|
| `output.md` | the model's final message, unedited |
| `lfu_cache.py` | the solution file it wrote |
| `run-meta.json` | usage, wall-clock, commands run, quota used, and the self-test result |
| `transcript.jsonl` | the Codex event stream for the run |

The transcript is as recorded except for one redaction: the home directory in
two CLI configuration warnings is shown as `~`.

## To score this row

1. Re-run `python3 lfu_cache.py` independently, as was done for the Fable row.
   The self-test in `run-meta.json` is the run's own check, not the scorer's.
2. Score it against `rubric.md` and fill the GPT-5.5 rows in
   `../scorecard.md`.
3. Update the BENCH-007 row in `LEDGER.md` once every row is done.

Do not fabricate a score in the meantime.
