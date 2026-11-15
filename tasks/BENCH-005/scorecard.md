# Scorecard: BENCH-005

> Scoring rubric and anchor definitions: see `rubric.md`.
> All scores are integers 1–5. Total is the sum of all six dimensions (max 30).

---

## Metadata

| Field | Value |
|-------|-------|
| Task ID | BENCH-005 |
| Date run | 2026-05-23 |
| Date scored | 2026-10-10 |
| Scorer | orchestrator (Claude Opus 5.5). Self-assessment rule applies: the claude row is an Anthropic lane and was scored with the same anchors as the codex row, conservatively where in doubt |
| Brief | [brief.md](./brief.md) |
| Evidence base | [claude/bench-summary.md](./claude/bench-summary.md), [codex/bench-summary.md](./codex/bench-summary.md), and the claude lane's five commits in the source repo (`cbced00`, `7c9904c`, `37ffdf7`, `8bcc0a7`, `8221969`), read with `git show`. The codex lane made no commits and its worktree no longer exists, so its row rests on the summary alone |

---

## Tool provenance

| Tool row | Harness | Underlying model | Provider |
|----------|---------|------------------|----------|
| claude | Claude Code (native) as orchestrator and verifier; T2 workers via Agent tool sub-agents; T1 workers via `codex exec --sandbox workspace-write` (codex-cli 0.132.0) | Orchestrator Claude Opus 4.7 (`claude-opus-4-7`). Workers: Claude Sonnet 4.6 (inventory, card), Codex GPT-5.3 (loops 1 and 2) | Anthropic (orchestrator), mixed workers |
| codex | Codex CLI (native) as orchestrator and verifier; all workers via nested `codex exec` | Orchestrator model **not recorded** in the summary. Inferred Codex GPT-5.3 (`gpt-5.3-codex`): it is the config default `agent-whoami` resolved for the workers in both lanes on the same machine that day, and the default recorded in BENCH-003 two days earlier. Workers: Codex GPT-5.3 for all four dispatches | OpenAI |
| cursor | not run, skipped by design (brief metadata: meta-bench on orchestration) | n/a | n/a |
| gemini | not run, skipped by design (brief metadata: meta-bench on orchestration) | n/a | n/a |

**Tier note.** The rows are not tier-matched below the orchestrator. The claude
lane used Sonnet 4.6 for the two doc steps and Codex GPT-5.3 for implementation;
the codex lane used Codex GPT-5.3 throughout. Both lanes therefore ran the
*same implementer model* on the two loops that decided the Acceptance result,
which makes the implementation outcome a weak signal about the orchestrators
and the contract handling a stronger one. The codex orchestrator model is an
inference, not a record; the row is scored rather than voided because the void
rule exists for multiplexing wrappers, and a native Codex CLI run on a recorded
config default is interpretable. Treat it as a caveat on the row.

---

## Results

| Tool | Correctness | Iterations | Quality | Failure mode | Autonomy | Time | **Total** |
|------|:-----------:|:----------:|:-------:|:------------:|:--------:|:----:|:---------:|
| claude | 2 | 1 | 3 | 4 | 5 | 3 | **18** |
| codex | 1 | 1 | 2 | 3 | 3 | 3 | **13** |
| cursor | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| gemini | n/a | n/a | n/a | n/a | n/a | n/a | n/a |

