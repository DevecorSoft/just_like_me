#!/usr/bin/env bash
set -e

REMOTE="${1:?Usage: $0 <user@host> [container_name]}"
CONTAINER="${2:-${PG_CONTAINER:-hindsight-postgres}}"
DUMP="/tmp/hindsight.dump"

docker exec -i "$CONTAINER" pg_dump -U postgres -d hindsight -Fc > "$DUMP"

rsync -azq "$DUMP" "$REMOTE:$DUMP"

ssh "$REMOTE" "docker exec -i '$CONTAINER' pg_restore -U postgres -d hindsight --clean --if-exists < '$DUMP' && rm -f '$DUMP'"

rm -f "$DUMP"
echo "Sync completed."
