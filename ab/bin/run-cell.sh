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

# Levers named codex_* run the same task through Codex instead of Claude; the
# task, cwd, gate and record shape are shared so the two backends stay
# comparable field for field.
backend=claude; [[ "$lever" == codex_* ]] && backend=codex
for t in yq jq "$backend"; do command -v "$t" >/dev/null || { echo "missing dependency: $t" >&2; exit 69; }; done

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

# A task may restrict itself to named levers. T3/T4 allow Agent so the
# sub-agent lever can actually delegate, which makes their tool_calls
# incomparable with every other lever's -- a sub-agent's calls never reach the
# parent stream. Refuse rather than warn: silently counting a delegated run
# against a non-delegated baseline is the exact failure the gate exists to stop.
task_levers="$(yq -r '.levers // [] | join(" ")' "$task_file")"
if [[ -n "$task_levers" ]] && [[ " $task_levers " != *" $lever "* ]]; then
  echo "run-cell: task $task_id is restricted to levers [$task_levers]; refusing to run it for '$lever'" >&2
  exit 65
fi

[[ -d "$repo" ]] || { echo "task repo does not exist: $repo" >&2; exit 66; }

# --- arm construction: the ONLY thing that may differ between arms ----------
extra_args=(); env_args=(); append_prompt=""
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
  codex_tier:control)     model="$(yq -r '.codex_tier_control // "gpt-5.6-terra"' "$task_file")"; effort=medium ;;
  codex_tier:treatment)   model="$(yq -r '.codex_tier_treatment // "gpt-5.6-luna"' "$task_file")"; effort=medium ;;
  codex_effort:control)   model="$(yq -r '.codex_effort_model // "gpt-5.6-terra"' "$task_file")"; effort=high ;;
  codex_effort:treatment) model="$(yq -r '.codex_effort_model // "gpt-5.6-terra"' "$task_file")"; effort=medium ;;
  # Context hygiene. Control is the operator's MCP setup exactly as a headless
  # run loads it, with tool search at its default; ENABLE_TOOL_SEARCH is unset
  # rather than inherited so a stray shell export cannot change the regime.
  mcp_prune:control|tool_deferral:control)
      model="$(yq -r '.hygiene_model // "claude-sonnet-5-5"' "$task_file")"; env_args=(-u ENABLE_TOOL_SEARCH) ;;
  mcp_prune:treatment)
      model="$(yq -r '.hygiene_model // "claude-sonnet-5-5"' "$task_file")"; env_args=(-u ENABLE_TOOL_SEARCH)
      extra_args+=(--strict-mcp-config) ;;
  tool_deferral:treatment)
      model="$(yq -r '.hygiene_model // "claude-sonnet-5-5"' "$task_file")"; env_args=(ENABLE_TOOL_SEARCH=false) ;;
  *) echo "unknown lever:arm combination: $lever:$arm" >&2; exit 64 ;;
esac
[[ -n "$append_prompt" ]] && extra_args+=(--append-system-prompt "$append_prompt")
[[ -n "$disallowed" ]] && extra_args+=(--disallowedTools "$disallowed")

stream="$(mktemp)"; trap 'rm -f "$stream" "$stream.err"' EXIT
started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

