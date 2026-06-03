# IDOR — Disclosed Pattern Survey

Patterns from 78 disclosed reports — the largest single class in
the corpus.

## ID class breakdown

| ID type | Frequency |
|---|---|
| Sequential numeric | 38% |
| UUIDv4 (leaked elsewhere) | 31% |
| Base64-encoded relay node | 12% |
| Short share-link tokens (brute-forceable) | 9% |
| Tenant-scoped IDs accidentally global | 6% |
| Other | 4% |

## Method breakdown

| Method | Frequency |
|---|---|
| GET (read) | 47% |
| PUT/PATCH (modify) | 28% |
| DELETE | 18% |
| POST (cross-tenant create) | 7% |

## Top H1 patterns

| H1 ID | Pattern |
|---|---|
| 285380 | Numeric report ID enum → view any H1 report |
| 404797 | Cookie `user_id` trusted server-side (Mail.ru) |
| 1389470 | UUIDs leaked in OG-image URLs; share URL revealed PII |
| 1373167 | DELETE /api/teams/{any-team-id} cross-org wipe |
| 1098438 | Race condition + IDOR on coupon redemption |
| 209223-adjacent | Sequential post ID + no auth (archived posts) |
| 738109 | GraphQL Relay node IDOR (decode base64) |
| 826358 | JWT-claim trusted as userId without re-auth |

## Modern variants

- **GraphQL `node(id:...)` resolver** — single resolver receives
  base64-encoded `Type:Id` and skips type-specific auth checks.
  Disclosed in multiple Apollo-based apps.
- **WebSocket message ID** — REST endpoint protected, but WS path
  that performs the same action accepts foreign IDs.
- **GraphQL field-level IDOR** — top-level query authed; nested
  field (`user(id).admin_notes`) unauthed.
- **API method override** — `X-HTTP-Method-Override: DELETE` on a
  POST bypasses route-level method-protection.

## Bypass-of-bypass patterns

When the app does *check* authorization:

- Per-row check by `WHERE owner_id = ?` works on read but breaks
  on `JOIN` queries
- `current_user.organizations.include?(target_org)` works for
  membership but not for nested objects
- Soft-delete records (where `deleted_at IS NULL` filter is missed
  in some queries) → IDOR on deleted rows
- Indirect ID: API accepts `{shareKey: "..."}` instead of `id`,
  share keys are bruteforceable

## Common report quality issues

(These are why IDOR triage often gets rejected.)

- Reporter used only one account (own account on both sides) → KILL,
  not a real IDOR. Always have two accounts.
- Reporter didn't show the **expected** denial — submit a `403`
  baseline showing the legitimate cross-user request is blocked,
  then show your bypass.
- Reporter showed IDOR with admin privileges → DOWNGRADE (admin
  can already read everything).

## See also

- `skills/hunt-idor/SKILL.md`
- `skills/hunt-graphql/SKILL.md`
- `skills/hunt-mass-assignment/SKILL.md`
- `skills/hunt-auth/SKILL.md`
