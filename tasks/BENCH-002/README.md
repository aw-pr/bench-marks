# BENCH-002 — Blind Adjudicator: Research Sweep Quality

## Status

Parked 2026-10-10. Only fixture A (the scrubbed Gemini sweep) exists; fixtures B
and C are placeholders because the OpenAI and Claude deep sweeps were never run.
Scrub tooling and `tests/test_scrub.py` pass (26 tests). To unpark: run the
OpenAI and Claude deep sweeps on `brief.md`, scrub each with `scripts/scrub.py`
(replacing the placeholders), then run `scripts/run-adjudicator.sh` and
`scripts/collate-results.py`. Before unparking, re-check fixture A: the scrubber
left a stray "Google's" in the model-release sentence, which could hint at a
provider. No ledger row, as nothing has been scored.


A blind, rubric-driven quality comparison of three research-sweeper outputs (gemini/openai/claude)
on the same brief: AI regulation and financial services, 2023–2026.

## What this benchmark does

1. **Scrub** — strips provider name, model-identifying frontmatter, and the full sources section
   from each `summary-*.md` output. Assigns blind labels A, B, C with a private mapping kept
   in `results/label-map.json` (gitignored).

2. **Adjudicate** — feeds each blinded summary, the original brief, and a fixed rubric
   (`rubric.md` in this directory) to Claude (the adjudicator). Returns a scored JSON verdict
   per label.

3. **De-anonymise** — joins verdicts with the label map and with token/cost data from
   `research-sweeper/runs/stats.json` to produce a final results table.

## Directory layout

```
tasks/BENCH-002/
  README.md               this file
  rubric.md               scoring dimensions + anchors for the adjudicator
  brief.md                the original research brief (self-contained, no external links)
  fixtures/
    summary-A.md          scrubbed Gemini output (label assigned at scrub time)
    summary-B.md          placeholder — populate after OpenAI deep sweep
    summary-C.md          placeholder — populate after Claude deep sweep
    scrub-manifest.json   records what was stripped per fixture (for auditability)
  results/
    label-map.json        GITIGNORED — maps A/B/C back to provider + run metadata
    verdicts-raw.json     adjudicator JSON output (populated by run-adjudicator.sh)
    results-table.md      final de-anonymised table (populated by collate-results.py)
  scripts/
    scrub.py              strips provider markers; writes fixtures + label-map.json
    run-adjudicator.sh    submits each blinded summary to Claude; writes verdicts-raw.json
    collate-results.py    de-anonymises + joins with stats.json; writes results-table.md
  tests/
    test_scrub.py         unit tests for scrub.py (no provider names survive)
```

## How to run

### Prerequisites

- Python 3.10+
- `ANTHROPIC_API_KEY` set (or use `./run-secure-command.sh` from research-sweeper)
- The `anthropic` Python package: `pip install anthropic`
- Completed sweep outputs for all three providers in `fixtures/` (see "Populating fixtures")

### Step 1 — Populate fixtures

Fixtures are pre-populated from the Gemini deep batch run. Before running the adjudicator,
add the OpenAI and Claude deep sweep outputs:

```bash
# After running the OpenAI deep sweep:
python3 scripts/scrub.py \
  --input /path/to/summary-*.md \  # the summary file from the OpenAI run
  --provider openai \
  --stats /path/to/research-sweeper/runs/stats.json

# After running the Claude deep sweep:
python3 scripts/scrub.py \
  --input /path/to/summary-*.md \
  --provider claude \
  --stats /path/to/research-sweeper/runs/stats.json
```

Alternatively, run the batch scrub once all three outputs exist:

```bash
python3 scripts/scrub.py \
  --batch \
  --gemini   /path/to/ai-regulation-fs-2026-gemini-deep/summary-*.md \
  --openai   /path/to/ai-regulation-fs-2026-openai-deep/summary-*.md \
  --claude   /path/to/ai-regulation-fs-2026-claude-deep/summary-*.md \
  --stats    /path/to/research-sweeper/runs/stats.json \
  --out-dir  tasks/BENCH-002/fixtures
```

The script writes `fixtures/summary-A.md`, `summary-B.md`, `summary-C.md` and
`results/label-map.json` (gitignored). Label assignment is randomised on first run and
frozen thereafter (re-running with existing fixtures is a no-op unless `--force` is passed).

### Step 2 — Run the unit tests

```bash
python3 -m pytest tasks/BENCH-002/tests/ -v
```

All tests must pass before adjudication.

### Step 3 — Run the adjudicator

```bash
bash tasks/BENCH-002/scripts/run-adjudicator.sh
```

Requires `ANTHROPIC_API_KEY`. Writes `results/verdicts-raw.json`.

### Step 4 — Collate results

```bash
python3 tasks/BENCH-002/scripts/collate-results.py \
  --verdicts  tasks/BENCH-002/results/verdicts-raw.json \
  --label-map tasks/BENCH-002/results/label-map.json \
  --stats     /path/to/research-sweeper/runs/stats.json \
  --out       tasks/BENCH-002/results/results-table.md
```

Writes a Markdown table joining adjudicator scores with provider identity, model, lane
token counts, and estimated cost from `stats.json`.

## Blind protocol

The adjudicator (Claude) must not see provider names, model identifiers, or the sources
section during scoring. `scrub.py` removes:

- YAML frontmatter fields: `provider`, `model_lane`, `model_synthesis`, `brief_file`
- The `tags:` field (contains the provider name)
- The inline `![[sources-...]]` transclusion at the end of the summary
- Any vertexaisearch redirect URLs (Gemini-specific, would identify the provider)
- The word "Gemini", "OpenAI", "Claude", "Anthropic", "Google DeepMind" from body text,
  replacing with `[MODEL-PROVIDER]` (this is conservative — the body text may still
  reference specific models by capability; that is acceptable and expected)

The `scrub-manifest.json` records what was stripped from each fixture so any leakage
can be audited after de-anonymisation.

## Gitignore additions

Add to repo `.gitignore` (already done if you see the entry below):

```
tasks/BENCH-002/results/label-map.json
```
