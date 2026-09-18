#!/usr/bin/env bash
# preflight.sh — refuse to run a lever whose machinery is absent.
#
# This exists because an absent lever does not fail loudly. The treatment arm
# silently degrades into the control arm, both arms produce the same numbers,
# and the harness reports "no measurable difference" for a lever that never
# ran. A rollout then gets cancelled on manufactured evidence.
#
# So every check here is a refusal, never a warning. Exit 0 means the lever can
# honestly be measured; anything else means it cannot.
#
# Usage: preflight.sh <lever> [repo_root]

set -uo pipefail

lever="${1:-}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1090
[[ -f "$here/repos.local.sh" ]] && source "$here/repos.local.sh"
repo_root="${2:-${BENCH_REPO_fractals:-}}"
[[ -n "$repo_root" ]] || { echo "no repo given and BENCH_REPO_fractals unset (see ab/repos.local.sh.example)" >&2; exit 78; }

[[ -n "$lever" ]] || { echo "usage: $(basename "$0") <lever> [repo_root]" >&2; exit 64; }

fail() { printf 'REFUSE  %s\n' "$1" >&2; exit 1; }
ok()   { printf 'ok      %s\n' "$1"; }

check_binary() {
  command -v "$1" >/dev/null 2>&1 || fail "$1 is not on PATH -- the lever cannot run, so measuring it would compare the control arm with itself"
  ok "$1 resolves to $(command -v "$1")"
}

check_index_fresh() {
  local db="$repo_root/.codegraph/codegraph.db"
  [[ -f "$db" ]] || fail "no codegraph index at $db"
  local db_epoch head_epoch
  db_epoch=$(stat -f %m "$db")
  head_epoch=$(cd "$repo_root" && git log -1 --format=%ct)
  if (( db_epoch < head_epoch )); then
    local changed
    changed=$(cd "$repo_root" && git log --since="@$db_epoch" --name-only --pretty=format: | sort -u | grep -c . || echo 0)
    fail "index is stale: built $(date -r "$db_epoch" '+%Y-%m-%d'), repo HEAD is $(date -r "$head_epoch" '+%Y-%m-%d'), $changed files changed since. A stale graph answers confidently from a codebase that no longer exists."
  fi
  ok "index is newer than HEAD"
}

check_mcp_responds() {
  local name="$1"
  command -v "$name" >/dev/null 2>&1 || fail "$name not on PATH, so its MCP server cannot start"
  timeout 20 "$name" --version >/dev/null 2>&1 \
    || fail "$name is on PATH but does not respond to --version; a registered-but-dead MCP server is the silent-degradation case this gate exists for"
  ok "$name responds"
}

check_model_reachable() {
  local model="$1"
  timeout 120 claude -p "Reply with the single word: ok" --model "$model" --output-format json >/dev/null 2>&1 \
    || fail "model $model did not answer a trivial prompt"
  ok "model $model reachable"
}

check_fixture_pair() {
  local dir="$repo_root"
  ok "fixture-pair lever: arms are prompt/context variants, no external machinery required"
}

printf '== preflight: %s (repo %s)\n' "$lever" "$repo_root"

case "$lever" in
  codegraph)
    # Retired 2026-08-23, never measured. Refuse by name rather than letting
    # check_binary report a missing tool, so the reason reaching the operator
    # is the decision and not the symptom.
    fail "codegraph is RETIRED, not merely missing -- see levers.yaml and RESULTS.md. Use the ast_grep lever. Re-adopting it means a pinned node@20, a moved npm prefix, and a per-repo index to keep fresh; do that deliberately, not by re-running this."
    ;;
  ast_grep)
    check_binary ast-grep
    # No index check: the whole point of this lever is that there is nothing to
    # keep fresh. If a staleness gate is ever needed here, the lever is wrong.
    ;;
  repo_priming|subagent_hygiene)
    check_fixture_pair
    ;;
  model_tier)
    check_model_reachable "${MODEL:-claude-sonnet-5}"
    ;;
  model_tier_haiku)
    check_model_reachable "${MODEL:-claude-haiku-4-5-20251001}"
    ;;
  prompt_cache)
    ok "observational lever: no arm to switch, cache_read ratio is read from usage"
    ;;
  *)
    fail "unknown lever: $lever"
    ;;
esac

printf 'PASS    %s can be measured honestly\n' "$lever"
