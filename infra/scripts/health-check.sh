#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker-compose.yml}"
PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
COMPOSE="docker compose -f ${PROJECT_DIR}/${COMPOSE_FILE}"

PASS=0
FAIL=0

check_service() {
  local name="$1"
  local status
  status=$($COMPOSE ps --format json 2>/dev/null | python3 -c "
import sys, json
for line in sys.stdin:
    obj = json.loads(line)
    if obj.get('Service') == '${name}' or obj.get('Name','').endswith('-${name}-1'):
        print(obj.get('Health','') or obj.get('Status',''))
        sys.exit(0)
print('not found')
" 2>/dev/null || echo "error")

  if echo "$status" | grep -qi "healthy\|running"; then
    echo "[PASS] ${name}: ${status}"
    PASS=$((PASS + 1))
  else
    echo "[FAIL] ${name}: ${status}"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== Synkra Health Check ==="
echo ""

for svc in frontend backend postgres redis nginx prometheus grafana; do
  check_service "$svc"
done

echo ""
echo "=== Results: ${PASS} passed, ${FAIL} failed ==="

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
