#!/usr/bin/env bash
set -euo pipefail
trap 'echo "Error occurred at line $LINENO"' ERR

PLIST_DST="$HOME/Library/LaunchAgents/com.justlikeme.hindsight-api.plist"

launchctl stop com.justlikeme.hindsight-api || true
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.justlikeme.hindsight-api.plist
rm -f "$PLIST_DST"
echo "removed"