Both lanes escalated after exhausting the 2-loop budget. Neither reached the
Acceptance pass condition (`0`), so neither row can score above 2 on
correctness, and both score 1 on iterations ("never reached an acceptable
state"). The gap between the rows is almost entirely about what each lane left
behind that can be checked, not about the refactor.

---

## Per-tool notes

### Claude (Opus 4.7 orchestrating Sonnet 4.6 + Codex GPT-5.3)

Four worker dispatches (two Sonnet, two Codex) plus two out-of-sandbox
verifications by Opus. The summary counts six by including the verifier steps;
on a worker-dispatch basis it matches the codex lane's four. Five commits
cover the run from 20:04 to 20:28 BST, consistent with the reported ~27 min.

- **Correctness 2.** Acceptance printed `20` (all twenty runs flapped), against
  a pre-U-FIX-4 baseline of roughly 19/20. Loop 1 did close the original
  bookmark-jump assertion (u7:740) on a single-run probe, but introduced
  deterministic failures at u7:757 and u8:802/870/883, two of which were green
  on the baseline per the lane's own stash comparison. Loop 2 did not recover
  them. Every other DoD item is present and checkable: the stage card follows
  `STAGE-TEMPLATE.md` with the Acceptance command verbatim, commits are
  authored via `agent-whoami` identities with the human user as committer,
  loop-N brief and output files exist, `HANDOVER.md` swaps the U-FIX-3 entry
  for a U-FIX-4 escalation note, and the card status is `escalated`. Not 1
  because only the Acceptance requirement is missing; not 3 because that
  requirement is the core one.
- **Iterations 1.** Two implementation loops, budget exhausted, never
  acceptable. A 1-line orchestrator compile fix sat between loop 2 and its
  verification.
- **Quality 3.** The inventory (186 lines, 24 async sources, 18 mutation
  paths) and the card are strong orchestrator artefacts, and the commit bodies
  are unusually good as an audit trail. Deductions: both loop briefs commit
  the absolute home-directory worktree path in their headers, against the
  brief's sanitisation constraint and while instructing the worker never to
  embed one; the Swift work for both loops lands as one commit, so the loop-1
  diff is not separately recoverable; and the evidence contradicts itself on
  u7:740 (summary: passes "on most runs"; loop-2 output: u7 fails at 740
  and/or 757 on 19 of 20 runs, then "a slim majority" of passes). The
  refactor itself regressed previously green assertions.
- **Failure mode 4.** The load-bearing rule held: Codex self-reported success
  on both loops ("no blocker; self-check passed") and the out-of-sandbox
  verifier caught both overclaims. The escalation is loud, specific and ends
  with a concrete next card (U-FIX-5, observer-chain inventory first).
  Not 5 because the lane's own reporting overclaims at the margin: the summary
  lists "None material" under deviations while the committed briefs leak home
  paths; loop 1 was verified with a single-run probe rather than the
  Acceptance command the lane's own card says to "run verbatim" (reasonable
  given deterministic failure, but undeclared as a deviation); and loop-2
  output calls the funnel ordering "provably correct" with no proof offered.
  The orchestrator-verifier also patched the implementation before verifying
  it. That was disclosed and trivial, but it is the verifier touching
  implementer output.
- **Autonomy 5.** No operator intervention is recorded in the summary or the
  run evidence, and the commit timeline is continuous. Scored on the same
  basis as the codex row: interventions the lane recorded, of which there are
  none here.
- **Time 3.** ~27 min self-reported; the commit timestamps (first commit
  20:04 after ~3 min of Sonnet work, last 20:28) corroborate it. Inside the
  5–30 min band, close to its upper edge.

Housekeeping risk: the `bench/u-fix-4-opus` branch no longer exists in the
source repo. The five commits survive only as unreferenced objects and will be
lost on the next `git gc` prune unless a ref is put back on `8221969`.

### Codex (Codex CLI orchestrating Codex GPT-5.3)

Four worker dispatches (inventory 49s, card 43s, loop 1 127s, loop 2 90s), with
a full 20-run Acceptance after each loop. No commits were made and the
worktree is gone, so none of the files the summary lists (inventory note,
card, loop outputs, verifier outputs) can be inspected. Every score below is
taken from the summary's self-report and scored conservatively.

- **Correctness 1.** Acceptance `12` after loop 1 and `18` after loop 2; the
  lane stopped at the loop-2 state. Beyond the failed Acceptance, the
  explicit DoD item "at least one commit on `bench/u-fix-4-codex` authored via
  `agent-whoami`" is not met, the summary does not mention loop-N brief files
  or a `HANDOVER.md` update, and contract step 7 (commit) was skipped. Key
  requirements missing, so the 1 anchor.
