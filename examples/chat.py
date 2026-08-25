"""Chat with the Atris API using the OpenAI Python SDK.

The endpoint is OpenAI-compatible, so the standard SDK works.
Needs: pip install openai, and ATRIS_API_KEY in your environment.
"""

import os

from openai import OpenAI

client = OpenAI(
    base_url="https://api.atris.ai/v1",
    api_key=os.environ["ATRIS_API_KEY"],
)

# Plain request
reply = client.chat.completions.create(
    model="atris:auto",
    messages=[{"role": "user", "content": "Say hello in five words."}],
)
print(reply.choices[0].message.content)

# The response carries billing info: request id, credits charged,
# dollar cost, and remaining balance. Keep the request id if you
# want to fetch the durable receipt later (see receipt.py).
atris = getattr(reply, "atris", None) or reply.model_extra.get("atris")
if atris:
    print(f"request_id: {atris['request_id']}")

# Streaming
stream = client.chat.completions.create(
    model="atris:auto",
    messages=[{"role": "user", "content": "Count to five."}],
    stream=True,
)
for chunk in stream:
    delta = chunk.choices[0].delta.content if chunk.choices else None
    if delta:
        print(delta, end="", flush=True)
print()
