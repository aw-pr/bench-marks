# Task Brief — BENCH-009

> A **lever meta-bench**, the Codex counterpart of BENCH-008. The thing being
> benchmarked is the Codex model tier: on cold repository comprehension, does
> Luna reach the answer Terra reaches, and at what share of the 5-hour window?
> Both arms run the identical prompt, corpus, sandbox and reasoning effort; the
> only variable is `-m`.
>
> Written up after the run from the lever as registered before it: the arms,
> grid and question below are the `codex_tier` entry in `ab/levers.yaml` as
> committed in `f97c17d`, before any cell ran.

---

## Metadata

| Field | Value |
|-------|-------|
| Task ID | BENCH-009 |
| Date | 2026-10-10 (run), 2026-11-15 (written up) |
| Source repo | fractals-from-the-90s |
| Source issue / PR | n/a — `token-maxing/TOKEN-SPEND-TODO.md` item 3, the Codex half of the routing guide |
| Lanes | **control** = `gpt-5.6-terra`, **treatment** = `gpt-5.6-luna`, both `codex exec --sandbox read-only` at `model_reasoning_effort=medium`. claude, cursor and gemini lanes N/A: single-harness tier A/B. |
| Harness | `ab/` at `acd529e`, run unattended by `ab/bin/overnight.sh` |

---

## Spec

All four corpus tasks, n=5 per arm, in one randomised order:

- **T1 orbit trace**: narrative comprehension over Swift.
- **T2 viewport consumers**: enumerative dependency lookup over Go.
- **T3 Go package types**: the exported types of every package under `internal/`.
- **T4 Swift declared types**: every type declared in the Swift sources.

T3 and T4 are restricted to the levers that cannot delegate; `codex exec`
cannot, so every command it runs reaches the stream being counted.

---

## Constraints

- Correctness is a **gate**: each task's answer key is a list of terms the
  final answer must name. Efficiency is compared only across passing runs.
- A Plus subscription reports no price. Cost is `quota_pct_used`, the share of
  the 5-hour window a cell drew, read from the run's own rollout, and
  `credits_spent` must be 0.
- Run overnight, on the assumption that nothing else draws on the window at
  that hour. The scorecard records where that assumption failed.

---

## Definition of done

- [x] 40 cells complete (4 tasks x 2 arms x 5 repeats), all recorded.
- [x] `credits_spent` checked on every record before any other figure.
- [x] Per-arm gate pass rate reported before any efficiency figure.
- [x] Paired per-task deltas for quota, tokens, tool calls and wall-clock.
- [x] A statement of what the result does **not** support.
- [x] A routing recommendation, or an explicit finding that there is none.
