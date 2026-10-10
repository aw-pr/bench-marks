#!/usr/bin/env bash
# run-codex.sh — the BENCH-007 GPT row, run natively in Codex.
#
# Isolation is the point. The workspace is an empty directory outside this
# repo, holding nothing but the brief, so the model cannot see the Opus or
# Fable rows sitting next to this script. Only the brief goes in as the prompt,
# unmodified, as PENDING.md requires.
#
# Scoring is deliberately not done here: the rubric needs judgement, and the
# scorer re-runs the test suite independently, as was done for the Fable row.
#
# Usage: run-codex.sh            (writes output.md, lfu_cache.py, run-meta.json)

set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ab="$here/../../../ab"
brief="$here/../brief.md"
[[ -f "$here/output.md" ]] && { echo "output.md already exists; refusing to overwrite a recorded row" >&2; exit 0; }

ws="$(mktemp -d "${TMPDIR:-/tmp}/bench007-gpt.XXXXXX")"
events="$here/transcript.jsonl"
effort="${BENCH007_EFFORT:-high}"

run_model() {
  local model="$1"
  quota_before="$("$ab/bin/codex-limits.sh" 2>/dev/null || echo '{}')"
  t0=$(date +%s)
  timeout 1800 codex exec --json --sandbox workspace-write --skip-git-repo-check \
    -C "$ws" -m "$model" -c "model_reasoning_effort=$effort" "$(cat "$brief")" \
    < /dev/null > "$events" 2>"$ws/.stderr"
  rc=$?
  wall=$(( $(date +%s) - t0 ))
  jq -e 'select(.type=="turn.completed")' "$events" >/dev/null 2>&1
}

model="gpt-5.5"; substituted=""
if ! run_model "$model"; then
  # The brief names GPT-5.5. If it is no longer served, the frontier Codex tier
  # stands in, and the substitution is recorded rather than hidden.
  substituted="$model not served ($(head -c 200 "$ws/.stderr" | tr '\n' ' '))"
  model="gpt-5.6-sol"
  run_model "$model" || { echo "both models failed; see $events" >&2; exit 1; }
fi

jq -r 'select(.type=="item.completed" and .item.type=="agent_message") | .item.text' "$events" > "$ws/.final"
{
  echo "# BENCH-007 solution: GPT row"
  echo
  echo "> Raw final message from \`codex exec\`, model \`$model\`, effort \`$effort\`,"
  echo "> isolated workspace containing only the brief. Unedited."
  echo
  cat "$ws/.final"
} > "$here/output.md"
[[ -f "$ws/lfu_cache.py" ]] && cp "$ws/lfu_cache.py" "$here/lfu_cache.py"

tests_rc=null; tests_tail=""
if [[ -f "$here/lfu_cache.py" ]]; then
  tests_tail="$(cd "$ws" && timeout 120 python3 lfu_cache.py 2>&1 | tail -20)"; tests_rc=$?
fi

thread="$(jq -r 'select(.type=="thread.started") | .thread_id' "$events" | head -1)"
rollout="$(find "${CODEX_HOME:-$HOME/.codex}/sessions" -name "rollout-*${thread:-none}.jsonl" | head -1)"
quota_after="$([[ -n "$rollout" ]] && "$ab/bin/codex-limits.sh" "$rollout" || echo '{}')"

jq -n --arg model "$model" --arg effort "$effort" --arg sub "$substituted" \
  --arg date "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --argjson wall "$wall" --argjson rc "$rc" \
  --argjson b "$quota_before" --argjson a "$quota_after" \
  --argjson tests_rc "$tests_rc" --arg tests_tail "$tests_tail" \
  --argjson files "$(ls -1 "$ws" | jq -R . | jq -s .)" \
  --argjson usage "$(jq -cs '[.[] | select(.type=="turn.completed") | .usage] | .[-1] // {}' "$events")" \
  --argjson commands "$(jq -s '[.[] | select(.type=="item.completed" and .item.type=="command_execution")] | length' "$events")" \
  '{model:$model, reasoning_effort:$effort, substituted_for:(if $sub=="" then null else $sub end),
    run_at:$date, wall_seconds:$wall, exit_code:$rc, commands_run:$commands, usage:$usage,
    files_written:$files, self_test_exit:$tests_rc, self_test_tail:$tests_tail,
    quota_pct_used:(($a.primary_pct // 0) - ($b.primary_pct // 0)),
    credits_spent:(($b.credits // 0) - ($a.credits // 0))}' > "$here/run-meta.json"

rm -rf "$ws"
echo "BENCH-007 GPT row recorded: model=$model wall=${wall}s self_test_exit=$tests_rc"
