// Chat with the Atris API using the OpenAI Node SDK.
// The endpoint is OpenAI-compatible, so the standard SDK works.
// Needs: npm install openai, and ATRIS_API_KEY in your environment.

import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "https://api.atris.ai/v1",
  apiKey: process.env.ATRIS_API_KEY,
});

const reply = await client.chat.completions.create({
  model: "atris:auto",
  messages: [{ role: "user", content: "Say hello in five words." }],
});

console.log(reply.choices[0].message.content);

// Billing info rides along on every response.
if (reply.atris) {
  console.log("request_id:", reply.atris.request_id);
  console.log("credits charged:", reply.atris.credits_charged);
}
