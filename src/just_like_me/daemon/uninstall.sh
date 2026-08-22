#!/usr/bin/env bash
set -euo pipefail
trap 'echo "Error occurred at line $LINENO"' ERR

PLIST_DST="$HOME/Library/LaunchAgents/com.justlikeme.hindsight-api.plist"
DOMAIN="gui/$(id -u)"

launchctl stop com.justlikeme.hindsight-api || true
launchctl bootout "$DOMAIN" "$PLIST_DST" || true
rm -f "$PLIST_DST"
echo "removed"
