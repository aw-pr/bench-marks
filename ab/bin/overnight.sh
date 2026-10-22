#!/usr/bin/env bash
# overnight.sh — drain the Codex 5-hour window on the queued levers, overnight,
# without touching paid credits or the Anthropic reserve.
#
# Rules, in the order they are checked before every cell:
#   1. Only inside the window (default 23:00-06:00 local).
#   2. Credit tripwire: if the Codex credit balance has fallen since the night
#      began, stop. Above 100% of the 5-hour window Codex bills credits without
#      any warning, so a falling balance is the only reliable signal.
#   3. Weekly Codex window at or above OVERNIGHT_WEEKLY_STOP: stop.
#   4. 5-hour window at or above OVERNIGHT_PAUSE_AT: sleep until it resets,
#      then carry on. Below 100 because one cell can cost several percent.
#   5. A non-Codex lever runs only while Anthropic seven-day utilisation is
#      under OVERNIGHT_ANTHROPIC_CEILING, keeping the rest in reserve.
#
# Resumable: each lever's randomised plan is written once to
# runs/<lever>.plan and consumed a line at a time, so a night cut short at
# 06:00 resumes where it stopped instead of re-running cells.
#
# Usage: overnight.sh [queue-file]     (default ab/overnight.queue)

set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$(cd "$here/.." && pwd)"
queue="${1:-$here/overnight.queue}"
start_hhmm="${OVERNIGHT_START:-2300}"
end_hhmm="${OVERNIGHT_END:-0600}"
pause_at="${OVERNIGHT_PAUSE_AT:-90}"
weekly_stop="${OVERNIGHT_WEEKLY_STOP:-95}"
anthropic_ceiling="${OVERNIGHT_ANTHROPIC_CEILING:-0.90}"
max_consecutive_errors=3

mkdir -p "$here/runs"
log="$here/runs/overnight-$(date +%Y-%m-%d).log"
exec >>"$log" 2>&1
say() { printf '%s  %s\n' "$(date '+%H:%M:%S')" "$*"; }

lock="$here/runs/.overnight.lock"
mkdir "$lock" 2>/dev/null || { say "another overnight run holds $lock; exiting"; exit 0; }
trap 'rmdir "$lock"' EXIT