codex_extra='{}'; claude_extra='{}'
if [[ "$backend" == codex ]]; then
  # Codex has no tool allowlist; read-only sandbox is its equivalent of the
  # Claude tasks' Read/Grep/Glob/Bash, and the deny list has nothing to bind to.
  allowed="codex:read-only"; disallowed=""; extra_args=(-c "model_reasoning_effort=$effort")
  quota_before="$("$here/bin/codex-limits.sh" 2>/dev/null || echo '{}')"
  t0=$(date +%s)
  timeout 900 codex exec --json --sandbox read-only --skip-git-repo-check \
    -C "$repo" -m "$model" "${extra_args[@]}" "$prompt" < /dev/null > "$stream" 2>"$stream.err"
  rc=$?
  wall_ms=$(( ($(date +%s) - t0) * 1000 ))

  result_text="$(jq -r 'select(.type=="item.completed" and .item.type=="agent_message") | .item.text // ""' "$stream" 2>/dev/null | tail -c 200000)"
  tool_calls="$(jq -r 'select(.type=="item.completed" and .item.type=="command_execution") | 1' "$stream" 2>/dev/null | wc -l | tr -d ' ')"
  tools_used="$(jq -nc --argjson n "${tool_calls:-0}" 'if $n > 0 then {shell: $n} else {} end')"
  # Commands arrive wrapped as `/bin/zsh -lc "<cmd>"`; record the inner verb.
  bash_cmds="$(jq -rs '[.[] | select(.type=="item.completed" and .item.type=="command_execution") | .item.command // "" | sub("^\\S+ -lc "; "") | ltrimstr("\"") | ltrimstr("'"'"'") | split(" ")[0] | split("/") | .[-1]] | group_by(.) | map({(.[0]): length}) | add // {}' "$stream" 2>/dev/null)"
  [[ -z "$bash_cmds" ]] && bash_cmds='{}'

  usage="$(jq -cs '[.[] | select(.type=="turn.completed") | .usage] | {
      input_tokens: (map(.input_tokens // 0) | add),
      output_tokens: (map(.output_tokens // 0) | add),
      cache_read_input_tokens: (map(.cached_input_tokens // 0) | add),
      cache_creation_input_tokens: (map(.cache_write_input_tokens // 0) | add),
      reasoning_output_tokens: (map(.reasoning_output_tokens // 0) | add),
      turns: length}' "$stream" 2>/dev/null)"
  is_error=$([[ $rc -eq 0 ]] && jq -e 'select(.type=="turn.completed")' "$stream" >/dev/null 2>&1 && echo false || echo true)
  res_json="$(jq -nc --argjson u "${usage:-null}" --argjson wall "$wall_ms" --argjson err "$is_error" \
    '{num_turns: $u.turns, duration_ms: $wall, duration_api_ms: null, ttft_ms: null,
      total_cost_usd: null, is_error: $err, usage: ($u // {}), subagent_stats: null}')"

  # Quota is read from this run's own rollout, found by its thread id, so a
  # concurrent Codex session cannot be mistaken for this cell's snapshot.
  thread="$(jq -r 'select(.type=="thread.started") | .thread_id' "$stream" 2>/dev/null | head -1)"
  rollout="$(find "${CODEX_HOME:-$HOME/.codex}/sessions" -name "rollout-*${thread:-none}.jsonl" 2>/dev/null | head -1)"
  quota_after="$([[ -n "$rollout" ]] && "$here/bin/codex-limits.sh" "$rollout" 2>/dev/null || echo '{}')"
  codex_extra="$(jq -nc --argjson b "$quota_before" --argjson a "$quota_after" --argjson u "${usage:-null}" --arg effort "$effort" --arg thread "$thread" '
    {backend: "codex", reasoning_effort: $effort, thread_id: $thread,
     reasoning_output_tokens: $u.reasoning_output_tokens,
     primary_pct_before: $b.primary_pct, primary_pct_after: $a.primary_pct,
     quota_pct_used: (if ($a.primary_pct != null and $b.primary_pct != null) then ($a.primary_pct - $b.primary_pct) else null end),
     credits_spent: (if ($a.credits != null and $b.credits != null) then ($b.credits - $a.credits) else null end)}')"
else

( cd "$repo" && env ${env_args[@]+"${env_args[@]}"} timeout 900 claude -p "$prompt" \
    --output-format stream-json --verbose \
    --model "$model" --allowedTools "$allowed" \
    ${extra_args[@]+"${extra_args[@]}"} < /dev/null ) > "$stream" 2>"$stream.err"
rc=$?

# What the session actually loaded, read from its own init event, and the size
# of the first turn's prompt. A context lever moves the fixed prefix every turn
# pays for; recording it lets the record prove the treatment arm differed,
# rather than the arms quietly loading the same tool set.
claude_extra="$(jq -c 'select(.type=="system" and .subtype=="init") | {
    mcp_servers_connected: ([.mcp_servers[]? | select(.status=="connected")] | length),
    mcp_tools: ([.tools[]? | select(startswith("mcp__"))] | length),
    tool_search: ((.tools // []) | index("ToolSearch") != null)}' "$stream" 2>/dev/null | head -1)"
prefix_tokens="$(jq -s '[.[] | select(.type=="assistant") | .message.usage] | first
    | if . then (.input_tokens // 0) + (.cache_creation_input_tokens // 0) + (.cache_read_input_tokens // 0) else null end' "$stream" 2>/dev/null)"
claude_extra="$(jq -nc --argjson i "${claude_extra:-null}" --argjson p "${prefix_tokens:-null}" '($i // {}) + {prefix_tokens: $p}')"

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
  --argjson res "$res_json" --argjson codex "$codex_extra" --argjson claude_extra "$claude_extra" \
  --arg argv "model=$model allowed=$allowed disallowed=${disallowed:-none} extra=${extra_args[*]:-none}${env_args[*]:+ env=${env_args[*]}}" \
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
    subagent_stats:$res.subagent_stats} + $codex + $claude_extra' \
  >> "$runs_dir/${lever}.jsonl"

printf '%s %s/%s rep%s  passed=%s  tool_calls=%s  cost=%s\n' \
  "$task_id" "$lever" "$arm" "$repeat" "$passed" "$tool_calls" \
  "$([[ "$backend" == codex ]] && jq -r '"quota+" + (.quota_pct_used|tostring) + "%"' <<<"$codex_extra" || jq -r 'select(.type=="result") | .total_cost_usd' "$stream" 2>/dev/null | head -1)"
