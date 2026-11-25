// Call any Atris x402 v2 endpoint using Base Mainnet USDC with zero API keys.
//
// Install:
//   npm install viem
//
// Run (set BASE_PRIVATE_KEY to a Base wallet holding USDC, or pass --probe):
//   node examples/x402_pay.mjs --probe
//   BASE_PRIVATE_KEY=0x... node examples/x402_pay.mjs

import crypto from "node:crypto";

const url = process.env.ATRIS_X402_URL || "https://api.atris.ai/x402/team-1/chat/completions";
const body = {
  model: "team-1",
  messages: [{ role: "user", content: "Explain EIP-3009 in one sentence." }],
};
const probeOnly = process.argv.includes("--probe");

// Step 1: Fetch HTTP 402 payment requirements.
const first = await fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

if (first.status !== 402) {
  console.error(`Expected 402, got ${first.status}:`, await first.text());
  process.exit(1);
}

const rawHeader = first.headers.get("payment-required");
const challenge = rawHeader
  ? JSON.parse(Buffer.from(rawHeader, "base64").toString("utf8"))
  : await first.json();
const req = challenge.accepts[0];

if (probeOnly) {
  console.log(JSON.stringify({ url, price_usd: (Number(req.amount) / 1e6).toFixed(2), requirement: req }, null, 2));
  process.exit(0);
}

const pk = (process.env.BASE_PRIVATE_KEY || "").trim();
if (!pk) {
  console.error("Set BASE_PRIVATE_KEY or run with --probe.");
  process.exit(2);
}

const { privateKeyToAccount } = await import("viem/accounts");
const account = privateKeyToAccount(pk);
const chainId = Number(String(req.network).split(":").pop());
const now = Math.floor(Date.now() / 1000);
const validAfter = BigInt(Math.max(0, now - 60));
const validBefore = BigInt(now + Number(req.maxTimeoutSeconds || 120));
const nonce = `0x${crypto.randomBytes(32).toString("hex")}`;

const signature = await account.signTypedData({
  domain: {
    name: req.extra?.name || "USD Coin",
    version: req.extra?.version || "2",
    chainId,
    verifyingContract: req.asset,
  },
  types: {
    TransferWithAuthorization: [
      { name: "from", type: "address" },
      { name: "to", type: "address" },
      { name: "value", type: "uint256" },
      { name: "validAfter", type: "uint256" },
      { name: "validBefore", type: "uint256" },
      { name: "nonce", type: "bytes32" },
    ],
  },
  primaryType: "TransferWithAuthorization",
  message: {
    from: account.address,
    to: req.payTo,
    value: BigInt(req.amount),
    validAfter,
    validBefore,
    nonce,
  },
});

const paymentPayload = {
  x402Version: 2,
  accepted: req,
  payload: {
    signature,
    authorization: {
      from: account.address,
      to: req.payTo,
      value: String(req.amount),
      validAfter: String(validAfter),
      validBefore: String(validBefore),
      nonce,
    },
  },
};

// Step 2: Retry with PAYMENT-SIGNATURE header.
const paid = await fetch(url, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "PAYMENT-SIGNATURE": Buffer.from(JSON.stringify(paymentPayload)).toString("base64"),
  },
  body: JSON.stringify(body),
});

console.log(`HTTP ${paid.status}`);
const receipt = paid.headers.get("payment-response");
if (receipt) {
  console.log("Receipt:", Buffer.from(receipt, "base64").toString("utf8"));
}
console.log(JSON.stringify(await paid.json(), null, 2));
