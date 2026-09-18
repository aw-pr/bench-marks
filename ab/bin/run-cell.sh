#!/usr/bin/env bash
# run-cell.sh — one cell of the A/B grid: one task, one arm, one repeat.
#
# Writes a single JSON record to ab/runs/<lever>.jsonl. Every number in that
# record comes from the CLI's own accounting, never from the model's
# self-report, because a model asked how many tokens it used will guess.
#
# The two arms differ by exactly one thing: the args this script builds for the
# named lever. Everything else -- prompt, model, cwd, tool allowlist -- is held
# identical, and the record carries the full argv so that claim is auditable
# rather than asserted.
#
# Usage: run-cell.sh <task.yaml> <lever> <control|treatment> <repeat-n>

set -uo pipefail

task_file="${1:-}"; lever="${2:-}"; arm="${3:-}"; repeat="${4:-1}"
[[ -n "$task_file" && -n "$lever" && -n "$arm" ]] || {
  echo "usage: $(basename "$0") <task.yaml> <lever> <control|treatment> <repeat-n>" >&2; exit 64; }
[[ -f "$task_file" ]] || { echo "no such task file: $task_file" >&2; exit 66; }

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
runs_dir="$here/runs"; mkdir -p "$runs_dir"

for t in yq jq claude; do command -v "$t" >/dev/null || { echo "missing dependency: $t" >&2; exit 69; }; done

task_id="$(yq -r '.id' "$task_file")"
repo_key="$(yq -r '.repo_key' "$task_file")"
# Task files name a repo key, never a path, so the corpus is machine-independent.
# shellcheck disable=SC1090
[[ -f "$here/repos.local.sh" ]] || { echo "missing $here/repos.local.sh -- copy repos.local.sh.example and set your paths" >&2; exit 78; }
source "$here/repos.local.sh"
eval "repo=\${BENCH_REPO_${repo_key}:-}"
[[ -n "$repo" ]] || { echo "no path mapped for repo_key '$repo_key' in repos.local.sh" >&2; exit 78; }
prompt="$(yq -r '.prompt' "$task_file")"
model="$(yq -r '.model // "claude-opus-5"' "$task_file")"
allowed="$(yq -r '.allowed_tools // "Read,Grep,Glob,Bash"' "$task_file")"
# --allowedTools only auto-approves; it does not restrict. Anything the arms
# must NOT reach has to be denied explicitly, or the control arm quietly gets
# the treatment's capability back. Observed on the first smoke run: a task
# given --allowedTools "Read,Grep,Glob" still used Bash 7 times and spawned a
# sub-agent.
disallowed="$(yq -r '.disallowed_tools // ""' "$task_file")"

[[ -d "$repo" ]] || { echo "task repo does not exist: $repo" >&2; exit 66; }

# --- arm construction: the ONLY thing that may differ between arms ----------
extra_args=(); append_prompt=""
case "$lever:$arm" in
  codegraph:control)      extra_args+=(--strict-mcp-config)
                          disallowed="${disallowed:+$disallowed,}mcp__codegraph" ;;
  codegraph:treatment)    extra_args+=(--strict-mcp-config --mcp-config "$repo/.mcp.json") ;;
  ast_grep:control)       disallowed="${disallowed:+$disallowed,}Bash(ast-grep:*),Bash(sg:*)" ;;
  ast_grep:treatment)     append_prompt="ast-grep is installed and on PATH. It is a structural code search over tree-sitter: \`ast-grep run -l <lang> -p '<pattern>'\` where \$NAME matches one node and \$\$\$ARGS matches many. Prefer it over textual grep when the question is about code structure -- calls, definitions, types -- rather than text." ;;
  repo_priming:control)   : ;;
  repo_priming:treatment) append_prompt="$(yq -r '.priming // ""' "$task_file")" ;;
  subagent_hygiene:control)
      append_prompt="When you delegate to a sub-agent, have it return the file contents it read." ;;
  subagent_hygiene:treatment)
      append_prompt="When you delegate to a sub-agent, have it return only its conclusion, never the file contents it read." ;;
  model_tier:control)     model="$(yq -r '.tier_control // "claude-opus-5"' "$task_file")" ;;
  model_tier:treatment)   model="$(yq -r '.tier_treatment // "claude-sonnet-5"' "$task_file")" ;;
  model_tier_haiku:control)
      model="$(yq -r '.haiku_control // "claude-sonnet-5"' "$task_file")" ;;
  model_tier_haiku:treatment)
      model="$(yq -r '.haiku_treatment // "claude-haiku-4-5-20251001"' "$task_file")" ;;
  prompt_cache:*)         : ;;
  *) echo "unknown lever:arm combination: $lever:$arm" >&2; exit 64 ;;
esac
[[ -n "$append_prompt" ]] && extra_args+=(--append-system-prompt "$append_prompt")
[[ -n "$disallowed" ]] && extra_args+=(--disallowedTools "$disallowed")

