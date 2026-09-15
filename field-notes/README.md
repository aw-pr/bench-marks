# Field Notes

Un-scored, narrative, publish-facing observations sourced from real project
work. Field notes are the home for episodes that are worth writing up but are
**not** fair four-tool comparisons: multi-model timelines, automation incidents,
rework and misdiagnosis stories, and production telemetry from the Autometta
fleet.

## What a field note is not

- **Not a scored `BENCH-NNN` task.** Field notes are never scored against
  `rubric.md`, never carry a six-dimension total, and never appear in
  `LEDGER.md`. The scored four-tool format is deliberately narrow: one brief,
  run in isolation, scored post-hoc. Diluting it with observational data would
  destroy the only property that makes the ledger worth keeping.
- **Not the engineering record.** A field note points back at the source repo's
  commits, envelopes and metrics ledger. It does not duplicate the engineering
  detail. The canonical record stays where the work happened.

## What a field note is for

The scored benches answer "which tool is better on this task". Field notes
answer the questions the bench cannot reach: what a model costs per passing
stage in production, how it fails when nobody is watching, what harness friction
it brings with it, and what a multi-model timeline actually looked like.

They feed the iTone Substack series alongside the scored benches.

## Using the stream

- Copy `TEMPLATE.md` to `FN-NNN-short-slug.md`.
- Use only facts you can source. Mark anything unknown as "unknown" rather than
  estimating.
- Add a row to `INDEX.md`. Leave `LEDGER.md` alone.
