# Field-Note Start Prompt

Paste the block below to a Claude Opus session to (a) scaffold the un-scored
`field-notes/` stream the first time it is run, and (b) author the first field
note (FN-001) from the fractals JSON-key-order incident.

**What this is.** Field notes are un-scored, narrative, publish-facing
observations from real project work — multi-model timelines, automation
incidents, rework/misdiagnosis stories. They feed the iTone series alongside the
scored benches but are NOT scored against `rubric.md` and must not be confused
with scored `BENCH-NNN` tasks. After the stream exists, reuse `field-notes/TEMPLATE.md`
for subsequent notes; this prompt only needs running once (for scaffold + FN-001).

---

```
You are the orchestrator for "The Bench" (bench-marks repo). Your job is a
STRUCTURE change plus authoring the first entry of a new stream — NOT to run a
scored bench task.

Working dir: the root of this repo (bench-marks)

## Step 0 — read first
Read README.md, CLAUDE.md, MODELS.md, rubric.md, LEDGER.md, and
templates/. Understand that the scored BENCH-NNN four-tool format is sacred and
must NOT be modified or diluted.

## Step 1 — add a new "field-notes" stream (un-scored incident debriefs)
The scored benches compare tools head-to-head. There is no home for real-project
episodes that are publishable but are NOT fair four-tool comparisons (multi-model
timelines, automation incidents, rework/misdiagnosis stories). Create that home:

1. Create field-notes/README.md explaining the stream: un-scored, narrative,
   publish-facing observations sourced from real project work; feeds the iTone
   series alongside scored benches; NOT a substitute for a BENCH task and NOT
   scored against rubric.md. Make explicit: field notes POINT BACK to source-repo
   commits/docs and do not duplicate engineering detail (canonical engineering
   record stays in the source repo's docs/LEARNINGS.md + metrics ledger).
2. Create field-notes/TEMPLATE.md with sections: Metadata (FN id, date, source
   repo, source commits, models/harnesses involved, status), TL;DR (2-3 lines),
   What happened, Cost & churn (time, test/tool runs, token cost if known,
   number of failed hypotheses), What paused/blocked automation, Root cause,
   Lesson(s), Publishable angle (the Substack hook), Links (source commits/docs).
3. Create field-notes/INDEX.md: a rolling table (FN id | date | source | one-line
   | models | link) — keep this SEPARATE from LEDGER.md so the scored dataset
   stays clean.
4. Add a short "Field notes" subsection to README.md pointing at field-notes/,
   and a one-line note in CLAUDE.md that field notes are un-scored and must not
   be confused with scored BENCH tasks.

## Step 2 — author the first field note: FN-001
Create field-notes/FN-001-json-key-order-flap.md from the template, using ONLY
the facts below (do not invent numbers; mark anything unknown as "unknown").

Source repo: fractals-from-the-90s
Source commits on dev: 08bd446 (fix: canonical scene JSON key ordering, Opus 4.8),
2d5078b (feat: U-USA-9 glitch count in HUD). Source engineering record:
docs/LEARNINGS.md and docs/metrics/ledger.ndjson in that repo.

WHAT HAPPENED: A conformance-test "flap" (tests u7StateConformance,
u8PersistenceSchemaVersion, u16CopySceneJSON) was tracked from 2026-05-22 as an
intermittent Coordinator state-mutation / NotificationCenter race. It was chased
across stages U-FIX-2, U-FIX-3 (two Codex GPT-5.5 loops, then human-escalated),
and an unattended AUTO-6 loop (parked), with a "Coordinator structural refactor
(single source of truth + explicit committed() yield)" planned as the fix.
On 2026-06-08 the real cause was found: NONDETERMINISTIC JSON KEY ORDERING.
The tests compared scene snapshots by raw JSON bytes; Foundation's JSONEncoder
emits keyed-container keys in a hash-seed-dependent order and ignores
SceneSnapshot's custom ordered encode(to:). Two encodes of the same scene were
byte-identical in VALUE but differed in key ORDER — the "same byte length,
different content" symptom. Fixed in one line of intent: .sortedKeys on the
production encoders (sceneJSONData, persistSession) and the test-side comparison
encoders. Suite then deterministically green (36/36 across repeated runs).

COST & CHURN: ~3 weeks of intermittent investigation across multiple loops/models
before diagnosis. In the final diagnosis+fix work: ~29 full xcodebuild test runs,
and 3 wrong hypotheses (GPU-denormal scope, NotificationCenter cross-talk,
renderer cross-thread write) were tried and disproved BEFORE the decisive move —
instrumenting the actual JSON diff — which took ~2 runs and should have been first.

Token/cost figures from Claude Code `/usage` for the Opus 4.8 session that did the
diagnosis + fix + this debrief (record these, WITH the caveats):
  - ~738k output tokens, ~104k uncached input, ~154.3M cache-read, ~2.8M cache-write.
  - 341+ assistant turns; ~3h 9m API compute over a ~5-day wall-clock window;
    2701 lines added / 169 removed across the session.
  - Notional cost $113.48 — this is the API-EQUIVALENT figure Claude Code computes;
    it was a Claude Max SUBSCRIPTION session, so it was NOT actual spend. Report it
    as "notional/subscription," never as a bill.
  - The cache-read total dwarfs everything and is CHEAP (re-reading context each
    turn; `/usage` flagged 65% of usage at >150k context). Do not present 154M as
    spend-equivalent.
  - UPPER-BOUND caveat: this 5-day session also contains non-flap work (the auto-3
    feature, a `/handoff` ~12%, `/repo-publish-docs-review` ~2%, and the bench-marks
    review). So these totals over-count the flap incident in isolation; the flap
    diagnosis+fix was the dominant chunk but not the whole figure. State this.

WHAT PAUSED AUTOMATION: The unattended loop's skip-on-red rule parked two
branches — auto-3 (a separate test, u15, went red due to a GPU denormal
flush-to-zero FALSE failure) and auto-6 (the flap "fix" regressed the suite).
Skip-on-red behaved correctly; it cannot distinguish a misdiagnosed/false-red
test from a real defect, so it stopped and waited for a human. The gap was
upstream, in diagnosis quality, not in the rule.

MODELS INVOLVED (timeline, NOT a scored head-to-head): GPT-5.5 (via Codex) made
the U-FIX-3 attempts and the AUTO-6 attempt under the NotificationCenter
hypothesis; Claude Opus 4.8 found the JSON-ordering root cause and shipped the
fix. Frame this as a process/economics observation, not a fair comparison.

LESSONS: (1) Byte-comparing JSON is the anti-pattern — compare decoded Equatable
structs, or pin .sortedKeys; a byte-equality test is testing the encoder, not the
data. (2) "Same byte length, different content" means key ordering — instrument
the diff (print the two blobs) BEFORE theorising about state/concurrency. (3)
Skip-on-red automation can't tell a misdiagnosed test from a real failure; the
cheap win is faster human triage of WHY red, not changing the rule. (4) The real
cost was diagnostic, not the fix: ~3 weeks and multiple model-loops chasing a
concurrency ghost, plus a long high-context Opus session (cache-read-dominated,
65% at >150k context) to finally instrument it. One-line fix, three-week tail —
cheap instrumentation early would have collapsed the whole cost curve.

PUBLISHABLE ANGLE: A concurrency ghost that survived three weeks and multiple
agents because no one printed the two failing values; the cure was one
deterministic-encoding flag. Good Substack hook on how agentic debugging picks
plausible-but-wrong root causes and how cheap instrumentation beats clever theory.

## Step 3 — index + finish
Add an FN-001 row to field-notes/INDEX.md. Do NOT touch LEDGER.md, rubric.md,
MODELS.md, or templates/. Commit on a new branch (not main) with atomic commits:
one for the field-notes scaffold, one for FN-001. Print a summary and the paths
created. Do not push.
```
