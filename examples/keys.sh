#!/usr/bin/env bash
# See your keys, balance, and per-key usage.
# Needs: export ATRIS_API_KEY="atris_..."
set -euo pipefail

BASE="https://api.atris.ai"
AUTH="x-atris-api-key: $ATRIS_API_KEY"

echo "== Your keys =="
curl -s "$BASE/api/developer/keys" -H "$AUTH"
echo

echo "== Credit balance =="
curl -s "$BASE/api/credits/balance" -H "$AUTH"
echo

# Per-key usage: pass an agent id from the keys list above.
if [ $# -ge 1 ]; then
  echo "== Usage for $1 =="
  curl -s "$BASE/api/developer/keys/$1/usage" -H "$AUTH"
  echo
fi
