"""Call any Atris x402 v2 endpoint using Base Mainnet USDC with zero API keys.

Requirements:
    pip install eth-account requests

Dry-run probe (free, no wallet needed):
    python3 examples/x402_pay.py --probe

Live paid call ($0.03 USDC on Base Mainnet):
    export BASE_PRIVATE_KEY="0x..."
    python3 examples/x402_pay.py \
      --url https://api.atris.ai/x402/team-1/chat/completions \
      --body '{"model":"team-1","messages":[{"role":"user","content":"Explain EIP-3009 in one sentence."}]}'
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import secrets
import sys
import time
from typing import Any, Dict

import requests


def decode_b64_json(raw: str) -> Dict[str, Any]:
    padded = raw + "=" * (-len(raw) % 4)
    return json.loads(base64.b64decode(padded).decode("utf-8"))


def encode_b64_json(obj: Dict[str, Any]) -> str:
    raw = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


def sign_eip3009_payment(requirement: Dict[str, Any], private_key: str) -> Dict[str, Any]:
    """Sign an x402 v2 EIP-3009 transferWithAuthorization payload for Base USDC."""
    from eth_account import Account

    acct = Account.from_key(private_key)
    network = str(requirement["network"])
    chain_id = int(network.split(":")[-1])
    now = int(time.time())
    valid_after = max(0, now - 60)
    valid_before = now + int(requirement.get("maxTimeoutSeconds") or 120)
    nonce = "0x" + secrets.token_hex(32)
    extra = requirement.get("extra") or {}

    typed_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "TransferWithAuthorization": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "validAfter", "type": "uint256"},
                {"name": "validBefore", "type": "uint256"},
                {"name": "nonce", "type": "bytes32"},
            ],
        },
        "primaryType": "TransferWithAuthorization",
        "domain": {
            "name": extra.get("name", "USD Coin"),
            "version": extra.get("version", "2"),
            "chainId": chain_id,
            "verifyingContract": requirement["asset"],
        },
        "message": {
            "from": acct.address,
            "to": requirement["payTo"],
            "value": int(requirement["amount"]),
            "validAfter": valid_after,
            "validBefore": valid_before,
            "nonce": nonce,
        },
    }

    signed = Account.sign_typed_data(private_key, full_message=typed_data)
    sig_hex = signed.signature.hex()
    if not sig_hex.startswith("0x"):
        sig_hex = "0x" + sig_hex

    return {
        "x402Version": 2,
        "accepted": requirement,
        "payload": {
            "signature": sig_hex,
            "authorization": {
                "from": acct.address,
                "to": requirement["payTo"],
                "value": str(requirement["amount"]),
                "validAfter": str(valid_after),
                "validBefore": str(valid_before),
                "nonce": nonce,
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Call an Atris x402 v2 endpoint with Base USDC.")
    parser.add_argument(
        "--url",
        default="https://api.atris.ai/x402/team-1/chat/completions",
        help="Full Atris x402 endpoint URL",
    )
    parser.add_argument(
        "--body",
        default='{"model":"team-1","messages":[{"role":"user","content":"Explain EIP-3009 in one sentence."}]}',
        help="JSON request body",
    )
    parser.add_argument(
        "--probe",
        action="store_true",
        help="Only fetch and print the free 402 payment requirement without paying",
    )
    args = parser.parse_args()
    body = json.loads(args.body)

    # Step 1: Unpaid request returns HTTP 402 with PAYMENT-REQUIRED header.
    probe = requests.post(args.url, json=body, timeout=30)
    if probe.status_code != 402:
        print(f"Unexpected HTTP {probe.status_code}: {probe.text}", file=sys.stderr)
        return 1

    header = probe.headers.get("PAYMENT-REQUIRED")
    challenge = decode_b64_json(header) if header else probe.json()
    requirement = challenge["accepts"][0]
    price_usd = int(requirement["amount"]) / 1_000_000

    if args.probe:
        print(json.dumps({"url": args.url, "price_usd": f"{price_usd:.2f}", "requirement": requirement}, indent=2))
        return 0

    private_key = os.environ.get("BASE_PRIVATE_KEY", "").strip()
    if not private_key:
        print("Set BASE_PRIVATE_KEY (Base wallet with USDC) or pass --probe for a free dry run.", file=sys.stderr)
        return 2

    # Step 2: Sign EIP-3009 authorization and retry with PAYMENT-SIGNATURE.
    payment_payload = sign_eip3009_payment(requirement, private_key)
    paid = requests.post(
        args.url,
        json=body,
        headers={"PAYMENT-SIGNATURE": encode_b64_json(payment_payload)},
        timeout=180,
    )
    print(f"HTTP {paid.status_code}")
    receipt_hdr = paid.headers.get("PAYMENT-RESPONSE")
    if receipt_hdr:
        print("Receipt:", json.dumps(decode_b64_json(receipt_hdr), indent=2))
    print(json.dumps(paid.json(), indent=2))
    return 0 if paid.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
