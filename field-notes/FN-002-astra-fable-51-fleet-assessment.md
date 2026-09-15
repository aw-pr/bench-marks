# FN-002 — GPT-6 Astra and Claude Fable 5.1 in production seats

## Metadata

| Field | Value |
|-------|-------|
| FN id | FN-002 |
| Date | 2026-09-15 |
| Source repo(s) | emergence-lab, autometta, fin-ops, reflexivity, contract-crawler |
| Source commits / records | each repo's `state/cost-log.jsonl` and `state/envelopes/`; slate design in `token-maxing/WEEKEND-RUNS.md` |
| Models / harnesses involved | `GPT-6 Astra <gpt-6-astra@local>` (Codex CLI), `Claude Fable 5.1 <claude-fable-5-1@local>` (Claude Code), with Opus 5, Sonnet 5 and Codex GPT-5.6 Terra as the surrounding fleet |
| Status | complete |

## TL;DR

Astra ran 14 metered worker attempts across five repos for 12.0M tokens and
carried nine stages to a pass, at roughly a quarter of an Opus 5 worker attempt
by median token cost. Fable 5.1 was cheaper still in the verifier seat than any
model the fleet has measured, at a 515,906-token median. Neither figure is a
controlled comparison, and both models are cheap partly because they stop early,
which is a virtue in a worker and unproven in a verifier.

## What happened

The weekend of 2026-09-11 was designed as an Astra assessment: nine cards across
five repos, Astra in the worker seat on eight and the verifier seat on one,
Claude models verifying. It was called on hold at 21:36 on the Friday when the
Codex five-hour window closed, with four cards unrun. Those four ran unattended
on 12 and 13 September and all passed; nobody wrote the result down until now.

Fable 5.1 was never a subject of that slate. It had been taking verifier and
worker seats across the fleet since 3 September, and its record is included here
because the two models arrived in production within a week of each other and the
question "what do the new models actually cost" is the same question.

## The numbers

All figures are metered token totals from the per-repo cost ledgers. A *seat* is
one (repo, stage, role) assignment; a seat may take several attempts.

### GPT-6 Astra — 13 seats, 20 rows, 14.4M tokens

| Repo | Stage | Role | Attempts | Tokens | Outcome |
|------|-------|:----:|:--------:|-------:|---------|
| autometta | 135 overnight reserve | worker | 1 | 936,530 | pass |
| autometta | 136 vendor freshness | worker | 1 | 680,196 | pass |
| emergence-lab | 88 zoom camera repair | worker | 1 | 3,157,545 | partial |
| emergence-lab | 90 windowed domain | worker | 1 | 268,160 | fail (correct stop) |
| emergence-lab | 93 PARAM_GROUPS to schema | worker | 1 | 1,399,982 | pass |
| emergence-lab | 94 CPU-fallback default | worker | 3 | 1,387,626 | fail, partial, pass |
| fin-ops | 02 schema catch-up | worker | 2 | 1,087,936 | fail, pass |
| fin-ops | 03 fleet view | worker | 1 | 830,483 | pass |
| fin-ops | 04 run-report export | worker | 1 | 610,910 | pass |
| reflexivity | 12 caption drafting | worker | 1 | 810,979 | pass |
| reflexivity | 14 first live dataset | worker | 1 | 877,380 | pass |
| emergence-lab | 87 zoom diagnostic | verifier | 5 | 1,979,264 | 3 aborted, fail, pass |
| contract-crawler | 01 per-source report | verifier | 1 | 390,901 | fail |

**Worker:** 11 seats, 14 metered attempts, 12,047,727 tokens. Nine seats reached
a pass; seven of those nine passed on the first attempt. Cost per passing stage,
counting every worker attempt including the two that never passed, is 1,338,636
tokens. Median attempt 745,588.

**Verifier:** 2 seats, 3 metered attempts, 2,370,165 tokens. This is too thin to
characterise, and both seats hit harness trouble before they hit the work.

### Claude Fable 5.1 — 9 seats, 11 rows, 8.2M tokens

| Repo | Stage | Role | Attempts | Tokens | Outcome |
|------|-------|:----:|:--------:|-------:|---------|
| emergence-lab | 76 nine-point Laplacian | worker | 2 | 2,312,922 | stalled, pass |
| emergence-lab | 79 Brian's Brain retune | worker | 1 | 537,783 | pass |
| reflexivity | 08 timeline exhibit | worker | 1 | 595,005 | pass |
| autometta | 132 dashboard pulse | verifier | 2 | 2,366,190 | fail, pass |
| autometta | 133 one timezone | verifier | 1 | 412,592 | pass |
| emergence-lab | 82 BZ high activator | verifier | 1 | 441,115 | pass |
| emergence-lab | 85 nine-point default | verifier | 1 | 359,681 | pass |
| emergence-lab | 91 detail adjudication | verifier | 1 | 656,002 | pass |
| emergence-lab | 95 app test-build convention | verifier | 1 | 515,906 | pass |

