---
name: hunt-mass-assignment
description: Mass assignment / parameter binding bugs — extra fields, role escalation, hidden flags.
keywords: [mass assignment, parameter binding, over-posting, hidden fields, role escalation, rails accepts_nested_attributes, spring binding]
---

# hunt-mass-assignment

## Triggers

"mass assignment", "parameter binding", "over-posting", "Rails
attributes", "Spring DataBinder".

## Phase 1 — discover the model shape

Read frontend code / API docs. Note every field the API returns and
which it accepts on write. The gap between "returned" and "accepted"
is the mass-assignment surface.

Look in error-suggestion endpoints (GraphQL field-name suggestions,
404 JSON error fields).

## Phase 2 — try the extras

For each PUT/PATCH/POST, try adding fields:

```
role: admin
is_admin: true
isAdmin: true
isSuperUser: true
permissions: ["*"]
verified_email: true
emailVerified: true
mfa_required: false
billing_tier: "enterprise"
credits: 100000
internal_note: "added by attacker"
parent_id: "<victim-org>"
user_id: "<victim>"
created_by: "<victim>"
```

If the API silently accepts these without 400 errors, mass
assignment is in play.

## Phase 3 — confirm impact

Re-fetch the object. Did the field actually change?

If yes:
- Did `role: admin` upgrade you? Try an admin-only endpoint
- Did `user_id` swap let you "become" victim? IDOR-adjacent

## Phase 4 — framework-specific

| Framework | Defense (and bypass) |
|---|---|
| Rails | `strong_parameters` allowlist; bypass by accepting via `accepts_nested_attributes_for` |
| Spring | `@RequestBody` defaults bind everything; check for `@JsonIgnore` on sensitive fields; `setAllowedFields` may filter incorrectly |
| Django REST | Serializer `fields = '__all__'` is the danger; check for ViewSet model exposure |
| Laravel | `$fillable` allowlist vs `$guarded` denylist — denylist is risky |
| Express + Mongoose | Schema strict mode — `strict: false` allows arbitrary keys |
| .NET | `[Bind(Include = "...")]` allowlist; older code uses `UpdateModel(obj)` blindly |

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| GitHub 2012 — Egor Homakov's Rails | Defining mass-assignment disclosure |
| H1 #1373167 | `role:admin` accepted on PATCH /users/me |
| H1 #404797 (Mail.ru) | `user_id` swap in profile update |
| Multiple Shopify | Sub-store role escalation via product API |

## Never-submit fallbacks

- Extra field accepted but never read → KILL
- Self-only escalation (raising your own credits but no transfer) → DOWNGRADE

## See also

- `hunt-idor` — sibling concept
- `hunt-auth` — role escalation chain
