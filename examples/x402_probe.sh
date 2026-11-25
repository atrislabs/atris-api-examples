#!/usr/bin/env bash
# Free probe: inspect live x402 v2 payment requirements on Atris with zero API keys.
set -euo pipefail

ENDPOINT="${1:-https://api.atris.ai/x402/team-1/chat/completions}"

echo "=== 1. Discovery manifest (GET /.well-known/x402) ==="
curl -sS https://api.atris.ai/.well-known/x402 | python3 -m json.tool | head -n 35

echo ""
echo "=== 2. Unpaid 402 challenge (POST ${ENDPOINT}) ==="
curl -sS -i -X POST "${ENDPOINT}" \
  -H "Content-Type: application/json" \
  -d '{}' | head -n 25
