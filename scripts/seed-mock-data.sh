#!/usr/bin/env bash
# Warm the API with a mock metrics collection + recommendation refresh (no DB required).
set -euo pipefail

API="${KUBEWISE_API:-http://localhost:8000/api/v1}"
SCENARIO="${KUBEWISE_SCENARIO:-wasteful}"

echo "==> POST ${API}/metrics/collect?scenario=${SCENARIO}"
curl -sf -X POST "${API}/metrics/collect?scenario=${SCENARIO}" || {
  echo "Failed. Is the backend running on port 8000?"
  exit 1
}
echo ""

echo "==> POST ${API}/recommendations/refresh?scenario=${SCENARIO}"
curl -sf -X POST "${API}/recommendations/refresh?scenario=${SCENARIO}" || exit 1
echo ""

echo "==> Done. Open http://localhost:3000 (frontend) if running."
