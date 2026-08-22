#!/usr/bin/env bash
set -euo pipefail
trap 'echo "Error occurred at line $LINENO"' ERR

PLIST_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/com.justlikeme.hindsight-api.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.justlikeme.hindsight-api.plist"

cp -f "$PLIST_SRC" "$PLIST_DST"

launchctl bootstrap gui/$(id -u) "$PLIST_DST"

echo "Installed to $PLIST_DST"
