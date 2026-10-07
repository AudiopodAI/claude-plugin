---
name: audiopod-account
description: Use when the user asks about their AudioPod account - how many credits they have left, their balance, what plan they are on, when it renews, "how much can I still do?", or whether they are running out of credits - or when an AudioPod tool was refused for insufficient credits. Calls get_account; never guesses a balance or quotes prices.
---

# AudioPod account, plan, and credits

`get_account` on the `audiopod` MCP server reads the connected AudioPod
account. It is free, changes nothing, and takes no arguments.

## When to call it

- "How many credits do I have left?", "what's my balance?"
- "What plan am I on?", "when does my plan renew?"
- "How much can I still do?", "am I running out of credits?"
- Right after any AudioPod tool was refused because the account does not have
  enough credits, so the user sees where they stand.

Call it every time the user asks. Never answer from memory or from an earlier
call: the balance changes with every job.

## What it returns

| Field | Meaning |
|---|---|
| `plan` | The account's plan name, for example Basic or Creator |
| `subscribed` | `true` on a paid plan |
| `credits.available` | Total credits the account can spend right now |
| `credits.monthly` | Credits from the plan's monthly allowance (reset each cycle) |
| `credits.payg` | Pay-as-you-go credits (they do not expire) |
| `renews_at` | When a paid plan next renews (only present when it will) |
| `ends_at` | When a paid plan that will not renew ends (only present then) |
| `billing_url` | The account's billing and credits page |
| `pricing_url` | AudioPod's plans page |

## How to answer

1. Call `get_account`.
2. State the plan and `credits.available`, with the monthly and pay-as-you-go
   split when both are non-zero. Give the renewal or end date if present.
3. Link `billing_url` for adding credits or managing the plan, and
   `pricing_url` for comparing plans. Quote both links exactly as returned.
4. If the balance is low or zero, say so plainly and point to those links.

## Rules

- Quote only the numbers `get_account` returned for this account. Never guess,
  estimate, or round them into something else.
- **Never state prices, per-job costs, or how many credits a job will use.**
  AudioPod's prices and plan allowances live at the pricing link; send the user
  there instead.
- Do not promise a job will fit in the remaining balance. Start the job; if it
  is refused for credits, call `get_account` and share the links.
- The account is whichever AudioPod account the user connected. If the numbers
  look wrong to them, they may have connected a different account; they can
  reconnect AudioPod from the app's connector or MCP settings.
- A "missing required scope" error means the connection lacks `audio:read`.
  The user can reconnect AudioPod to grant it.

## Help

Docs: https://docs.audiopod.ai. Support: https://audiopod.ai/support.
