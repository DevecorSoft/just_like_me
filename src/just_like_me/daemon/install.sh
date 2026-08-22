#!/usr/bin/env bash
set -euo pipefail
trap 'echo "Error occurred at line $LINENO"' ERR

PLIST_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/com.justlikeme.hindsight-api.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.justlikeme.hindsight-api.plist"
LABEL="com.justlikeme.hindsight-api"
DOMAIN="gui/$(id -u)"

if lsof -nP -iTCP:8888 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port 8888 is already in use. Stop the existing process first." >&2
  lsof -nP -iTCP:8888 -sTCP:LISTEN
  exit 1
fi

cp -f "$PLIST_SRC" "$PLIST_DST"

if launchctl print "$DOMAIN/$LABEL" >/dev/null 2>&1; then
  launchctl bootout "$DOMAIN" "$PLIST_DST" || true
fi

launchctl bootstrap "$DOMAIN" "$PLIST_DST"
launchctl kickstart -k "$DOMAIN/$LABEL"

echo "Installed to $PLIST_DST"
