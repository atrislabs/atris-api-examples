#!/usr/bin/env bash
# One chat request against the Atris API with curl.
# Needs: export ATRIS_API_KEY="atris_..."
set -euo pipefail

curl -s https://api.atris.ai/v1/chat/completions \
  -H "x-atris-api-key: $ATRIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "atris:auto",
    "messages": [{"role": "user", "content": "Say hello in five words."}]
  }'