stream="$(mktemp)"; trap 'rm -f "$stream" "$stream.err"' EXIT
started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

( cd "$repo" && timeout 900 claude -p "$prompt" \
    --output-format stream-json --verbose \
    --model "$model" --allowedTools "$allowed" \
    ${extra_args[@]+"${extra_args[@]}"} < /dev/null ) > "$stream" 2>"$stream.err"
rc=$?

# --- metrics: all from the CLI's own events --------------------------------
result_text="$(jq -r 'select(.type=="result") | .result // ""' "$stream" 2>/dev/null | head -c 200000)"
tool_calls="$(jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") | .name' "$stream" 2>/dev/null | wc -l | tr -d ' ')"
tools_used="$(jq -rs '[.[] | select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") | .name] | group_by(.) | map({(.[0]): length}) | add // {}' "$stream" 2>/dev/null)"
[[ -z "$tools_used" ]] && tools_used='{}'

# The tools histogram records tool NAMES, so a lever whose treatment is "this
# binary is on PATH" looks identical in both arms: every call is just "Bash".
# Capture the leading word of each Bash command as well, so the record can
# prove the treatment arm actually reached for the thing being tested rather
# than quietly behaving like its own control.
bash_cmds="$(jq -rs '[.[] | select(.type=="assistant") | .message.content[]? | select(.type=="tool_use" and .name=="Bash") | .input.command // "" | split(" ")[0] | split("/") | .[-1]] | group_by(.) | map({(.[0]): length}) | add // {}' "$stream" 2>/dev/null)"
[[ -z "$bash_cmds" ]] && bash_cmds='{}'

res_json="$(jq -c 'select(.type=="result") | {num_turns, duration_ms, duration_api_ms, ttft_ms, total_cost_usd, is_error, usage, subagent_stats}' "$stream" 2>/dev/null | head -1)"
if [[ -z "$res_json" ]]; then
  # No result event: the CLI died before finishing. Record the run as a
  # failure with whatever the stderr said, rather than dropping it -- a
  # silently missing row would bias the arm it belonged to.
  res_json='{"num_turns":null,"duration_ms":null,"duration_api_ms":null,"ttft_ms":null,"total_cost_usd":null,"is_error":true,"usage":{}}'
  printf 'warning: no result event for %s/%s rep%s; stderr: %s\n' "$lever" "$arm" "$repeat" "$(head -c 300 "$stream.err" 2>/dev/null)" >&2
fi

# --- the gate: answer key --------------------------------------------------
# Crude by design: substring presence over the final answer. It cannot judge
# prose quality, and is not asked to -- quality is rubric.md's job. What it can
# do is refuse to let a wrong-but-cheap run count as a win for its lever.
missing="$(yq -r '.answer_key.must_mention[]' "$task_file" 2>/dev/null | while IFS= read -r term; do
  [[ -z "$term" ]] && continue
  grep -qiF -- "$term" <<<"$result_text" || printf '%s\n' "$term"
done | jq -Rsc 'split("\n") | map(select(length>0))')"
passed=$([[ "$missing" == "[]" && $rc -eq 0 ]] && echo true || echo false)

jq -nc \
  --arg task "$task_id" --arg lever "$lever" --arg arm "$arm" --argjson repeat "$repeat" \
  --arg model "$model" --arg started "$started" --argjson rc "$rc" \
  --argjson passed "$passed" --argjson missing "$missing" \
  --argjson tool_calls "${tool_calls:-0}" --argjson tools "$tools_used" \
  --argjson bash_cmds "$bash_cmds" \
  --argjson res "$res_json" \
  --arg argv "model=$model allowed=$allowed disallowed=${disallowed:-none} extra=${extra_args[*]:-none}" \
  '{task:$task, lever:$lever, arm:$arm, repeat:$repeat, model:$model,
    started_at:$started, exit_code:$rc, passed:$passed, missing_terms:$missing,
    tool_calls:$tool_calls, tools:$tools, bash_cmds:$bash_cmds, argv:$argv,
    num_turns:$res.num_turns, duration_ms:$res.duration_ms,
    duration_api_ms:$res.duration_api_ms, ttft_ms:$res.ttft_ms,
    total_cost_usd:$res.total_cost_usd, is_error:$res.is_error,
    input_tokens:$res.usage.input_tokens,
    output_tokens:$res.usage.output_tokens,
    cache_read_input_tokens:$res.usage.cache_read_input_tokens,
    cache_creation_input_tokens:$res.usage.cache_creation_input_tokens,
    subagent_stats:$res.subagent_stats}' \
  >> "$runs_dir/${lever}.jsonl"

printf '%s %s/%s rep%s  passed=%s  tool_calls=%s  cost=%s\n' \
  "$task_id" "$lever" "$arm" "$repeat" "$passed" "$tool_calls" \
  "$(jq -r 'select(.type=="result") | .total_cost_usd' "$stream" 2>/dev/null | head -1)"
