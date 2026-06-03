# GraphQL — Disclosed Pattern Survey

31 disclosed reports.

## Pattern frequency

| Pattern | Frequency |
|---|---|
| IDOR via `node(id:)` or top-level field | 28% |
| Alias batching → rate-limit bypass | 22% |
| Field-level authorization missing on nested fields | 17% |
| CSRF via GET query | 11% |
| Persisted-query auto-register bypass | 8% |
| Introspection enabled in production (info disc only) | 7% |
| Field-suggestion error leakage | 4% |
| Depth/complexity DoS (DoS-excluded in most programs) | 3% |

## Top reports

| H1 ID | Pattern |
|---|---|
| 1130828 | Blind SQLi via GraphQL where ID concatenated |
| 1093706 | Alias batching → brute-force 2FA |
| 962653 | CSRF via GET query bypass |
| 2052158 | Persisted query bypass via APQ auto-register |

## Common server-side missteps

- Auth at top-level resolver only; nested fields skip
- `node(id:...)` resolver returns any record type without per-type
  check
- Hasura: missing `x-hasura-role` header validation
- Apollo: `extensions.persistedQuery` auto-register without rate
  limit
- GraphiQL exposed at `/graphql` in production
- Error verbosity leaks DB column names / file paths

## See also

- `skills/hunt-graphql/SKILL.md`
- `skills/hunt-idor/SKILL.md`
- `skills/hunt-race/SKILL.md`
