#!/usr/bin/env bash
# run-grid.sh — run every cell of one lever's grid in randomised order.
#
# Order is randomised rather than looped arm-by-arm so that anything which
# drifts over the run -- cache warmth, provider load, rate limiting -- lands on
# both arms evenly instead of systematically favouring whichever went second.
#
# Usage: run-grid.sh <lever> <repeats> [task.yaml ...]

set -uo pipefail
lever="${1:?usage: run-grid.sh <lever> <repeats> [task...]}"
repeats="${2:?}"; shift 2
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tasks=("$@"); [[ ${#tasks[@]} -gt 0 ]] || tasks=("$here"/tasks/*.yaml)

"$here/bin/preflight.sh" "$lever" || { echo "grid refused: preflight failed for $lever" >&2; exit 1; }

plan="$(mktemp)"; trap 'rm -f "$plan"' EXIT
for t in "${tasks[@]}"; do
  for arm in control treatment; do
    for ((n = 1; n <= repeats; n++)); do printf '%s\t%s\t%s\n' "$t" "$arm" "$n"; done
  done
done > "$plan"

total=$(wc -l < "$plan" | tr -d ' ')
printf '== grid: lever=%s cells=%s (randomised order)\n' "$lever" "$total"

i=0
while IFS=$'\t' read -r t arm n; do
  i=$((i + 1))
  printf '[%s/%s] ' "$i" "$total"
  # stdin is redirected because run-cell.sh invokes `claude -p`, which reads
  # stdin and would otherwise consume the rest of this loop's plan -- the loop
  # then exits after one cell and reports itself complete.
  "$here/bin/run-cell.sh" "$t" "$lever" "$arm" "$n" < /dev/null || printf '  (cell failed, recorded)\n'
done < <(sort -R "$plan")

printf '== grid complete: %s\n' "$here/runs/${lever}.jsonl"