hhmm() { date +%H%M; }
in_window() {
  local now; now=$(hhmm)
  if (( 10#$start_hhmm > 10#$end_hhmm )); then
    (( 10#$now >= 10#$start_hhmm || 10#$now < 10#$end_hhmm ))
  else
    (( 10#$now >= 10#$start_hhmm && 10#$now < 10#$end_hhmm ))
  fi
}
# Seconds from now until the next HHMM, so a sleep never overruns the window.
secs_until() {
  local at; at=$(date -j -f '%H%M%S' "${1}00" +%s)
  (( at <= $(date +%s) )) && at=$((at + 86400))
  echo $((at - $(date +%s)))
}
secs_to_close() { secs_until "$end_hhmm"; }

limits() { "$here/bin/codex-limits.sh" 2>/dev/null; }
field() { jq -r ".$1" <<<"$2"; }
ge() { awk -v a="$1" -v b="$2" 'BEGIN{exit !(a >= b)}'; }

# Claude reports utilisation in its stream; a trivial Haiku call is the
# cheapest way to read it. Only paid for when a non-Codex lever is queued.
anthropic_ok() {
  local u
  u="$(timeout 120 claude -p "ok" --model claude-haiku-4-5-20251001 --output-format stream-json --verbose < /dev/null 2>/dev/null \
      | jq -r 'select(.type=="rate_limit_event") | .rate_limit_info.unifiedWindows.seven_day.utilization // empty' | tail -1)"
  [[ -n "$u" ]] || { say "anthropic: could not read utilisation; treating as over the ceiling"; return 1; }
  say "anthropic seven-day utilisation $u (ceiling $anthropic_ceiling)"
  ! ge "$u" "$anthropic_ceiling"
}

# 0 = carry on, 1 = stop for the night.
governor() {
  while true; do
    in_window || { say "outside $start_hhmm-$end_hhmm; stopping"; return 1; }
    local l; l="$(limits)" || { say "no Codex rate-limit snapshot; stopping rather than run blind"; return 1; }
    local p w c r
    p=$(field primary_pct "$l"); w=$(field secondary_pct "$l"); c=$(field credits "$l"); r=$(field primary_resets_at "$l")
    if awk -v now="$c" -v base="$credits_baseline" 'BEGIN{exit !(now < base - 0.0001)}'; then
      say "CREDIT TRIPWIRE: balance $credits_baseline -> $c; stopping"; return 1
    fi
    ge "$w" "$weekly_stop" && { say "weekly Codex window at ${w}%; stopping"; return 1; }
    if ge "$p" "$pause_at"; then
      local wait=$(( r - $(date +%s) + 60 )) close; close=$(secs_to_close)
      (( wait >= close )) && { say "5h window at ${p}%, resets after the window closes; stopping"; return 1; }
      say "5h window at ${p}%; sleeping $((wait / 60)) min until reset"
      sleep "$wait"; continue
    fi
    return 0
  done
}

plan_for() {
  local lever="$1" repeats="$2" plan="$here/runs/$1.plan" t tl
  [[ -f "$plan" ]] && return 0
  local tasks=()
  for t in "$here"/tasks/*.yaml; do
    tl="$(yq -r '.levers // [] | join(" ")' "$t")"
    [[ -n "$tl" && " $tl " != *" $lever "* ]] && continue
    tasks+=("$t")
  done
  for t in "${tasks[@]}"; do
    for arm in control treatment; do
      for ((n = 1; n <= repeats; n++)); do printf '%s\t%s\t%s\n' "${t#"$here"/}" "$arm" "$n"; done
    done
  done | sort -R > "$plan"
  say "plan written: $lever, $(wc -l < "$plan" | tr -d ' ') cells"
}

run_lever() {
  local lever="$1" repeats="$2" plan="$here/runs/$1.plan" errors=0
  plan_for "$lever" "$repeats"
  [[ -s "$plan" ]] || { say "$lever: plan empty, done"; return 0; }
  if [[ "$lever" != codex_* ]]; then anthropic_ok || { say "$lever skipped: Anthropic reserve"; return 0; }; fi
  governor || return 1
  "$here/bin/preflight.sh" "$lever" || { say "$lever: preflight refused; skipping lever"; return 0; }
  while [[ -s "$plan" ]]; do
    governor || return 1
    local line t arm n
    line="$(head -1 "$plan")"; IFS=$'\t' read -r t arm n <<<"$line"
    "$here/bin/run-cell.sh" "$here/$t" "$lever" "$arm" "$n" < /dev/null
    sed -i '' 1d "$plan"
    local last; last="$(tail -1 "$here/runs/$lever.jsonl")"
    if [[ "$(jq -r '.credits_spent // 0 | . > 0.0001' <<<"$last")" == true ]]; then
      say "CREDIT TRIPWIRE: last cell spent $(jq -r .credits_spent <<<"$last") credits; stopping"; return 1
    fi
    if [[ "$(jq -r .is_error <<<"$last")" == true ]]; then
      errors=$((errors + 1))
      (( errors >= max_consecutive_errors )) && { say "$lever: $errors errors in a row; stopping"; return 1; }
    else errors=0; fi
  done
  say "$lever: plan complete"
}

run_job() {
  local name="$1" script="$2" done_file="$3"
  [[ -e "$repo_root/$done_file" ]] && return 0
  governor || return 1
  say "job $name: starting"
  ( cd "$repo_root" && "$repo_root/$script" < /dev/null ) || say "job $name: failed (exit $?)"
}

say "== overnight start, queue $queue"
# launchd fires a few minutes early; wait for the window rather than miss it,
# but never sit idle for longer than that.
if ! in_window; then
  lead=$(secs_until "$start_hhmm")
  (( lead <= 1800 )) || { say "window opens in $((lead / 60)) min; not waiting that long, exiting"; exit 0; }
  say "waiting $((lead / 60)) min for the window"; sleep "$lead"
fi
credits_baseline="$(field credits "$(limits)")"
say "credit baseline $credits_baseline; pause at ${pause_at}%, weekly stop ${weekly_stop}%"

while read -r kind a b c; do
  [[ -z "$kind" || "$kind" == \#* ]] && continue
  case "$kind" in
    job)   run_job "$a" "$b" "$c" || break ;;
    lever) run_lever "$a" "$b" || break ;;
    *)     say "unknown queue entry: $kind" ;;
  esac
done < "$queue"

say "== overnight end; Codex now $(limits)"
