"""Send one chat request, then fetch its durable billing receipt.

Every Atris API request gets a receipt you can fetch later by request id.
Needs: pip install requests, and ATRIS_API_KEY in your environment.
"""

import os

import requests

BASE = "https://api.atris.ai"
HEADERS = {"x-atris-api-key": os.environ["ATRIS_API_KEY"]}

# 1. Send a chat request
chat = requests.post(
    f"{BASE}/v1/chat/completions",
    headers=HEADERS,
    json={
        "model": "atris:auto",
        "messages": [{"role": "user", "content": "One fun fact, one sentence."}],
    },
)
chat.raise_for_status()
body = chat.json()

print(body["choices"][0]["message"]["content"])

atris = body["atris"]
request_id = atris["request_id"]
print(f"\ncharged {atris['credits_charged']} credits, request {request_id}")

# 2. Fetch the durable receipt for that exact request
receipt = requests.get(
    f"{BASE}/api/atris2/billing/receipts/{request_id}",
    headers=HEADERS,
)
receipt.raise_for_status()
print("\nreceipt:")
print(receipt.json())
