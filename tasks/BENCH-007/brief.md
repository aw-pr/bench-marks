# Task Brief — BENCH-007

> A **model-variant meta-bench**, not a four-tool comparison. The same
> brief below is run by four **frontier peer models** — Fable, Opus,
> GPT-5.5, Gemini-Pro — each in its own native harness, on an isolated
> copy of the task. This is explicitly not a Claude/Codex/Cursor/Gemini
> subscription bench; Sonnet and Haiku are not subjects here either. See
> `MODELS.md` for the Fable working-hypothesis entry this task is
> designed to test.

---

## Metadata

| Field | Value |
|-------|-------|
| Task ID | BENCH-007 |
| Date | 2026-07-04 |
| Source repo | standalone |
| Source issue / PR | n/a — frontier-tier model comparison, commissioned directly |
| Rows | Fable, Opus, GPT-5.5, Gemini-Pro — same brief, isolated runs, no cross-model visibility |

---

## Spec

Implement an **O(1)-amortised LFU (Least Frequently Used) cache** in
Python 3.11+, as a single self-contained module with no third-party
dependencies.

Requirements:

1. A class `LFUCache(capacity: int)` supporting:
   - `get(key) -> value | None` — returns the value if present, else
     `None`. On a hit, increments the key's use-frequency and marks it
     most-recently-used *within* its frequency bucket.
   - `put(key, value) -> None` — inserts or updates. If the cache is at
     capacity and a new key is inserted, evict the least-frequently-used
     key; if there is a tie in frequency, evict the least-recently-used
     among the tied keys.
   - Both operations must run in **O(1) amortised time**, not O(log n)
     or O(n). A heap-based or naive-scan implementation does not satisfy
     this requirement — the brief specifically excludes those approaches.
2. `capacity == 0` is a valid construction; `get`/`put` on it are no-ops
   that never store anything (and `get` always returns `None`).
3. Updating the value of an existing key via `put` counts as a use (bumps
   its frequency), but does not count as a second insertion against
   capacity.
4. Include a short written proof/argument (in the solution's comments or
   an accompanying paragraph) for *why* the design achieves O(1)
   amortised `get`/`put` — not just an assertion that it does.
5. Include a test suite (can be `unittest`, `pytest`, or plain assert
   statements in a `if __name__ == "__main__":` block) that exercises:
   - basic get/put and eviction-on-capacity behaviour,
   - the frequency-tie-break-by-recency rule,
   - the `capacity == 0` edge case,
   - a "value update doesn't double-count as insertion" case.

## Constraints

- No external packages (no `cachetools`, no `sortedcontainers`, no
  `collections.OrderedDict`-as-a-crutch-for-frequency — `OrderedDict` is
  fine for LRU *within* a frequency bucket, but the frequency ordering
  itself must not depend on scanning or sorting).
- Single file, runnable as-is (`python3 lfu_cache.py`) with the test
  suite executing when run directly.
- Do not use any timing/benchmark harness to "prove" O(1) — the proof
  must be structural (data-structure argument), not empirical timing.

## Definition of done

- [ ] `LFUCache` class implemented, matching the interface above.
- [ ] Get/put are structurally O(1) amortised (doubly-linked frequency
      buckets, or equivalent — not a heap, not a sorted structure, not a
      linear scan for the min-frequency key).
- [ ] `capacity == 0` handled without raising and without ever caching.
- [ ] Tie-break-by-recency-within-frequency is implemented and tested.
- [ ] Value-update-is-not-a-new-insertion is implemented and tested.
- [ ] A structural O(1) argument is present in prose or comments.
- [ ] Test suite runs to completion with no failures when the file is
      executed directly.

## Context paste

None — this is a standalone algorithmic kernel task; no external repo
context is required. The brief above is fully self-contained and
identical across all four rows.

## Notes for the scorer

Rubric mapping is the standard six dimensions, scored per model row
(Fable / Opus / GPT-5.5 / Gemini-Pro), same as a normal four-subscription
bench — the only change from the usual bench-marks row labels is that
the rows are **model identities**, not tool/subscription handles. The
known trap in this brief is the O(1) requirement: a plausible-looking
but actually-O(n) or O(log n) "LFU cache" (e.g. re-sorting a list, or a
heap with lazy deletion presented as O(1)) is the most likely
silent-wrong failure mode to watch for when scoring Correctness and
Failure mode.
