---
name: hunt-csrf
description: CSRF — token absence, SameSite quirks, JSON-CT bypass, Flash/CORS abuse, login CSRF.
keywords: [csrf, xsrf, samesite, cross-site request forgery, token, double submit, login csrf]
---

# hunt-csrf

## Triggers

"csrf", "xsrf", "samesite", "anti-csrf token", "double submit cookie".

## Pre-flight: cookie posture

Inspect target's session cookie:

- `SameSite=Lax` (default in modern browsers): CSRF still possible on
  GET state-changing endpoints
- `SameSite=Strict`: cross-site cookies blocked; CSRF mostly off-table
- `SameSite=None; Secure`: cookie cross-site → CSRF wide open
- No attribute at all (Chrome treats as Lax): same as Lax

## Phase 1 — token presence + binding

For every state-changing endpoint:

1. Capture a successful request, identify the CSRF token (header
   `X-CSRF-Token`, form field, JSON property)
2. Replay request **omitting** the token → expect 403; if 200 → CSRF
3. Replay with **another user's** token → expect 403; if 200 → token
   not session-bound
4. Replay with **empty** token (`X-CSRF-Token: `) → expect 403; if
   200 → empty-token bypass
5. Replay with **token from a different action** → tests scoping

## Phase 2 — SameSite=Lax bypass via GET state change

If app accepts state-changing actions on GET (`/transfer?to=...`) and
cookie is Lax, CSRF works via top-level navigation:

```html
<a href="https://app.example.com/transfer?to=attacker&amount=1000">Click me</a>
```

Lax allows cookies on top-level navigations regardless of method.

## Phase 3 — JSON CT bypass

`Content-Type: application/json` triggers CORS preflight — usually
blocks simple CSRF. But:

- If server accepts `text/plain`: send JSON body with `text/plain`
  CT — no preflight
- If server accepts `application/x-www-form-urlencoded` with a JSON-
  looking body (`{"x":1}=garbage`) — no preflight, body parsed as JSON

## Phase 4 — login CSRF

Force victim to log in as **attacker**:

```html
<form action="https://app.example.com/login" method="POST">
  <input name="email" value="attacker@evil.com">
  <input name="password" value="attackerpass">
</form>
<script>document.forms[0].submit()</script>
```

After submission, victim's browser is logged in as attacker —
anything victim does (save credit card, write notes) is recorded
in attacker's account. Reportable when chained with a "view login
history" or "save-to-account" flow.

## Phase 5 — Flash CSRF (vintage but check)

If a `crossdomain.xml` at the target permits `*`, legacy Flash
players can issue authenticated cross-origin requests. Unlikely
in 2026 but check static asset hosts.

## Phase 6 — CORS-misconfig amplified CSRF

See `hunt-cors`. When `Access-Control-Allow-Origin: <reflected>` +
`Allow-Credentials: true`, attacker's JS can make authenticated
fetches and read the response — strictly stronger than CSRF.

## Disclosed-report patterns

| Source | Pattern |
|---|---|
| H1 #117461 | Empty-token bypass |
| H1 #131202 (Uber) | Cookie-bomb forcing login CSRF |
| H1 #321820 | JSON CT switched to text/plain |
| H1 #1100210 | SameSite=Lax bypass via GET state-change |

## Never-submit fallbacks

- Logout CSRF → KILL (universal never-submit)
- CSRF on read-only endpoint → KILL
- CSRF on action that has no side effect (e.g., "mark notification
  read") → KILL/DOWNGRADE depending on program

## See also

- `hunt-cors`
- `hunt-xss` — XSS bypasses CSRF entirely (read tokens)
- `hunt-oauth` — `state` parameter == OAuth CSRF
