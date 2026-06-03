# Finding — BENCH-006: codegraph MCP vs grep/Read

Condensed result. Full experiment log:
`fractals-from-the-90s/docs/metrics/codegraph-ab-benchmark.md`.

## Scoreboard

| Experiment | Tool calls (codegraph / baseline) | Correctness | Friction winner | Index accuracy |
|---|---|---|---|---|
| 1. Comprehension trace | 2 / 5 | tie (both correct; codegraph more complete) | **codegraph** | n/a |
| 2. Index accuracy audit | n/a | n/a | n/a | **high, one real miss** |
| 3. Implement (orientation) | 1 / 1 | tie | tie (grep edge) | ghost-symbol gotcha |
| 4. Capability sweep | all 7 tools work | n/a | n/a | n/a |

## What each arm did well

- **codegraph wins cold comprehension / "what depends on X".** Exp 1: the
  reference-orbit → perturbation trace took **2 calls vs 5**, fewer
  round-trips, and it volunteered callers, covering tests, and the Swift
  parity mirror *for free*. Higher token volume per call (returns whole
  files), but fewer trips.
- **baseline (grep/Read) wins token frugality and failure honesty.** It
  pulls only the exact ranges you choose, and when it is wrong it is
  *loud* (an empty grep is obvious); codegraph can be silently-confident
  on a bad edge.
- **Known-symbol edit is a wash** (Exp 3): the `Edit` action is
  tool-identical, so it reduces to orientation cost, ~1 call either way.

## Index accuracy (Exp 2, vs grep ground truth)

- `callers` edges: **100%** precision + recall on two probed symbols.
- `impact`: **complete**, including cross-package transitive reach; mild
  file-node noise.
- `callees`: caught all intra-project function calls but **conflates
  "calls" with "type-uses"** and **missed one value-receiver method call**
  (`sc.Validate()` where three same-named `Validate` methods exist).
- Display quirk: `explore`'s blast-radius summary line mislabeled caller
  file distribution; the dedicated `callers` tool was correct. Trust the
  specialised tool over the summary line.

## Gotcha

Creating a git worktree under `.claude/worktrees/` made codegraph index
it and emit **transient duplicate/ghost symbols**; removing the worktree
self-healed the index. Codegraph should ignore that path.

## Recommendation

**Keep codegraph.** Use it **first** for comprehension, tracing, and
pre-refactor impact — that is where it clearly beats grep/Read. Fall back
to grep/Read for surgical confirmation and known-symbol edits, trust the
specialised `callers`/`callees`/`impact` tools over the `explore` summary
line, treat `callees` as "uses" not strict "calls", and verify any
suspect edge with grep before acting on it.

This finding is encoded as a reusable, all-families skill:
`mcp-hub/skills/codegraph-first`.
