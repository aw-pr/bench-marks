# Scorecard — EXAMPLE-001

> **THIS IS AN EXAMPLE. Scores and notes are illustrative only and do not represent real benchmark data.**

> Scoring rubric and anchor definitions: see `rubric.md`.
> All scores are integers 1–5. Total is the sum of all six dimensions (max 30).

---

## Metadata

| Field | Value |
|-------|-------|
| Task ID | EXAMPLE-001 |
| Date scored | 2026-05-15 |
| Scorer | orchestrator (EXAMPLE) |
| Brief | [brief.md](./brief.md) |

---

## Results

| Tool | Correctness | Iterations | Quality | Failure mode | Autonomy | Time | **Total** |
|------|:-----------:|:----------:|:-------:|:------------:|:--------:|:----:|:---------:|
| claude | 5 | 5 | 4 | 5 | 5 | 5 | **29** |
| codex | 4 | 3 | 3 | 3 | 4 | 4 | **21** |
| cursor | 3 | 3 | 4 | 3 | 3 | 3 | **19** |
| gemini | 4 | 4 | 3 | 4 | 4 | 4 | **23** |

---

## Per-tool notes

### Claude (Claude Max / Opus)

Produced a complete, correct implementation on the first pass. Used `np.roll` for periodic boundaries correctly on both axes. V.max() after 1000 steps was 0.51 (within range). Code was clean but used a slightly verbose variable naming style. No quality issues that would block a PR. Quality deducted one point for minor verbosity rather than any correctness issue.

### Codex (Codex Plus)

Initial output used a loop-based Laplacian instead of vectorised `np.roll`. Correct behaviour, but slower and less idiomatic. Required one cleanup pass to vectorise. Boundary handling was correct on the first attempt. Final result passed all acceptance criteria.

### Cursor (Cursor Pro)

Autocomplete initially produced a Laplacian that used zero-padding rather than periodic boundaries — a silent correctness failure (score 1 was tempting but the error was caught when the V.max() check failed visibly, so scored 3). After one correction prompt specifying "periodic via np.roll" the implementation was correct. Output quality was good once corrected.

### Gemini (Gemini Plus)

Asked one clarifying question before starting: "Should boundary conditions wrap on both axes, or only horizontally?" — appropriate caution given a slightly ambiguous spec. After confirmation, produced a correct vectorised implementation. Autonomy deducted one point for the clarifying question (brief already specified wrap-around, though it could have been clearer). Quality was serviceable but used `np.zeros_like` + manual assignment rather than a direct expression.

---

## Verdict

**Winner:** claude

**Runner-up:** gemini

**Key finding (one sentence):**
On a well-specified numerical task with an explicit function signature, Claude produced a correct, clean implementation in a single pass; the other tools required either correction cycles or clarifying exchanges.

**iTone post angle (optional):**
"When the spec is airtight, one-pass delivery is the differentiator — here is what that actually looked like across four tools."

---

> **REMINDER: This scorecard is an EXAMPLE. All scores, notes, and findings are fabricated for illustrative purposes.**
