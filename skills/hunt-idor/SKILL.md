---
name: hunt-idor
description: Insecure Direct Object Reference — sequential IDs, UUID exposure via search/list, GraphQL nodes, indirect refs.
keywords: [idor, broken access control, authorization, object reference, tenant isolation, multi-tenant]
---

# hunt-idor

## When this skill loads

Triggers: "idor", "object reference", "broken access", "tenant
isolation", "multi-tenant", "cross-user", "horizontal privilege".

## Pre-flight setup

You need **two accounts** in the target:

- Account A (your test account)
- Account B (a second test account; create it; never use a real
  victim's account)

For multi-tenant, set up two **orgs/workspaces** too.

## Phase 1 — find the IDs

In every authenticated response, harvest IDs:

- Numeric (`123`, `0a4f`)
- UUIDv4 (random; leakable via teammate listing, public profiles, share links)
- Base64 / nanoid / ULID
- GraphQL Relay node IDs (decode the base64 → reveals type + id)

For each ID class, check **predictability** (sequential vs random)
and **leak surface** (where else does it appear — emails, OG tags,
public sitemaps, S3 paths).

## Phase 2 — swap and verify

For every endpoint A can reach, swap A's ID for B's ID and verify:

```
GET /api/orders/{A's order id}    → A's data
GET /api/orders/{B's order id}    → expect 403/404
                                    if 200 → IDOR
```

Methods to vary (servers often guard GET but not other verbs):

- GET → swap and read
- POST → cross-tenant create
- PUT/PATCH → cross-tenant modify
- DELETE → cross-tenant delete (highest impact)

Locations of the ID:

- URL path: `/api/orders/123`
- Query: `?orderId=123`
- Body: `{"orderId":"123"}`
- Header: `X-Tenant-ID: 123`
- Cookie: `tenant=123`
- JWT claim (modifiable if JWT signature bypass exists)
- WebSocket message payload

## Phase 3 — masking via secondary ID

Some apps hide the primary ID and use a "share key":

```
/share/abc-randomish-key  →  fetches by share key, not user check
```

Probes:

- Brute-force the share key (entropy check first)
- Find leak surface (Slack share, email forward, browser history,
  Referer to third-party)
- Truncation: send shorter key — does the server allow partial match?

## Phase 4 — GraphQL Relay node IDs

```
base64decode("VXNlcjoxMjM=") = "User:123"
```

Modify the integer, re-encode, re-send via `node(id:"...")`. Many
servers skip auth on the generic `node` resolver.

## Phase 5 — indirect references

```
PUT /api/profile
{ "userId": "victim-uuid", "email": "newemail@attacker.com" }
```

The endpoint trusts the body's `userId` instead of the session. Common
in admin-impersonation endpoints accidentally exposed.

## Phase 6 — mass-assignment overlap

Often co-occurs with IDOR:

```
PATCH /api/users/me
{ "id": "victim", "role": "admin", "email": "x@y.com" }
```

If the ORM blindly applies the body, attacker swaps the row.

See `hunt-mass-assignment`.

## Phase 7 — method override / HTTP smuggling-lite

When `DELETE /api/users/B` is blocked at the proxy:

- `X-HTTP-Method-Override: DELETE` on a POST
- `_method=DELETE` form parameter (Rails, Laravel)
- HEAD instead of GET to bypass logging

## Phase 8 — admin function exposure

Endpoints like `/api/admin/users/B/reset-password` may be:

- Allowed for any authenticated user (no role check)
- Allowed only with `X-Admin-User: 1` header (header trusted from client)
- Allowed when called via the public API key

Bug bounty triagers care about **demonstrated cross-user impact**.
Always provide the second-account POC, not a hypothetical.

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #285380 (HackerOne) | Increment numeric report ID to view any report |
| H1 #404797 (Mail.ru) | Cookie `user_id` trusted server-side |
| H1 #1389470 (Slack-like) | UUIDs leaked in OG-image URLs; pasted in chat = view |
| H1 #1373167 | DELETE on /api/teams/{any-team-id} cross-org wipe |
| Optus 2022 breach | Sequential `contactid` in public API; no auth at all |
| Parler 2021 dump | Sequential post IDs + no auth on archived posts |

## Never-submit fallbacks

- "Theoretical IDOR" — only proved by guessing IDs you don't have
  → KILL until you have an actual cross-account demo.
- IDOR where the second "account" is a guest you control on both
  sides with no separation of trust → KILL (self-only).
- IDOR returning empty data fields → DOWNGRADE (info-only, no PII).

## See also

- `hunt-mass-assignment`
- `hunt-graphql` — IDOR via Relay nodes
- `hunt-auth` — flaws upstream of IDOR
- `triage-validation` — Q1 + Q4 are the IDOR gatekeepers
