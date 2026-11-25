# Atris API examples

Working examples for the Atris API. Every request is billed from actual model usage, and every request comes with a receipt you can fetch.

Base URL: `https://api.atris.ai`

Machine-readable guides (point your agent at these):
- Full API guide: `https://api.atris.ai/llms.txt`
- Zero-API-key x402 discovery (Base USDC): `https://api.atris.ai/.well-known/x402` | `https://api.atris.ai/x402/openapi.json` | `https://api.atris.ai/SKILL.md`
- Live x402scan directory: [x402scan.com/server/94aa677d-d793-49c0-8537-a93254c1d552](https://www.x402scan.com/server/94aa677d-d793-49c0-8537-a93254c1d552)

## Zero API keys: pay per request with x402 (Base USDC)

If your agent holds USDC on Base (`eip155:8453`), skip signup and call Atris directly with no API key:

| Endpoint | Price (USDC) | What it does |
|---|---|---|
| `POST /x402/team-1/chat/completions` | `$0.03` | OpenAI-compatible `team-1` (fast open model + stronger reviewer check) |
| `POST /x402/agents/agent-1` | `$0.03` | Call published Atris `agent-1` via OpenAI chat completions |
| `POST /x402/aeo/check` | `$0.75` | AI Engine Optimization audit across ChatGPT & Perplexity |
| `POST /x402/design/extract` | `$0.25` | Extract full brand & CSS design tokens from any public URL |
| `POST /x402/design/search` | `$0.05` | Search extracted brand design systems by visual style |
| `POST /x402/documents/parse` | `$0.25` | Verified PDF/image to Markdown parser (up to 5 pages) |
| `POST /x402/youtube/search` | `$0.05` | Verified YouTube video watch permalinks & titles |

Free dry-run probe (no wallet required):

```bash
python3 examples/x402_pay.py --probe
```

Live paid call:

```bash
export BASE_PRIVATE_KEY="0x..."
python3 examples/x402_pay.py --url https://api.atris.ai/x402/team-1/chat/completions
```

## Get a key

1. Sign in at [atris.ai](https://atris.ai).
2. Open Settings, then Developer.
3. Create a key. The full secret is shown once, so copy it then.

Set it in your shell:

```bash
export ATRIS_API_KEY="atris_..."
```

## Send your first message

The chat endpoint is OpenAI-compatible, so the OpenAI SDKs work as-is. Point them at our base URL:

```python
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.atris.ai/v1",
    api_key=os.environ["ATRIS_API_KEY"],
)

reply = client.chat.completions.create(
    model="atris:auto",
    messages=[{"role": "user", "content": "Hello"}],
)
print(reply.choices[0].message.content)
```

Or with plain curl:

```bash
curl https://api.atris.ai/v1/chat/completions \
  -H "x-atris-api-key: $ATRIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"atris:auto","messages":[{"role":"user","content":"Hello"}]}'
```

## What's in this repo

| File | Shows |
|------|-------|
| [`examples/chat.sh`](examples/chat.sh) | One chat request with curl |
| [`examples/chat.py`](examples/chat.py) | Chat with the OpenAI Python SDK, plus streaming |
| [`examples/chat.js`](examples/chat.js) | Chat with the OpenAI Node SDK |
| [`examples/receipt.py`](examples/receipt.py) | Fetch the billing receipt for a request |
| [`examples/keys.sh`](examples/keys.sh) | List keys, check balance, see per-key usage |
| [`examples/x402_probe.sh`](examples/x402_probe.sh) | Inspect live x402 v2 payment challenges with curl (free) |
| [`examples/x402_pay.py`](examples/x402_pay.py) | Call any Atris x402 endpoint in Python with Base USDC (zero API keys) |
| [`examples/x402_pay.mjs`](examples/x402_pay.mjs) | Call any Atris x402 endpoint in Node.js (`viem`) with Base USDC |

## Billing

One credit is $0.01. Requests bill from actual model usage at Atris rates, with a $0.01 minimum per request.

Every chat response includes an `atris` object with the request id, credits charged, dollar cost, and your remaining balance. Fetch the durable receipt any time:

```bash
curl https://api.atris.ai/api/atris2/billing/receipts/REQUEST_ID \
  -H "x-atris-api-key: $ATRIS_API_KEY"
```

## Managing keys

```bash
# List your keys
curl https://api.atris.ai/api/developer/keys -H "x-atris-api-key: $ATRIS_API_KEY"

# Per-key usage
curl https://api.atris.ai/api/developer/keys/AGENT_ID/usage -H "x-atris-api-key: $ATRIS_API_KEY"

# Rotate (new secret shown once, old key stops working)
curl -X POST https://api.atris.ai/api/developer/keys/AGENT_ID/rotate -H "x-atris-api-key: $ATRIS_API_KEY"

# Revoke
curl -X DELETE https://api.atris.ai/api/developer/keys/AGENT_ID -H "x-atris-api-key: $ATRIS_API_KEY"

# Balance
curl https://api.atris.ai/api/credits/balance -H "x-atris-api-key: $ATRIS_API_KEY"
```

## Auth reference

Two ways to authenticate:

- `x-atris-api-key: atris_...` with a developer key (use this for code and agents)
- `Authorization: Bearer <JWT>` with a signed-in session (this is what the dashboard uses)

Keys are created with a JWT via `POST /api/developer/create-key`. The secret is revealed once in that response.
