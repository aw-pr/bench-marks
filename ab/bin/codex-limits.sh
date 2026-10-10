#!/usr/bin/env bash
# codex-limits.sh — the latest Codex rate-limit snapshot, as one JSON object.
#
# Codex does not expose its quota on demand; it reports it inside each
# session's rollout under ~/.codex/sessions. Reading the newest rollout costs
# nothing, whereas asking Codex costs quota -- and above 100% of the 5-hour
# window it costs paid credits, silently.
#
# A window whose resets_at has passed is reported at 0%, since the snapshot was
# taken before the reset.
#
# Usage: codex-limits.sh [rollout.jsonl]
#   {"primary_pct":..,"primary_resets_at":..,"secondary_pct":..,
#    "secondary_resets_at":..,"credits":..,"source":".."}

set -uo pipefail
sessions="${CODEX_HOME:-$HOME/.codex}/sessions"

snapshot_from() {
  grep '"rate_limits"' "$1" 2>/dev/null | tail -1 | jq -c '.payload.rate_limits // empty' 2>/dev/null
}

src="${1:-}"; snap=""
if [[ -n "$src" ]]; then
  snap="$(snapshot_from "$src")"
else
  # Newest first; a rollout that died before its first turn carries no snapshot.
  while IFS= read -r f; do
    snap="$(snapshot_from "$f")"
    [[ -n "$snap" ]] && { src="$f"; break; }
  done < <(find "$sessions" -name 'rollout-*.jsonl' -mtime -8 -print0 2>/dev/null | xargs -0 ls -t 2>/dev/null)
fi
[[ -n "$snap" ]] || { echo "no Codex rate-limit snapshot found under $sessions" >&2; exit 1; }

jq -c --arg src "$(basename "$src")" --argjson now "$(date +%s)" '
  def eff(w): if (w.resets_at // 0) <= $now then 0 else (w.used_percent // 0) end;
  {primary_pct: eff(.primary), primary_resets_at: .primary.resets_at,
   secondary_pct: eff(.secondary), secondary_resets_at: .secondary.resets_at,
   credits: ((.credits.balance // "0") | tonumber), source: $src}' <<<"$snap"
