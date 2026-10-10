#!/usr/bin/env bash
# install-overnight.sh — schedule bin/overnight.sh nightly via launchd.
#
# launchd rather than a Claude session or cron: it survives the terminal that
# started it (FN-002 lost an unattended agent to a parent shell's SIGHUP), it
# runs a missed slot on wake, and it spends no Anthropic tokens keeping itself
# alive. caffeinate holds the Mac awake while the run is live, on AC power.
#
# Usage: install-overnight.sh            install or refresh, fires daily 22:55
#        install-overnight.sh --remove   unload and delete the job

set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
label="com.bench-marks.overnight"
plist="$HOME/Library/LaunchAgents/$label.plist"

launchctl bootout "gui/$(id -u)/$label" 2>/dev/null || true
if [[ "${1:-}" == --remove ]]; then rm -f "$plist"; echo "removed $label"; exit 0; fi

# launchd starts with a bare PATH; the run needs codex, claude, yq, jq, timeout.
path="$(dirname "$(command -v codex)"):$(dirname "$(command -v yq)"):$(dirname "$(command -v timeout)"):/usr/bin:/bin:/usr/sbin:/sbin"

mkdir -p "$(dirname "$plist")" "$here/runs"
cat > "$plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$label</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/caffeinate</string><string>-is</string>
    <string>/bin/bash</string><string>$here/bin/overnight.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>22</integer><key>Minute</key><integer>55</integer></dict>
  <key>EnvironmentVariables</key>
  <dict><key>PATH</key><string>$path</string></dict>
  <key>StandardOutPath</key><string>$here/runs/launchd.log</string>
  <key>StandardErrorPath</key><string>$here/runs/launchd.log</string>
</dict>
</plist>
EOF
plutil -lint "$plist" >/dev/null
launchctl bootstrap "gui/$(id -u)" "$plist"
echo "installed $label: daily 22:55, log in $here/runs/overnight-<date>.log"
