---
name: hunt-race
description: Race-condition hunter — single-packet attacks, alias batching, double-spend, TOCTOU.
keywords: [race condition, toctou, race window, single packet, last byte sync, double spend, double request]
---

# hunt-race

## Triggers

"race", "race condition", "double-spend", "toctou", "single packet
attack".

## Pre-flight

Race conditions exploit **non-atomic** business logic. Look for
sequences like:

1. Check user balance ≥ X
2. Deduct X
3. Increment recipient

If two requests interleave between (1) and (2), both pass the check.

## Phase 1 — find candidate endpoints

- One-time coupons / referral bonuses
- Withdrawals, transfers, redemptions
- "Vote once" surveys
- "Send invite once" emails
- 2FA OTP "verify"
- Rate-limited password attempts (alias batching → unlimited)
- Account deletion vs in-flight purchase

## Phase 2 — single-packet attack (PortSwigger 2023)

Send ~20–30 requests over a single HTTP/2 connection with last-byte
synchronization. They arrive at the server nearly simultaneously,
defeating most TCP-level scheduling jitter.

Tool: Burp's "Repeater group" → "Send group in parallel (single-
packet attack)".

Manual h2load:

```bash
h2load -n 20 -c 1 -p https/2 \
  -H 'cookie: session=...' \
  -H 'content-type: application/json' \
  -d body.json https://target/api/redeem
```

## Phase 3 — last-byte sync (HTTP/1.1)

For HTTP/1.1 servers, send 20 partial requests (all but last byte),
then push the final byte across all sockets:

```python
# pseudocode — see PortSwigger turbo-intruder for full impl
sockets = [open_socket(target) for _ in range(20)]
for s in sockets:
    s.send(request_minus_last_byte)
# now all servers are blocked on byte 1
for s in sockets:
    s.send(last_byte)
```

`turbo-intruder` Burp extension does this for you (`requestEngine
= RequestEngine(...).queue(...)`).

## Phase 4 — alias-batching races on GraphQL

```graphql
mutation {
  a0: redeemCoupon(code: "ONE-TIME-CODE") { credit }
  a1: redeemCoupon(code: "ONE-TIME-CODE") { credit }
  ...
  a19: redeemCoupon(code: "ONE-TIME-CODE") { credit }
}
```

Single HTTP request, 20 in-process redemptions — server's DB writes
race. See `hunt-graphql`.

## Phase 5 — distinguish race from idempotency-bug

Send 20 sequential requests with 50ms between them.

- If 20 redemptions happen: it's an idempotency bug (no atomicity at all)
- If only 1 happens sequentially but multiple in parallel: it's a race

The first case isn't really a race — it's worse, and usually
reportable as IDOR / business logic.

## Phase 6 — TOCTOU file operations

For file upload + processing:

1. Server checks file extension OK (.png)
2. Server moves file to processing dir
3. Server processes

Swap file content between (2) and (3) using a slow upload + symlink.
Rare in modern stacks but check old Java / PHP apps.

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #1185600 (HackerOne) | Race in invite acceptance → multi-team-add |
| H1 #1098438 (Shopify) | Coupon redemption race |
| H1 #2050020 | 2FA OTP verify race → bypass |
| PortSwigger 2023 disclosures | Single-packet attack first published |

## Never-submit fallbacks

- Race in "user clicks button twice quickly" causing double email
  → DOWNGRADE
- Race with no monetary or data impact → KILL
- Theoretical race without a successful parallel demonstration →
  CHAIN REQUIRED

## See also

- `hunt-graphql` — alias batching primitive
- `hunt-auth` — 2FA bypass via race
- `docs/verification/phase2e` — race lab