**Verifier:** 6 seats, 7 attempts, 4,751,486 tokens, every seat reaching a
verdict. 791,914 tokens per seat. **Worker:** 3 seats, 3,445,710 tokens, all
three reaching a pass.

### Median tokens per attempt, against the fleet

| Model | Worker median | n | Verifier median | n |
|-------|--------------:|--:|----------------:|--:|
| Claude Fable 5.1 | 595,005 | 3 | **515,906** | 7 |
| Codex GPT-5.6 Terra | 841,276 | 12 | 600,916 | 8 |
| GPT-6 Astra | **745,588** | 14 | 952,809 | 3 |
| Claude Sonnet 5 | 2,242,564 | 13 | 1,221,602 | 36 |
| Claude Opus 5 | 3,209,808 | 12 | 2,351,165 | 18 |
| Claude Fable 5 | 4,617,912 | 3 | — | 0 |

**Read this table carefully or not at all.** The rows are different cards in
different repos over different weeks. Astra's cards were chosen as the hard
ones; the Opus 5 and Sonnet 5 rows are whatever the fleet happened to dispatch.
The Fable 5 to Fable 5.1 worker gap is n=3 against n=3 on unrelated work and
should not be read as a generational improvement. This is production telemetry,
not a bench.

## What paused or blocked automation

- **The Codex SDK transport rejects Astra.** Every repo that wanted Astra in a
  seat needed a CLI transport override added to its local manifest. Three repos
  got one for this slate.
- **Astra cannot open Chromium under the Codex sandbox,** so no card with a GUI
  requirement can be given to it. Browser roles stay on Claude.
- **emergence-lab 87 burned three aborted verifier dispatches** before a run
  stuck, then failed once more before passing. Five dispatches for one verdict.
- **fin-ops 02's first failure was a harness timing gap, not a model result.**
  The tick cut the run worktree from the old dev tip before the card's fixture
  commit landed, so Astra found no fixture and stopped at 199,794 tokens without
  touching a file. Correct conduct, wasted dispatch.
- **contract-crawler 01 is still open.** Astra, in the verifier seat, failed it
  on two criteria: seven pre-existing stale-date test failures and a denied
  socket in the existing suite, neither caused by the worker's change, and card
  text naming `data/state/jobs.jsonl` paths that do not exist in a run worktree
  because state is symlinked and ignored. Both findings were correct. The card
  is defective and the baseline was dirty; it needs a re-brief, not a retry.

## Lessons

1. **Cheap attempts are not the same as cheap outcomes.** Astra's 745,588-token
   median is flattered by the attempts where it correctly refused to work: 268k
   on stage 90 when the card's premise was overturned, 199k on fin-ops 02 when
   the fixture was absent. Judge a worker on cost per passing stage
   (1,338,636 here) and count the seats that never passed.
2. **The best Astra result and the worst are the same behaviour.** Stopping
   early when the card is wrong is exactly what a worker should do, and it is
   indistinguishable in the ledger from stopping early because it gave up. Only
   the envelope notes separate them, which is an argument for keeping the
   scorecard block mandatory in the dispatch envelope.
3. **A model that needs a transport override is not free.** Astra's per-attempt
   cost is the cheapest measured in the worker seat, and it came with a manifest
   change in three repos, a class of card it cannot be given, and five
   dispatches to get one verdict out of a verifier seat. The harness friction is
   real spend that the token ledger does not record.
4. **Fable 5.1 is the cheapest verifier the fleet has measured,** at 42% of
   Sonnet 5's median attempt and 22% of Opus 5's, over seven attempts with every
   seat reaching a verdict. That is the most immediately actionable number in
   this note and the one most worth testing deliberately rather than observing.
5. **Nine stages passed and the record sat unwritten for four days.** The
   weekend's compute finished itself; the assessment did not. An unattended
   fleet writes ledger rows, not conclusions.

## Publishable angle

Two frontier models arrived in the same week and the interesting number was not
which one was smarter. It was that the cheapest model in the fleet was cheap
partly because it knew when to quit, and that telling "correctly refused" apart
from "gave up" needed a human reading nine envelopes four days later.

## Links

- Per-repo ledgers: `<repo>/state/cost-log.jsonl`, `<repo>/state/envelopes/`
- Slate design and hold: `token-maxing/WEEKEND-RUNS.md`, `token-maxing/HANDOFF.md`
- contract-crawler stage 01 was re-briefed and re-dispatched 2026-09-15 with
  Fable 5.1 in the worker seat and Astra retained as verifier (card commit
  `c8f4b5f`). When it lands it adds the second Astra-as-verifier seat and the
  first Fable 5.1 worker seat outside emergence-lab and reflexivity; both
  tables above are stated as of 2026-09-15 and will need the new rows.