- **Iterations 1.** Two implementation loops, budget exhausted, never
  acceptable. The orchestrator also had to correct a malformed Acceptance
  block in the worker-authored card before loop 1.
- **Quality 2.** No diff, card or brief survives to assess. The one quality
  signal recorded is negative (dispatch 2 wrote a malformed Acceptance loop
  into the card). The summary itself is clear but thin. Scored below the
  serviceable anchor because "serviceable" cannot be shown from what exists;
  this partly double-counts the missing commit already reflected in
  correctness, and is flagged as a judgement call below.
- **Failure mode 3.** Good catches: the verifier ran the full 20-run
  Acceptance outside the worker sandbox on both loops, the malformed card
  Acceptance was caught before dispatch, and the missing commit and the
  permission escalation are both declared openly. Not higher because the
  escalation carries no diagnosis (no failing tests named, no suspected root
  cause, no next step), which the brief asks for explicitly ("record the
  escalation reasoning carefully"), and the summary's "seven-step flow
  executed" relabels step 7 as "stop/escalation decision" when the commit step
  did not happen. Whether the workers overclaimed success is not recorded.
- **Autonomy 3.** Nested `codex exec` needed elevated permission
  (`Operation not permitted` without escalation), which in Codex CLI is an
  operator approval. The summary does not say how many approvals were given
  (one per dispatch would be four); scored at the one-or-two anchor as the
  most generous reading the evidence supports.
- **Time 3.** No total wall-clock recorded. A lower bound from the summary is
  ~5 min of worker time plus two full 20-run Acceptance loops (~4.6 min each
  on the same machine per the claude lane), so at least ~14 min. Nothing shows
  it exceeded 30 min, so the 5–30 band, with the caveat that it is inferred.

### Cursor / Gemini

Not run by design, per the brief's metadata. No harness-delta comparison applies.

---

## Two-family invariant (for autometta memory)

- The implementer ≠ verifier boundary held in both lanes. Both orchestrators
  ran Acceptance outside the worker sandbox and both escalated at the budget
  rather than weakening the command. That is the contract working under two
  orchestrator families.
- The asymmetry is audit trail. The Opus lane committed card, briefs, outputs
  and the Swift diff with per-agent authors; the Codex lane committed nothing,
  so its run now exists only as a self-report. For a contract whose point is
  verifiable evidence, step 7 is not optional on an escalated run.
- The implementer was the same model (Codex GPT-5.3) in both lanes for both
  loops, and both lanes failed the same Acceptance. The structural refactor
  defeated the 2-loop card scope regardless of orchestrator, which repeats the
  U-FIX-3 finding and supports the claude lane's U-FIX-5 recommendation.

---

## Judgement calls that moved the result

1. **Escalation is not "acceptable" for iterations.** Both rows take 1 on
   iterations because neither reached a green Acceptance. Treating
   escalation as the endpoint would lift both to 3 and change neither the
   ranking nor the gap.
2. **Missing commits cost the codex row on correctness and quality.** The
   missing commit is an explicit DoD failure (correctness 1 vs 2), and the
   absence of inspectable artefacts held quality to 2. Scoring codex quality
   at 3 on the benefit of the doubt would narrow the gap to 18 vs 14 and still
   leave claude ahead.
3. **The codex row is scored, not voided, despite an unrecorded orchestrator
   model**, on the inference set out under Tool provenance. Voiding it would
   leave BENCH-005 with no comparison at all.

---

## Verdict

**Winner:** claude (18 vs 13)

**Runner-up:** codex

**Key finding (one sentence):**
Both orchestrators held the implementer ≠ verifier boundary and both escalated
an Acceptance that the same Codex GPT-5.3 implementer could not turn green, so
the separating factor was audit trail: the Opus lane left five attributable
commits and checkable evidence, while the Codex lane committed nothing and
survives only as self-report.

**iTone post angle (optional):**
When two orchestrators fail the same task, the useful one is the one that
failed in writing: an escalation you can audit is worth more than a better
FLAP count you cannot.
