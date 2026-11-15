#!/usr/bin/env bash
# BENCH-001 runner. Runs the remaining tools against brief.md in isolation.
# Codex already run manually (GPT-5.5 x-high, 2m29s). This script does the rest.
#
# Each tool: fresh temp cwd, brief.md as the SOLE prompt, no extra steering,
# stdout captured verbatim to tasks/BENCH-001/<tool>/post.md, wall-clock timed.

set -u

TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRIEF="$TASK_DIR/brief.md"

# High-reasoning model tiers. Edit if your account exposes a higher one.
CLAUDE_MODEL="opus"
GEMINI_MODEL="gemini-2.5-pro"
# cursor-agent: account default (--list-models returned none); leave unset.

run_tool() {
  local name="$1"; shift
  local outdir="$TASK_DIR/$name"
  mkdir -p "$outdir"
  local workdir; workdir="$(mktemp -d)"
  echo ">>> $name : starting in $workdir"
  local start end secs
  start=$(date +%s)
  ( cd "$workdir" && timeout 600 "$@" ) > "$outdir/post.md" 2> "$outdir/stderr.log"
  local rc=$?
  end=$(date +%s)
  secs=$((end - start))
  local words; words=$(wc -w < "$outdir/post.md" | tr -d ' ')
  echo ">>> $name : rc=$rc  ${secs}s  ${words} words  -> $outdir/post.md"
  echo "| $name | ${secs}s (script) | 1 (scripted, single pass) | rc=$rc, ${words} words, model as configured |" >> "$TASK_DIR/run-log-scripted.md"
  rm -rf "$workdir"
}

echo "tool | wall | cycles | notes" > "$TASK_DIR/run-log-scripted.md"

# Claude: -p reads prompt from stdin. Opus 4.7, thinking applied automatically.
run_tool claude bash -c "claude -p --model '$CLAUDE_MODEL' --permission-mode default --no-session-persistence < '$BRIEF'"

# Gemini: pass brief as the prompt; default approval (read-only for a writing task).
run_tool gemini bash -c "GEMINI_CLI_TRUST_WORKSPACE=true gemini -m '$GEMINI_MODEL' --approval-mode default --skip-trust -p \"\$(cat '$BRIEF')\""

# Cursor dropped from BENCH-001: it exposes only frontier coding models, not
# meaningful for a writing brief.

echo "ALL DONE. See $TASK_DIR/run-log-scripted.md and each <tool>/post.md"
