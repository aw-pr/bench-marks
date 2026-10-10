#!/usr/bin/env bash
# run-adjudicator.sh — submit each blinded summary to Claude for scoring.
#
# Prerequisites:
#   - ANTHROPIC_API_KEY set in env (or use run-secure-command.sh from research-sweeper)
#   - pip install anthropic
#   - fixtures/summary-A.md, summary-B.md, summary-C.md populated
#   - tasks/BENCH-002/rubric.md and tasks/BENCH-002/brief.md present
#
# Output: results/verdicts-raw.json

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCH_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
FIXTURES_DIR="$BENCH_DIR/fixtures"
RESULTS_DIR="$BENCH_DIR/results"
RUBRIC="$BENCH_DIR/rubric.md"
BRIEF="$BENCH_DIR/brief.md"
OUT="$RESULTS_DIR/verdicts-raw.json"

mkdir -p "$RESULTS_DIR"

# Verify prerequisites
for label in A B C; do
    if [[ ! -f "$FIXTURES_DIR/summary-$label.md" ]]; then
        echo "Error: $FIXTURES_DIR/summary-$label.md not found. Run scrub.py first." >&2
        exit 1
    fi
done

if [[ ! -f "$RUBRIC" ]]; then
    echo "Error: rubric.md not found at $RUBRIC" >&2
    exit 1
fi

if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    echo "Error: ANTHROPIC_API_KEY is not set." >&2
    exit 1
fi

echo "Running adjudicator on labels A, B, C..."
echo "Output will be written to: $OUT"

python3 - <<PYEOF
import json
import os
import sys
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
    sys.exit(1)

BENCH_DIR = Path("$BENCH_DIR")
FIXTURES_DIR = Path("$FIXTURES_DIR")
RESULTS_DIR = Path("$RESULTS_DIR")
RUBRIC_PATH = Path("$RUBRIC")
BRIEF_PATH = Path("$BRIEF")
OUT_PATH = Path("$OUT")

rubric = RUBRIC_PATH.read_text(encoding="utf-8")
brief = BRIEF_PATH.read_text(encoding="utf-8")

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a blind adjudicator scoring research summaries on a fixed rubric.

You will be given:
1. The original research brief (what the sweep was asked to produce)
2. A scoring rubric with five dimensions, each scored 1-5
3. One blinded summary to score (the provider is unknown to you)

Score each dimension independently using the anchors provided. Do not compare this summary
to others you may score in the same session — score only against the rubric anchors.

Return ONLY a single JSON object matching the schema defined at the end of the rubric.
No preamble, no postscript, no markdown fences. The JSON must be parseable by json.loads.
"""

verdicts = []

for label in ["A", "B", "C"]:
    summary_path = FIXTURES_DIR / f"summary-{label}.md"
    summary = summary_path.read_text(encoding="utf-8")

    user_message = f"""## Research Brief

{brief}

---

## Scoring Rubric

{rubric}

---

## Summary to Score (Label: {label})

{summary}

---

Score Summary {label} on all five dimensions. Return the JSON object only."""

    print(f"  Scoring label {label}...", flush=True)

    response = client.messages.create(
        model="claude-opus-4-7-20261101",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_text = response.content[0].text if response.content else ""

    # Strip any accidental fences
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        verdict = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"  Warning: could not parse JSON for label {label}: {e}", file=sys.stderr)
        verdict = {"label": label, "parse_error": str(e), "raw": raw_text}

    verdicts.append(verdict)
    print(f"  Label {label}: total={verdict.get('total', '?')}")

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUT_PATH.write_text(json.dumps(verdicts, indent=2), encoding="utf-8")
print(f"\nVerdicts written to: {OUT_PATH}")
PYEOF

echo "Done."
