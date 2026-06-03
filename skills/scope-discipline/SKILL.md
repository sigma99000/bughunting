---
name: scope-discipline
description: Hard-stop scope enforcement. Refuses to emit payloads for hosts not in scope.md.
keywords: [scope, in-scope, out-of-scope, asset, authorization, boundary]
---

# scope-discipline

## When this skill loads

Auto-loads at the start of **every** engagement-touching command:
`/surface /recon /intel /hunt /chain /validate /report /token-scan
/autopilot /web3-audit`.

## Hard rules

1. **Refuse to emit payloads** for any host that does not match an
   entry in the current engagement's `scope.md` `## In scope`
   section.
2. **Match strictly**:
   - `example.com` matches only `example.com`. Not `www.example.com`.
   - `*.example.com` matches any single subdomain. Not
     `example.com` itself.
   - `**.example.com` matches multi-level. Many programs do not
     allow this — only honor when explicitly stated.
   - Path scopes (`example.com/api/*`) require the path prefix to
     match.
3. **Refuse implicit expansion**:
   - A discovered subdomain that resolves to the same IP as an
     in-scope asset is **not** automatically in scope.
   - A CNAME target outside the scope domain is out of scope (the
     CNAME source may still be in scope).
4. **Out-of-scope explicit overrides in-scope wildcard**:
   - `*.example.com` in-scope + `corp.example.com` out-of-scope →
     `corp.example.com` is out.
5. **Third-party SaaS rule**:
   - Stripe, Zendesk, Salesforce, etc. hosted at a subdomain →
     out of scope unless program explicitly says otherwise. Report
     directly to the vendor.

## Boundary checks before emitting

Before any active payload, run:

```
host = extract_host(payload_url)
scope = load(engagement/scope.md)

if not scope.in_scope_match(host):
    return "REFUSED: <host> is not in scope per scope.md line <N>."

if scope.out_of_scope_match(host):
    return "REFUSED: <host> is explicitly out of scope per scope.md line <N>."
```

## When the operator overrides

If the operator types something like "I have separate authorization
for this", CBH still refuses unless the operator updates `scope.md`
to add the asset. The reasoning: the engagement folder is the
audit trail. Verbal-only authorization isn't auditable.

## Common mistakes to surface

| Mistake | Fix |
|---|---|
| Operator typos `app.exemple.com` (homoglyph or typo) | Warn — host doesn't resolve to a known-target IP range |
| Operator pastes a Burp request from a *different* engagement | Detect engagement folder mismatch; refuse |
| Wildcard subdomain via `*.example.com` taking over `cdn.example.com` (CDN provider) | Warn — CDN provider hosts may be third-party-owned |
| In-scope `api.example.com` but operator targets `api.example.com.attacker.com` (open redirect testbed) | Allow — `attacker.com` is operator-owned, not a target |

## Coverage with bug-bounty platforms

| Platform | Where to find scope |
|---|---|
| HackerOne | `https://hackerone.com/<program>/policy_scopes` (logged-in) |
| Bugcrowd | `https://bugcrowd.com/<program>/scope` |
| Intigriti | Program detail page → "Scope" tab |
| Immunefi | Program page → "Assets in scope" |
| YesWeHack | Program page → "Scope" |

`scope.md` should always quote the **date** the operator copied the
scope. Scopes drift; a 2-month-old scope is stale.

## Output format when refusing

```
REFUSED: hunt-xss payload would target adminapi.example.com.
   scope.md line 14 lists *.example.com but line 22 excludes adminapi.example.com.
   To proceed: confirm authorization and update scope.md, then re-run.
```

## See also

- `triage-validation` — Q3 cross-references this skill
- `redteam-mindset` — even in red-team mode, scope is hard
